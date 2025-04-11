#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Processor
Handles interactions with LLM APIs (Claude, OpenAI, Gemini, and OpenAI-compatible)
"""

import os
import json
import time
import anthropic
import openai
import base64
import io
import requests
from urllib.parse import urlparse
from datetime import datetime

# Import Gemini library
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Import PyPDF2 conditionally for PDF processing
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("Warning: PyPDF2 not installed. PDF text extraction will be limited.")

# Import PIL for image handling with Gemini
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow (PIL) not installed. Image processing for Gemini will be limited.")


class LLMProcessor:
    """Processes interactions with LLM APIs"""
    
    def __init__(self, config_manager):
        """Initialize LLM processor with configuration"""
        self.config_manager = config_manager
        self.api_settings = config_manager.get_api_settings()
        self.output_dir = config_manager.get_output_dir()
        
        # Default rate limit delay
        self.rate_limit_delay = 10
        
        # Initialize clients based on API type
        self.client = None # Initialize client attribute
        self._initialize_clients()
        
        # Output file paths
        self.prompts_dir = os.path.join(self.output_dir, 'prompts')
        self.messages_dir = os.path.join(self.output_dir, 'messages')
        self.outputs_dir = os.path.join(self.output_dir, 'outputs')
        self.files_dir = os.path.join(self.output_dir, 'files')
        self.merged_output_file = os.path.join(self.output_dir, 'merged_output.txt')
        
    def _initialize_clients(self):
        """Initialize API clients based on settings"""
        api_type = self.api_settings.get('type', 'claude')
        api_key = self.api_settings.get('api_key', '')
        api_base = self.api_settings.get('api_base', None) # Get base URL if set
        
        self.client = None # Reset client
        
        try:
            if api_type == 'claude':
                # Use default base URL if not provided
                claude_base = api_base or 'https://api.anthropic.com'
                self.client = anthropic.Anthropic(api_key=api_key, base_url=claude_base)
                self._test_claude_connection()
            elif api_type == 'openai':
                # Use default base URL if not provided
                openai_base = api_base or 'https://api.openai.com/v1'
                self.client = openai.OpenAI(api_key=api_key, base_url=openai_base)
            elif api_type == 'gemini':
                # Gemini uses configure, not a traditional client object in the same way
                # API Base is not directly used in configure, handled via library internals or proxies
                genai.configure(api_key=api_key)
                # We store the configured library module itself or a marker
                self.client = genai 
                self._test_gemini_connection()
            else:  # OpenAI-compatible
                # Require API base for compatible APIs, provide a default if missing
                compatible_base = api_base or 'https://api.deepseek.com/v1'
                self.client = openai.OpenAI(api_key=api_key, base_url=compatible_base)
        except Exception as e:
            print(f"Warning: Error initializing {api_type} client: {e}")
            self.client = None # Ensure client is None on error
    
    def _test_claude_connection(self):
        """Test Claude API connection"""
        try:
            if not hasattr(self.client, 'messages'):
                print("Warning: Anthropic client missing expected attributes")
                return False
            # A light check, maybe list models if available without cost?
            # For now, just check attribute existence.
            return True
        except Exception as e:
            print(f"Error testing Claude connection: {e}")
            return False

    def _test_gemini_connection(self):
        """Test Gemini API connection by listing models"""
        try:
            # Listing models is a lightweight way to check API key validity
            models = genai.list_models()
            # Check if any generative models are returned
            if any('generateContent' in m.supported_generation_methods for m in models):
                 print("Gemini connection successful.")
                 return True
            else:
                 print("Warning: No generative models found via Gemini API. Check API key and permissions.")
                 return False
        except Exception as e:
            print(f"Error testing Gemini connection: {e}")
            # Invalidate client state if connection fails
            self.client = None 
            return False

    def refresh_settings(self):
        """Refresh API settings"""
        self.api_settings = self.config_manager.get_api_settings()
        self._initialize_clients()
    
    def _get_reasoning_prompt(self):
        """Get appropriate reasoning prompt based on settings"""
        reasoning_enabled = self.api_settings.get('reasoning_enabled', True)
        if not reasoning_enabled:
            return ""
        
        reasoning_level = self.api_settings.get('reasoning_level', 'medium')
        reasoning_prompts = {
            'low': "Think step-by-step about this information.",
            'medium': "Think step-by-step carefully and provide detailed reasoning about this information.",
            'high': "Think step-by-step very carefully, showing your detailed reasoning process and evidence evaluation about this information."
        }
        return reasoning_prompts.get(reasoning_level, reasoning_prompts['medium'])
    
    def _encode_file(self, file_path):
        """Encode file contents as base64"""
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
            return base64.b64encode(file_content).decode('utf-8')
        except Exception as e:
            print(f"Error encoding file {file_path}: {e}")
            return None

    def _get_media_type(self, file_extension):
        """Get the media type for a file extension"""
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.pdf': 'application/pdf'
            # Add more as needed
        }
        return media_types.get(file_extension, 'application/octet-stream')

    def process_file(self, file_path):
        """Process a single file through the LLM"""
        try:
            # Refresh settings before processing each file to get latest config
            self.refresh_settings() 
            
            # Check if client is initialized
            if not self.client:
                 api_type = self.api_settings.get('type', 'unknown')
                 return {
                    'filename': os.path.basename(file_path),
                    'result': f"Error: API client for '{api_type}' not initialized. Check API key and settings.",
                    'error': True
                 }

            # Get prompts and message
            prompts = self.config_manager.get_prompts()
            message = self.config_manager.get_message()
            
            system_prompt = prompts.get('system_prompt', '')
            user_message = message.get('user_message', '')
            reasoning_prompt = self._get_reasoning_prompt()
            
            # Combine prompts for actual use
            # Note: Gemini uses system_instruction differently, handled in _call_gemini_api
            combined_system_prompt = f"{system_prompt}"
            if reasoning_prompt:
                combined_system_prompt += f" {reasoning_prompt}"
            
            # Save prompts and message used
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            
            prompt_file = os.path.join(self.prompts_dir, f"prompt_{filename}_{timestamp}.txt")
            message_file = os.path.join(self.messages_dir, f"message_{filename}_{timestamp}.txt")
            output_file = os.path.join(self.outputs_dir, f"output_{filename}_{timestamp}.txt")
            
            # Save combined system prompt (might differ slightly from what's sent to Gemini)
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(combined_system_prompt)
                
            with open(message_file, 'w', encoding='utf-8') as f:
                f.write(user_message)
            
            # Call appropriate API based on settings
            api_type = self.api_settings.get('type', 'claude')
            if api_type == 'claude':
                result = self._call_claude_api(combined_system_prompt, user_message, file_path)
            elif api_type == 'gemini':
                # Pass original system prompt and user message separately for Gemini
                result = self._call_gemini_api(system_prompt, user_message, file_path, reasoning_prompt)
            else:  # 'openai' or 'openai_compatible'
                result = self._call_openai_api(combined_system_prompt, user_message, file_path)
            
            # Save output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
                
            # Append to merged output
            self._append_to_merged_output(filename, result)
            
            return {
                'filename': filename,
                'result': result,
                'output_file': output_file
            }
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            # Log traceback for debugging
            import traceback
            traceback.print_exc()
            return {
                'filename': os.path.basename(file_path),
                'result': f"Error: {str(e)}",
                'error': True
            }

    def _call_claude_api_direct(self, system_prompt, user_message, filename, file_content=None, file_type=None):
        """Call Claude API using direct HTTP requests as a fallback"""
        # (Implementation remains the same as before)
        try:
            api_key = self.api_settings.get('api_key', '')
            api_base = self.api_settings.get('api_base', 'https://api.anthropic.com')
            model = self.api_settings.get('model', 'claude-3-7-sonnet-20250219')
            temperature = float(self.api_settings.get('temperature', 0.7))
            
            # Parse the base URL
            url_parts = urlparse(api_base)
            api_url = f"{url_parts.scheme}://{url_parts.netloc}/v1/messages"
            
            # Create minimal headers
            headers = {
                "Content-Type": "application/json",
                "X-Api-Key": api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Create the messages based on content type
            if file_content and file_type:
                if file_type == "image":
                    # Can't use direct request for images, fall back to text only
                    data = {
                        "model": model,
                        "temperature": temperature,
                        "max_tokens": 4000,
                        "system": system_prompt,
                        "messages": [
                            {
                                "role": "user",
                                "content": f"{user_message}\n\nFile: {filename} (Image couldn't be included)"
                            }
                        ]
                    }
                elif file_type == "pdf":
                    # Can't use direct request for PDFs, fall back to text only
                    data = {
                        "model": model,
                        "temperature": temperature,
                        "max_tokens": 4000,
                        "system": system_prompt,
                        "messages": [
                            {
                                "role": "user",
                                "content": f"{user_message}\n\nFile: {filename} (PDF couldn't be included)"
                            }
                        ]
                    }
                else:
                    # Text file
                    data = {
                        "model": model,
                        "temperature": temperature,
                        "max_tokens": 4000,
                        "system": system_prompt,
                        "messages": [
                            {
                                "role": "user",
                                "content": f"{user_message}\n\nFile: {filename}\n\nFile Contents:\n{file_content}"
                            }
                        ]
                    }
            else:
                # No file content, just use the message
                data = {
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": 4000,
                    "system": system_prompt,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{user_message}\n\nFile: {filename}"
                        }
                    ]
                }
            
            # Make the request with a fresh session
            session = requests.Session()
            response = session.post(
                api_url,
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = ""
                
                for content in result.get("content", []):
                    if content.get("type") == "text":
                        response_text += content.get("text", "")
                
                return response_text
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_detail = json.dumps(error_json["error"])
                except Exception:
                    pass
                
                return f"Error: API returned status {response.status_code}: {error_detail}"
                
        except Exception as e:
            return f"Error using direct API call: {str(e)}"

    def _call_claude_api(self, system_prompt, user_message, file_path):
        """Call the Claude API using the appropriate method for each file type"""
        # (Implementation remains the same as before)
        try:
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1].lower()
            
            # Check if client is available
            if not self.client or not isinstance(self.client, anthropic.Anthropic):
                print("Claude client not initialized correctly. Attempting fallback.")
                # Try to read file as text for direct API call
                if file_extension in ['.txt', '.md', '.csv', '.json', '.xml', '.html']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text_content = f.read()
                        return self._call_claude_api_direct(system_prompt, user_message, filename, text_content, "text")
                    except Exception:
                        return self._call_claude_api_direct(system_prompt, user_message, filename)
                else: # Images, PDFs, others handled by direct call
                     return self._call_claude_api_direct(system_prompt, user_message, filename, None, "image" if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] else "pdf" if file_extension == '.pdf' else None)

            file_content_base64 = self._encode_file(file_path)
            if not file_content_base64:
                return f"Error: Could not read file {filename}"

            # Get model and settings
            model = self.api_settings.get('model', 'claude-3-7-sonnet-20250219')
            temperature = float(self.api_settings.get('temperature', 0.7))
            
            # Different handling based on file type
            message_content = []
            is_multimodal = False

            if file_extension == '.pdf':
                message_content.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": file_content_base64
                    }
                })
                is_multimodal = True
            elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                media_type = self._get_media_type(file_extension)
                message_content.append({
                    "type": "image", 
                    "source": {
                        "type": "base64", 
                        "media_type": media_type, 
                        "data": file_content_base64
                    }
                })
                is_multimodal = True
            else:
                # For text-based files, try to include content
                text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html']
                if file_extension in text_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_text = f.read()
                        # Add file content to user message for text files
                        user_message = f"{user_message}\n\nFile: {filename}\n\nFile Contents:\n{file_text}"
                    except UnicodeDecodeError:
                        user_message = f"{user_message}\n\nFile: {filename}\n\n(File contents could not be included due to format compatibility.)"
                else:
                     user_message = f"{user_message}\n\nFile: {filename}\n\n(File contents could not be included due to format compatibility.)"

            # Add the main text part of the user message
            message_content.append({"type": "text", "text": user_message})

            try:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=4000,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": message_content}]
                )
            except Exception as specific_error:
                print(f"Claude API error: {specific_error}")
                print("Falling back to direct API call")
                # Determine fallback type based on original extension
                fallback_file_type = None
                fallback_file_content = None
                if file_extension == '.pdf':
                    fallback_file_type = "pdf"
                elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                     fallback_file_type = "image"
                elif file_extension in text_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            fallback_file_content = f.read()
                        fallback_file_type = "text"
                    except Exception:
                        pass # Fallback without content
                # Use the original user_message for fallback
                original_user_message = message.get('user_message', '') 
                return self._call_claude_api_direct(system_prompt, original_user_message, filename, fallback_file_content, fallback_file_type)

            # Extract response text
            response_text = ""
            for content in response.content:
                if content.type == "text":
                    response_text += content.text
            
            return response_text
            
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            print("Attempting fallback to direct API call")
            # Attempt a direct API call as a fallback
            try:
                # Determine fallback type based on original extension
                fallback_file_type = None
                fallback_file_content = None
                file_extension = os.path.splitext(file_path)[1].lower()
                text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html']
                if file_extension == '.pdf':
                    fallback_file_type = "pdf"
                elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                     fallback_file_type = "image"
                elif file_extension in text_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            fallback_file_content = f.read()
                        fallback_file_type = "text"
                    except Exception:
                        pass # Fallback without content
                # Use the original user_message for fallback
                original_user_message = self.config_manager.get_message().get('user_message', '')
                return self._call_claude_api_direct(system_prompt, original_user_message, os.path.basename(file_path), fallback_file_content, fallback_file_type)
            except Exception as fallback_error:
                return f"Error calling Claude API: {str(e)}\nFallback attempt also failed: {str(fallback_error)}"

    def _call_openai_api(self, system_prompt, user_message, file_path):
        """Call the OpenAI or OpenAI-compatible API"""
        # (Implementation remains the same as before)
        try:
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1].lower()
            
            # Check client initialization
            if not self.client or not isinstance(self.client, openai.OpenAI):
                 return f"Error: OpenAI client not initialized correctly."

            model = self.api_settings.get('model', 'gpt-4')
            temperature = float(self.api_settings.get('temperature', 0.7))
            is_compatible = self.api_settings.get('type', '') == 'openai_compatible'
            
            messages = [{"role": "system", "content": system_prompt}]
            user_content = [{"type": "text", "text": f"{user_message}\n\nFile: {filename}"}]

            # Handle file content based on type
            text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html']
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

            if file_extension == '.pdf':
                pdf_text = None
                if PYPDF2_AVAILABLE:
                    try:
                        with open(file_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            pdf_text = ""
                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                pdf_text += f"\n--- Page {page_num + 1} ---\n"
                                pdf_text += page.extract_text() or "" # Handle empty pages
                        if pdf_text:
                             user_content[0]["text"] += f"\n\nExtracted PDF Content:\n{pdf_text}"
                        else:
                             user_content[0]["text"] += "\n\n(Could not extract text from PDF.)"
                    except Exception as pdf_error:
                        print(f"Error extracting PDF text: {pdf_error}")
                        user_content[0]["text"] += "\n\n(Error extracting PDF content.)"
                else:
                    user_content[0]["text"] += "\n\n(PDF processing requires PyPDF2 library.)"

            elif file_extension in image_extensions:
                if PIL_AVAILABLE: # Check if Pillow is available for image handling
                    try:
                        file_content_base64 = self._encode_file(file_path)
                        if file_content_base64:
                            media_type = self._get_media_type(file_extension)
                            user_content.append({
                                "type": "image_url", 
                                "image_url": {"url": f"data:{media_type};base64,{file_content_base64}"}
                            })
                        else:
                            user_content[0]["text"] += "\n\n(Could not encode image file.)"
                    except Exception as img_err:
                         print(f"Error processing image for OpenAI: {img_err}")
                         user_content[0]["text"] += "\n\n(Error processing image file.)"
                else:
                     user_content[0]["text"] += "\n\n(Image processing requires Pillow library.)"

            elif file_extension in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_text = f.read()
                    user_content[0]["text"] += f"\n\nFile Contents:\n{file_text}"
                except UnicodeDecodeError:
                    user_content[0]["text"] += "\n\n(File contents could not be read as text.)"
                except Exception as txt_err:
                    print(f"Error reading text file: {txt_err}")
                    user_content[0]["text"] += "\n\n(Error reading file content.)"
            else:
                # For other file types
                user_content[0]["text"] += "\n\n(File contents could not be included due to format compatibility.)"

            messages.append({"role": "user", "content": user_content})

            try:
                response = self.client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    messages=messages
                )
                return response.choices[0].message.content
            except Exception as api_error:
                 # Handle API errors, especially for compatible providers
                 print(f"OpenAI/Compatible API error: {api_error}")
                 if is_compatible:
                     # Try a simpler text-only request as fallback for compatible APIs
                     try:
                         print("Attempting text-only fallback for OpenAI-compatible API...")
                         fallback_messages = [
                             {"role": "system", "content": system_prompt},
                             {"role": "user", "content": f"{user_message}\n\nFile: {filename}\n\n(File content omitted due to potential API incompatibility.)"}
                         ]
                         response = self.client.chat.completions.create(
                             model=model,
                             temperature=temperature,
                             messages=fallback_messages
                         )
                         return response.choices[0].message.content
                     except Exception as fallback_error:
                         return f"Error: API provider failed. Details: {str(api_error)}. Fallback attempt also failed: {str(fallback_error)}"
                 else:
                     # Re-raise for standard OpenAI
                     raise api_error

        except Exception as e:
            api_type_str = "OpenAI-compatible" if is_compatible else "OpenAI"
            print(f"Error calling {api_type_str} API: {e}")
            return f"Error calling {api_type_str} API: {str(e)}"

    def _call_gemini_api(self, system_prompt, user_message, file_path, reasoning_prompt):
        """Call the Google Gemini API"""
        try:
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1].lower()
            
            # Check client initialization (Gemini uses the library module)
            if not self.client or self.client != genai:
                 return f"Error: Gemini client not configured correctly."

            model_name = self.api_settings.get('model', 'gemini-1.5-pro-latest')
            temperature = float(self.api_settings.get('temperature', 0.7))
            
            # Initialize the Gemini model
            # Apply safety settings - adjust as needed
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            # Generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                # max_output_tokens=4000 # Adjust if needed, Gemini has higher limits
            )

            # Handle system prompt (instruction)
            # Combine system prompt and reasoning prompt for Gemini's system_instruction
            full_system_instruction = system_prompt
            if reasoning_prompt:
                full_system_instruction += f"\n\n{reasoning_prompt}"

            model = self.client.GenerativeModel(
                model_name=model_name,
                safety_settings=safety_settings,
                generation_config=generation_config,
                system_instruction=full_system_instruction if full_system_instruction else None 
            )

            # Prepare content for Gemini API
            gemini_content = []
            
            # Add user text message first
            gemini_content.append(f"{user_message}\n\nFile: {filename}")

            # Handle file content based on type
            text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html']
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp'] # Gemini supports these image types well

            if file_extension in image_extensions:
                if PIL_AVAILABLE:
                    try:
                        img = Image.open(file_path)
                        # Gemini SDK prefers PIL Image objects directly
                        gemini_content.append(img) 
                    except Exception as img_err:
                        print(f"Error opening image file {filename} with Pillow: {img_err}")
                        gemini_content.append("\n\n(Could not process image file.)")
                else:
                    gemini_content.append("\n\n(Image processing requires Pillow library.)")
            
            elif file_extension == '.pdf':
                 # Gemini doesn't directly ingest PDFs via the standard API like Claude.
                 # Best approach is text extraction if possible.
                 pdf_text = None
                 if PYPDF2_AVAILABLE:
                     try:
                         with open(file_path, 'rb') as f:
                             pdf_reader = PyPDF2.PdfReader(f)
                             pdf_text = ""
                             for page_num in range(len(pdf_reader.pages)):
                                 page = pdf_reader.pages[page_num]
                                 pdf_text += f"\n--- Page {page_num + 1} ---\n"
                                 pdf_text += page.extract_text() or ""
                         if pdf_text:
                              gemini_content.append(f"\n\nExtracted PDF Content:\n{pdf_text}")
                         else:
                              gemini_content.append("\n\n(Could not extract text from PDF.)")
                     except Exception as pdf_error:
                         print(f"Error extracting PDF text for Gemini: {pdf_error}")
                         gemini_content.append("\n\n(Error extracting PDF content.)")
                 else:
                     gemini_content.append("\n\n(PDF text extraction requires PyPDF2 library.)")

            elif file_extension in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_text = f.read()
                    gemini_content.append(f"\n\nFile Contents:\n{file_text}")
                except UnicodeDecodeError:
                    gemini_content.append("\n\n(File contents could not be read as text.)")
                except Exception as txt_err:
                    print(f"Error reading text file for Gemini: {txt_err}")
                    gemini_content.append("\n\n(Error reading file content.)")
            else:
                # For other unsupported file types
                gemini_content.append("\n\n(File type not directly supported for content inclusion.)")

            # Call Gemini API
            response = model.generate_content(gemini_content)
            
            # Extract text response
            # Handle potential blocked responses due to safety settings
            if response.parts:
                 return "".join(part.text for part in response.parts if hasattr(part, 'text'))
            elif response.prompt_feedback.block_reason:
                 return f"Error: Response blocked due to {response.prompt_feedback.block_reason}. Content may violate safety policies."
            else:
                 # Sometimes the response might be empty without an explicit block reason
                 # Check candidates if available
                 try:
                     return response.text # Accessing .text directly might work sometimes
                 except ValueError: # Handle cases where .text access fails (e.g., blocked)
                     print(f"Gemini response issue: No parts and no block reason. Full response: {response}")
                     return "Error: Received an empty or blocked response from Gemini."


        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            import traceback
            traceback.print_exc()
            return f"Error calling Gemini API: {str(e)}"

    def _append_to_merged_output(self, filename, result):
        """Append result to merged output file"""
        try:
            with open(self.merged_output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{'='*50}\n")
                f.write(f"FILE: {filename}\n")
                f.write(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                # Include model ID used for this specific output
                model_id = self.api_settings.get('model', 'N/A')
                api_type = self.api_settings.get('type', 'N/A')
                f.write(f"API_TYPE: {api_type}\n")
                f.write(f"MODEL_ID: {model_id}\n")
                f.write(f"{'='*50}\n\n")
                f.write(result)
        except Exception as e:
            print(f"Error appending to merged output: {e}")
    
    def get_files_list(self):
        """Get list of files in the files directory"""
        try:
            files = [f for f in os.listdir(self.files_dir) 
                    if os.path.isfile(os.path.join(self.files_dir, f)) and not f.startswith('.')] # Ignore hidden files
            return files
        except Exception as e:
            print(f"Error getting files list: {e}")
            return []
    
    def process_all_files(self, progress_callback=None):
        """Process all files in the files directory with rate limiting"""
        files = self.get_files_list()
        results = []
        
        for i, filename in enumerate(files):
            file_path = os.path.join(self.files_dir, filename)
            result = self.process_file(file_path)
            results.append(result)
            
            # Call progress callback if provided
            if progress_callback:
                # If callback returns False, it means processing was canceled
                if not progress_callback(i + 1, len(files), result):
                    print("File processing canceled")
                    break
                
            # Add delay between files (except after the last one)
            # The actual sleep is handled in the UI callback to keep it responsive
            # if i < len(files) - 1 and self.rate_limit_delay > 0:
            #     time.sleep(self.rate_limit_delay) 
        
        return results
