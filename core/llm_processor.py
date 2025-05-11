#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Processor
Handles interactions with LLM APIs (Claude, OpenAI, Gemini, and OpenAI-compatible),
supports iterative processing, MD5 hashing, and CSV logging.
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
import hashlib # Added for MD5
import csv # Added for CSV output

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


def _calculate_md5(file_path):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error calculating MD5 for {file_path}: {e}")
        return "md5_error"

class LLMProcessor:
    """Processes interactions with LLM APIs"""
    
    def __init__(self, config_manager):
        """Initialize LLM processor with configuration"""
        self.config_manager = config_manager
        self.api_settings = config_manager.get_api_settings()
        self.output_dir = config_manager.get_output_dir()
        
        self.client = None 
        self._initialize_clients()
        
        self.prompts_dir = os.path.join(self.output_dir, 'prompts')
        self.messages_dir = os.path.join(self.output_dir, 'messages')
        self.outputs_dir = os.path.join(self.output_dir, 'outputs')
        self.files_dir = os.path.join(self.output_dir, 'files') # Source files for processing
        
        # Ensure output directories exist
        for dir_path in [self.prompts_dir, self.messages_dir, self.outputs_dir]:
            os.makedirs(dir_path, exist_ok=True)

        self.merged_output_file = os.path.join(self.output_dir, 'merged_output.txt')
        self.summary_csv_file = os.path.join(self.output_dir, 'processing_summary.csv')
        self._initialize_csv()

    def _initialize_csv(self):
        """Initializes the CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.summary_csv_file):
            with open(self.summary_csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "Filename", "MD5_Hash", "Iteration_Num", 
                    "API_Type", "Model_ID", "Result_Snippet", "Output_File_Path", "Error"
                ])

    def _log_to_csv(self, timestamp, filename, md5_hash, iteration_num, api_type, model_id, result, output_file_path, error_message=None):
        """Appends a record to the summary CSV file."""
        result_snippet = (result[:100] + '...') if result and len(result) > 100 else result
        if error_message: 
            result_snippet = (error_message[:100] + '...') if error_message and len(error_message) > 100 else error_message
        
        try:
            with open(self.summary_csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, filename, md5_hash, iteration_num, 
                    api_type, model_id, result_snippet, output_file_path, error_message or ""
                ])
        except Exception as e:
            print(f"Error writing to CSV: {e}")

    def _initialize_clients(self):
        """Initialize API clients based on settings"""
        api_type = self.api_settings.get('type', 'claude')
        api_key = self.api_settings.get('api_key', '')
        api_base = self.api_settings.get('api_base', None)
        
        self.client = None
        
        try:
            if api_type == 'claude':
                claude_base_url = api_base or 'https://api.anthropic.com'
                # Ensure base_url for Claude SDK does not end with /v1, as SDK appends it.
                if claude_base_url.endswith('/v1'):
                    claude_base_url = claude_base_url[:-3] 
                elif claude_base_url.endswith('/v1/'): # also handle trailing slash
                    claude_base_url = claude_base_url[:-4]

                self.client = anthropic.Anthropic(api_key=api_key, base_url=claude_base_url if claude_base_url != 'https://api.anthropic.com' else None)
                self._test_claude_connection()
            elif api_type == 'openai':
                openai_base_url = api_base or 'https://api.openai.com/v1'
                self.client = openai.OpenAI(api_key=api_key, base_url=openai_base_url)
            elif api_type == 'gemini':
                genai.configure(api_key=api_key) # Gemini doesn't use base_url in configure in the same way
                self.client = genai 
                self._test_gemini_connection()
            else:  # OpenAI-compatible
                compatible_base_url = api_base or 'https://api.deepseek.com/v1' 
                self.client = openai.OpenAI(api_key=api_key, base_url=compatible_base_url)
        except Exception as e:
            print(f"Warning: Error initializing {api_type} client: {e}")
            self.client = None

    def _test_claude_connection(self):
        try:
            if not hasattr(self.client, 'messages'):
                print("Warning: Anthropic client missing expected attributes")
                return False
            return True
        except Exception as e:
            print(f"Error testing Claude connection: {e}")
            return False

    def _test_gemini_connection(self):
        try:
            models = genai.list_models()
            if any('generateContent' in m.supported_generation_methods for m in models):
                 print("Gemini connection successful.")
                 return True
            else:
                 print("Warning: No generative models found via Gemini API.")
                 return False
        except Exception as e:
            print(f"Error testing Gemini connection: {e}")
            self.client = None 
            return False

    def refresh_settings(self):
        self.api_settings = self.config_manager.get_api_settings()
        self._initialize_clients()
    
    def _get_reasoning_prompt(self):
        reasoning_enabled = self.api_settings.get('reasoning_enabled', True)
        if not reasoning_enabled: return ""
        level = self.api_settings.get('reasoning_level', 'medium')
        prompts = {
            'low': "Think step-by-step.",
            'medium': "Think step-by-step carefully and provide detailed reasoning.",
            'high': "Think step-by-step very carefully, showing your detailed reasoning process and evidence evaluation."
        }
        return prompts.get(level, prompts['medium'])
    
    def _encode_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding file {file_path}: {e}")
            return None

    def _get_media_type(self, file_extension):
        types = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.pdf': 'application/pdf'}
        return types.get(file_extension, 'application/octet-stream')

    def process_file(self, file_path, iteration_num):
        current_timestamp_obj = datetime.now()
        current_timestamp_str = current_timestamp_obj.strftime("%Y-%m-%d %H:%M:%S")
        file_timestamp_str = current_timestamp_obj.strftime("%Y%m%d_%H%M%S")
        
        filename = os.path.basename(file_path)
        md5_hash = _calculate_md5(file_path)
        md5_short = md5_hash[:8] if md5_hash != "md5_error" else "md5_error"

        api_type = self.api_settings.get('type', 'unknown')
        model_id = self.api_settings.get('model', 'N/A')
        output_file_path = ""
        error_message_for_csv = None

        try:
            self.refresh_settings() 
            
            if not self.client:
                 error_msg = f"Error: API client for '{api_type}' not initialized. Check API key and settings."
                 self._log_to_csv(current_timestamp_str, filename, md5_hash, iteration_num, api_type, model_id, error_msg, "", error_msg)
                 return {'filename': filename, 'md5': md5_hash, 'iteration': iteration_num, 'result': error_msg, 'error': True}

            prompts = self.config_manager.get_prompts()
            message_config = self.config_manager.get_message()
            
            system_prompt = prompts.get('system_prompt', '')
            user_message_template = message_config.get('user_message', '')
            
            user_message = user_message_template.replace("{filename}", filename)\
                                               .replace("{md5}", md5_hash)\
                                               .replace("{iteration}", str(iteration_num))

            reasoning_prompt = self._get_reasoning_prompt()
            combined_system_prompt = f"{system_prompt}"
            if reasoning_prompt:
                combined_system_prompt += f" {reasoning_prompt}"
            
            prompt_filename = f"prompt_{filename}_{md5_short}_iter{iteration_num}_{file_timestamp_str}.txt"
            message_filename = f"message_{filename}_{md5_short}_iter{iteration_num}_{file_timestamp_str}.txt"
            output_filename = f"output_{filename}_{md5_short}_iter{iteration_num}_{file_timestamp_str}.txt"
            
            prompt_file_path = os.path.join(self.prompts_dir, prompt_filename)
            message_file_path = os.path.join(self.messages_dir, message_filename)
            output_file_path = os.path.join(self.outputs_dir, output_filename)
            
            with open(prompt_file_path, 'w', encoding='utf-8') as f: f.write(combined_system_prompt)
            with open(message_file_path, 'w', encoding='utf-8') as f: f.write(user_message)
            
            if api_type == 'claude':
                result = self._call_claude_api(combined_system_prompt, user_message, file_path, filename, md5_hash, iteration_num)
            elif api_type == 'gemini':
                result = self._call_gemini_api(system_prompt, user_message, file_path, reasoning_prompt, filename, md5_hash, iteration_num)
            else:
                result = self._call_openai_api(combined_system_prompt, user_message, file_path, filename, md5_hash, iteration_num)
            
            output_content = f"File: {filename}\nMD5: {md5_hash}\nIteration: {iteration_num}\nTimestamp: {current_timestamp_str}\nAPI: {api_type}\nModel: {model_id}\n\n{result}"
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
                
            self._append_to_merged_output(filename, md5_hash, iteration_num, result, current_timestamp_str)
            self._log_to_csv(current_timestamp_str, filename, md5_hash, iteration_num, api_type, model_id, result, output_file_path)
            
            return {'filename': filename, 'md5': md5_hash, 'iteration': iteration_num, 'result': result, 'output_file': output_file_path, 'error': False}
            
        except Exception as e:
            print(f"Error processing file {file_path} (iter {iteration_num}): {e}")
            import traceback
            traceback.print_exc()
            error_message_for_csv = f"Error: {str(e)}"
            self._log_to_csv(current_timestamp_str, filename, md5_hash, iteration_num, api_type, model_id, "", output_file_path, error_message_for_csv)
            return {'filename': filename, 'md5': md5_hash, 'iteration': iteration_num, 'result': error_message_for_csv, 'error': True}

    def _call_claude_api_direct(self, system_prompt, user_message, filename, file_content=None, file_type=None):
        try:
            api_key = self.api_settings.get('api_key', '')
            # Use the API base from settings, ensuring it does NOT end with /v1 for direct call construction
            api_base_from_config = self.api_settings.get('api_base', 'https://api.anthropic.com')
            if api_base_from_config.endswith('/v1'):
                api_base_from_config = api_base_from_config[:-3]
            if api_base_from_config.endswith('/v1/'):
                api_base_from_config = api_base_from_config[:-4]

            model = self.api_settings.get('model', 'claude-3-opus-20240229') 
            temperature = float(self.api_settings.get('temperature', 0.7))
            
            # Construct the full URL for the messages endpoint
            api_url = f"{api_base_from_config.rstrip('/')}/v1/messages"
            
            headers = {"Content-Type": "application/json", "X-Api-Key": api_key, "anthropic-version": "2023-06-01"}
            content_for_api = [{"type": "text", "text": user_message}]

            if file_content and file_type == "text":
                 content_for_api[0]["text"] += f"\n\nFile Contents:\n{file_content}"
            elif file_type in ["image", "pdf"]:
                 content_for_api[0]["text"] += f"\n\n(File type {file_type} not directly embeddable in this fallback)"

            data = {"model": model, "temperature": temperature, "max_tokens": 4096, "system": system_prompt, "messages": [{"role": "user", "content": content_for_api}]}
            
            session = requests.Session()
            response = session.post(api_url, headers=headers, json=data, timeout=180) 
            
            if response.status_code == 200:
                result = response.json()
                return "".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")
            else:
                error_detail = response.text
                try: error_detail = json.dumps(response.json().get("error", error_detail))
                except: pass
                return f"Error: API returned status {response.status_code}: {error_detail} (URL: {api_url})"
        except Exception as e:
            return f"Error using direct API call: {str(e)}"

    def _call_claude_api(self, system_prompt, user_message, file_path, filename, md5_hash, iteration_num):
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            
            if not self.client or not isinstance(self.client, anthropic.Anthropic):
                print("Claude client not initialized. Attempting direct fallback.")
                text_content, file_type_fallback = None, None
                if file_extension in ['.txt', '.md', '.csv', '.json', '.xml', '.html']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f: text_content = f.read()
                        file_type_fallback = "text"
                    except: pass
                elif file_extension == '.pdf': file_type_fallback = "pdf"
                elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']: file_type_fallback = "image"
                return self._call_claude_api_direct(system_prompt, user_message, filename, text_content, file_type_fallback)

            file_content_base64 = self._encode_file(file_path)
            if not file_content_base64: return f"Error: Could not read file {filename}"

            model = self.api_settings.get('model', 'claude-3-opus-20240229')
            temperature = float(self.api_settings.get('temperature', 0.7))
            api_message_content = [{"type": "text", "text": user_message}]

            if file_extension == '.pdf':
                api_message_content.insert(0, {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": file_content_base64}})
            elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                media_type = self._get_media_type(file_extension)
                api_message_content.insert(0, {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": file_content_base64}})
            elif file_extension in ['.txt', '.md', '.csv', '.json', '.xml', '.html']:
                 try:
                     with open(file_path, 'r', encoding='utf-8') as f: file_text = f.read()
                     for item in api_message_content:
                         if item["type"] == "text": item["text"] += f"\n\nFile Contents:\n{file_text}"; break
                 except Exception as e:
                     print(f"Could not read text file {filename} for Claude: {e}")
                     for item in api_message_content:
                         if item["type"] == "text": item["text"] += "\n\n(Could not include file content due to read error)"; break
            else: 
                for item in api_message_content:
                    if item["type"] == "text": item["text"] += "\n\n(File type not directly embeddable)"; break
            
            try:
                response = self.client.messages.create(model=model, max_tokens=4096, temperature=temperature, system=system_prompt, messages=[{"role": "user", "content": api_message_content}])
            except Exception as specific_error:
                print(f"Claude SDK API error: {specific_error}. Falling back to direct call.")
                text_content_fallback, file_type_fallback = None, None
                if file_extension in ['.txt', '.md']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f: text_content_fallback = f.read()
                        file_type_fallback = "text"
                    except: pass
                return self._call_claude_api_direct(system_prompt, user_message, filename, text_content_fallback, file_type_fallback)

            return "".join(c.text for c in response.content if c.type == "text")
        except Exception as e:
            print(f"Error calling Claude API: {e}. Attempting final fallback.")
            text_content_fallback, file_type_fallback = None, None
            if os.path.splitext(filename)[1].lower() in ['.txt', '.md']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f: text_content_fallback = f.read()
                    file_type_fallback = "text"
                except: pass
            return self._call_claude_api_direct(system_prompt, user_message, filename, text_content_fallback, file_type_fallback)

    def _call_openai_api(self, system_prompt, user_message, file_path, filename, md5_hash, iteration_num):
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            if not self.client or not isinstance(self.client, openai.OpenAI): return f"Error: OpenAI client not initialized."
            model = self.api_settings.get('model', 'gpt-4-turbo') 
            temperature = float(self.api_settings.get('temperature', 0.7))
            is_compatible = self.api_settings.get('type', '') == 'openai_compatible'
            messages_for_api = [{"role": "system", "content": system_prompt}]
            user_content_parts = [{"type": "text", "text": user_message}]
            text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html']
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

            if file_extension == '.pdf':
                if PYPDF2_AVAILABLE:
                    try:
                        pdf_text = "" # Initialize pdf_text
                        truncation_note = "" # Initialize truncation_note
                        with open(file_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            pdf_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
                        
                        # Truncate if using compatible API and text is very long
                        if is_compatible and pdf_text and len(pdf_text) > 15000: 
                            original_len = len(pdf_text)
                            pdf_text = pdf_text[:15000] # Truncate to 15000 characters
                            truncation_note = f"\n\n(Extracted PDF content was truncated from {original_len} to 15000 chars for compatible API)"
                            print(f"Warning: PDF text for {filename} (MD5: {md5_hash}, Iter: {iteration_num}) truncated to 15000 characters for compatible API.")

                        if pdf_text: 
                            user_content_parts[0]["text"] += f"\n\nExtracted PDF Content:\n{pdf_text}{truncation_note}"
                        else: 
                            user_content_parts[0]["text"] += "\n\n(Could not extract text from PDF.)"
                    except Exception as e: user_content_parts[0]["text"] += f"\n\n(Error extracting PDF: {e})"
                else: user_content_parts[0]["text"] += "\n\n(PDF processing needs PyPDF2)"
            elif file_extension in image_extensions:
                if PIL_AVAILABLE:
                    try:
                        b64_content = self._encode_file(file_path)
                        if b64_content: user_content_parts.append({"type": "image_url", "image_url": {"url": f"data:{self._get_media_type(file_extension)};base64,{b64_content}"}})
                        else: user_content_parts[0]["text"] += "\n\n(Could not encode image)"
                    except Exception as e: user_content_parts[0]["text"] += f"\n\n(Error processing image: {e})"
                else: user_content_parts[0]["text"] += "\n\n(Image processing needs Pillow)"
            elif file_extension in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f: file_text = f.read()
                    user_content_parts[0]["text"] += f"\n\nFile Contents:\n{file_text}"
                except Exception as e: user_content_parts[0]["text"] += f"\n\n(Error reading text file: {e})"
            else: user_content_parts[0]["text"] += "\n\n(File type not directly embeddable)"
            messages_for_api.append({"role": "user", "content": user_content_parts})
            try:
                response = self.client.chat.completions.create(model=model, temperature=temperature, messages=messages_for_api, max_tokens=4000)
                return response.choices[0].message.content
            except Exception as api_error:
                 print(f"OpenAI/Compatible API error during initial call: {api_error}") # Enhanced logging
                 if is_compatible: 
                     print(f"Detailed error from compatible API: {type(api_error).__name__} - {str(api_error)}") # More detailed error
                     print("Attempting text-only fallback for OpenAI-compatible API...")
                     fallback_messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message + "\n\n(File content omitted due to API issue. Initial error: " + str(api_error)[:100] + ")"}] # Add error snippet to note
                     response = self.client.chat.completions.create(model=model,temperature=temperature,messages=fallback_messages)
                     return response.choices[0].message.content
                 raise api_error
        except Exception as e: return f"Error calling {self.api_settings.get('type', 'OpenAI')} API: {str(e)}"

    def _call_gemini_api(self, system_prompt, user_message, file_path, reasoning_prompt, filename, md5_hash, iteration_num):
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            if not self.client or self.client != genai: return f"Error: Gemini client not configured."
            model_name = self.api_settings.get('model', 'gemini-1.5-pro-latest')
            temperature = float(self.api_settings.get('temperature', 0.7))

            configurable_categories_enums = [
                HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                HarmCategory.HARM_CATEGORY_HARASSMENT,
            ]
            if hasattr(HarmCategory, 'HARM_CATEGORY_CIVIC_INTEGRITY'):
                configurable_categories_enums.append(HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY)
            
            safety_settings = [
                {
                    'category': cat_enum.name, 
                    'threshold': HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE.name 
                }
                for cat_enum in configurable_categories_enums
            ]
            
            generation_config = genai.types.GenerationConfig(temperature=temperature)
            full_system_instruction = system_prompt + (f"\n\n{reasoning_prompt}" if reasoning_prompt else "")
            model = self.client.GenerativeModel(model_name=model_name, safety_settings=safety_settings, generation_config=generation_config, system_instruction=full_system_instruction or None)
            
            gemini_parts = [user_message] 
            text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html']
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp']

            if file_extension in image_extensions:
                if PIL_AVAILABLE:
                    try: gemini_parts.append(Image.open(file_path))
                    except Exception as e: gemini_parts.append(f"\n\n(Error opening image: {e})")
                else: gemini_parts.append("\n\n(Image processing needs Pillow)")
            elif file_extension == '.pdf':
                try:
                    print(f"Attempting to upload PDF to Gemini: {file_path}")
                    if not os.path.exists(file_path):
                        gemini_parts.append("\n\n(Error: PDF file not found at path for Gemini upload.)")
                    else:
                        uploaded_file = genai.upload_file(path=file_path, mime_type='application/pdf')
                        gemini_parts.append(uploaded_file)
                        print(f"Successfully uploaded PDF: {uploaded_file.name}")
                except Exception as e_upload:
                    print(f"Error uploading PDF to Gemini: {e_upload}. Falling back to text extraction.")
                    gemini_parts.append(f"\n\n(Notice: PDF direct upload failed: {e_upload}. Attempting text extraction.)")
                    if PYPDF2_AVAILABLE:
                        try:
                            with open(file_path, 'rb') as f:
                                pdf_reader = PyPDF2.PdfReader(f)
                                pdf_text = "".join(page.extract_text() or "" for page in pdf_reader.pages if page.extract_text())
                            if pdf_text.strip():
                                gemini_parts.append(f"\n\nExtracted PDF Content (fallback):\n{pdf_text}")
                            else:
                                gemini_parts.append("\n\n(Fallback: No text could be extracted from PDF using PyPDF2.)")
                        except Exception as e_pypdf:
                            gemini_parts.append(f"\n\n(Fallback: Error extracting PDF text using PyPDF2: {e_pypdf})")
                    else:
                        gemini_parts.append("\n\n(Fallback: PyPDF2 not available for PDF text extraction.)")
            elif file_extension in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f: file_text = f.read()
                    gemini_parts.append(f"\n\nFile Contents:\n{file_text}")
                except Exception as e: gemini_parts.append(f"\n\n(Error reading text file: {e})")
            else: gemini_parts.append("\n\n(File type not directly supported for content inclusion.)")
            
            response = model.generate_content(gemini_parts)
            
            if response.parts: return "".join(part.text for part in response.parts if hasattr(part, 'text'))
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                 return f"Error: Response blocked ({response.prompt_feedback.block_reason}). Details: {response.prompt_feedback}"
            else:
                 try: return response.text 
                 except ValueError: 
                      print(f"Unexpected Gemini response structure: {response}")
                      return "Error: Empty or unexpected response format from Gemini."
        except Exception as e: 
            print(f"Gemini API call failed. Safety Settings: {safety_settings}, Params: model_name={model_name}, temp={temperature}")
            return f"Error calling Gemini API: {str(e)}"

    def _append_to_merged_output(self, filename, md5_hash, iteration_num, result, timestamp_str):
        try:
            with open(self.merged_output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{'='*50}\nFILE: {filename}\nMD5: {md5_hash}\nITERATION: {iteration_num}\nTIMESTAMP: {timestamp_str}\n")
                f.write(f"API_TYPE: {self.api_settings.get('type', 'N/A')}\nMODEL_ID: {self.api_settings.get('model', 'N/A')}\n{'='*50}\n\n{result}")
        except Exception as e: print(f"Error appending to merged output: {e}")
    
    def get_files_list(self):
        try: return [f for f in os.listdir(self.files_dir) if os.path.isfile(os.path.join(self.files_dir, f)) and not f.startswith('.')]
        except Exception as e: print(f"Error getting files list: {e}"); return []
    
    def process_files_iteratively(self, file_paths_to_process, num_iterations, delay_seconds, progress_callback, completion_callback):
        total_files, total_steps = len(file_paths_to_process), len(file_paths_to_process) * num_iterations
        completed_steps, all_results, errors = 0, [], []
        for file_idx, file_path in enumerate(file_paths_to_process):
            filename = os.path.basename(file_path)
            for iter_idx in range(num_iterations):
                current_iter_num = iter_idx + 1
                progress_percent = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
                if progress_callback and not progress_callback(file_idx + 1, total_files, current_iter_num, num_iterations, filename, progress_percent):
                    if completion_callback: completion_callback("Processing cancelled.", "User cancellation")
                    return {"status": "cancelled", "results": all_results, "errors": errors}
                print(f"Processing {filename}, Iteration {current_iter_num}/{num_iterations}")
                result_data = self.process_file(file_path, current_iter_num)
                all_results.append(result_data)
                if result_data.get('error'): errors.append(f"File: {filename}, Iter: {current_iter_num} - {result_data.get('result')}")
                completed_steps += 1
                if completed_steps < total_steps and delay_seconds > 0:
                    print(f"Delaying for {delay_seconds}s..."); time.sleep(delay_seconds)
        if progress_callback: progress_callback(total_files, total_files, num_iterations, num_iterations, "All Done", 100)
        msg, err_summary = ("Processing complete.", None) if not errors else ("Processing completed with errors.", "\n".join(errors))
        if completion_callback: completion_callback(msg, err_summary)
        return {"status": "completed", "results": all_results, "errors": errors}
