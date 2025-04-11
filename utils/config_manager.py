#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Manager
Handles application configuration and settings
"""

import os
import json
import shutil
from pathlib import Path

class ConfigManager:
    """Manages application configuration and settings"""
    
    def __init__(self):
        """Initialize configuration manager"""
        # Configuration directory in user's home
        self.config_dir = os.path.expanduser("~/.configurational_llm")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Output directory in Documents
        self.output_dir = os.path.expanduser("~/Documents/ConfigurationalLLM")
        
        # Ensure directories exist
        self._ensure_dirs()
        
        # Load or create initial configuration
        self.config = self._load_config()
    
    def _ensure_dirs(self):
        """Ensure that required directories exist"""
        # Create config directory if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Create output directories
        dirs_to_create = [
            self.output_dir,
            os.path.join(self.output_dir, 'prompts'),
            os.path.join(self.output_dir, 'messages'),
            os.path.join(self.output_dir, 'outputs'),
            os.path.join(self.output_dir, 'files')
        ]
        
        for directory in dirs_to_create:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self):
        """Create and return default configuration"""
        default_config = {
            "api_settings": {
                "type": "claude",  # claude, openai, or openai_compatible
                "api_key": "",
                "api_base": "https://api.anthropic.com",
                "model": "claude-3-7-sonnet-20250219",
                "temperature": 0.7,
                "reasoning_level": "medium"  # low, medium, high
            },
            "prompts": {
                "system_prompt": "You are a helpful assistant designed to process scientific literature. Your task is to analyze the provided document and extract key information. Be objective and accurate in your analysis."
            },
            "message": {
                "user_message": "Please analyze this document and summarize the key findings, methodology, and conclusions. If there are any tables or charts, describe their contents."
            },
            "language": "en_US"  # Default language
        }
        
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_output_dir(self):
        """Get output directory path"""
        return self.output_dir
    
    def get_api_settings(self):
        """Get API settings"""
        return self.config.get("api_settings", {})
    
    def set_api_settings(self, settings):
        """Set API settings"""
        self.config["api_settings"] = settings
        return self._save_config()
    
    def get_prompts(self):
        """Get prompts settings"""
        return self.config.get("prompts", {})
    
    def set_prompts(self, prompts):
        """Set prompts settings"""
        self.config["prompts"] = prompts
        return self._save_config()
    
    def get_message(self):
        """Get message settings"""
        return self.config.get("message", {})
    
    def set_message(self, message):
        """Set message settings"""
        self.config["message"] = message
        return self._save_config()
    
    def get_language(self):
        """Get current language setting"""
        return self.config.get("language", "en_US")
    
    def set_language(self, language):
        """Set language setting"""
        self.config["language"] = language
        return self._save_config()
