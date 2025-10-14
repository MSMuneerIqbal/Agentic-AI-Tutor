"""
Gemini API Manager with Multiple API Keys and Automatic Failover
Handles quota management and automatic switching between API keys
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GeminiAPIManager:
    """
    Manages multiple Gemini API keys with automatic failover and quota management.
    """
    
    def __init__(self):
        self.api_keys = [
            "AIzaSyBL-wWNOaQR54BJxxYgFTEEixar6kf9Z3c",
            "AIzaSyAKTITRjPPgWKExRRCCSjT_xW_sy10WDSk", 
            "AIzaSyAjN4eXQA8fU9rmnrJ4otUwbozcaPF5YMg",
            "AIzaSyCSJwyQJNKkFrK2VlPMFiCzpL8uom7KH9w"
        ]
        
        self.models = [
            "gemini-2.0-flash-exp",
            "gemini-1.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-flash"
        ]
        
        self.current_key_index = 0
        self.current_model_index = 0
        self.key_usage_stats = {}
        self.key_quota_limits = {}
        self.key_last_reset = {}
        self.failed_keys = set()
        
        # Initialize usage tracking
        for i, key in enumerate(self.api_keys):
            self.key_usage_stats[key] = {
                'requests': 0,
                'tokens': 0,
                'errors': 0,
                'last_used': None,
                'quota_exceeded': False
            }
            self.key_quota_limits[key] = {
                'requests_per_minute': 60,
                'requests_per_day': 1500,
                'tokens_per_minute': 32000,
                'tokens_per_day': 1000000
            }
            self.key_last_reset[key] = datetime.now()
    
    def get_current_config(self) -> Dict[str, str]:
        """Get current API key and model configuration."""
        return {
            'api_key': self.api_keys[self.current_key_index],
            'model': self.models[self.current_model_index]
        }
    
    def switch_to_next_key(self) -> bool:
        """Switch to the next available API key."""
        original_index = self.current_key_index
        
        for _ in range(len(self.api_keys)):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            current_key = self.api_keys[self.current_key_index]
            
            if current_key not in self.failed_keys:
                logger.info(f"Switched to API key index {self.current_key_index}")
                return True
        
        # If all keys are failed, reset failed keys and try again
        if len(self.failed_keys) == len(self.api_keys):
            logger.warning("All API keys failed, resetting failed keys list")
            self.failed_keys.clear()
            self.current_key_index = (original_index + 1) % len(self.api_keys)
            return True
        
        return False
    
    def switch_to_next_model(self) -> bool:
        """Switch to the next available model."""
        self.current_model_index = (self.current_model_index + 1) % len(self.models)
        logger.info(f"Switched to model: {self.models[self.current_model_index]}")
        return True
    
    def update_usage_stats(self, api_key: str, tokens_used: int = 0, error: bool = False):
        """Update usage statistics for an API key."""
        if api_key not in self.key_usage_stats:
            return
        
        stats = self.key_usage_stats[api_key]
        stats['requests'] += 1
        stats['tokens'] += tokens_used
        stats['last_used'] = datetime.now()
        
        if error:
            stats['errors'] += 1
    
    def check_quota_limits(self, api_key: str) -> bool:
        """Check if API key is within quota limits."""
        if api_key not in self.key_usage_stats:
            return True
        
        stats = self.key_usage_stats[api_key]
        limits = self.key_quota_limits[api_key]
        now = datetime.now()
        
        # Reset daily counters if needed
        if now.date() > self.key_last_reset[api_key].date():
            stats['requests'] = 0
            stats['tokens'] = 0
            self.key_last_reset[api_key] = now
        
        # Check limits
        if stats['requests'] >= limits['requests_per_day']:
            logger.warning(f"API key {api_key[:10]}... exceeded daily request limit")
            stats['quota_exceeded'] = True
            return False
        
        if stats['tokens'] >= limits['tokens_per_day']:
            logger.warning(f"API key {api_key[:10]}... exceeded daily token limit")
            stats['quota_exceeded'] = True
            return False
        
        return True
    
    def mark_key_failed(self, api_key: str, reason: str = "Unknown"):
        """Mark an API key as failed."""
        self.failed_keys.add(api_key)
        logger.error(f"API key {api_key[:10]}... marked as failed: {reason}")
        
        # Update usage stats
        self.update_usage_stats(api_key, error=True)
    
    def get_available_keys(self) -> List[str]:
        """Get list of available (non-failed) API keys."""
        return [key for key in self.api_keys if key not in self.failed_keys]
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get detailed usage report for all API keys."""
        report = {
            'current_key_index': self.current_key_index,
            'current_model_index': self.current_model_index,
            'current_config': self.get_current_config(),
            'available_keys': len(self.get_available_keys()),
            'total_keys': len(self.api_keys),
            'failed_keys': len(self.failed_keys),
            'key_stats': {}
        }
        
        for key in self.api_keys:
            stats = self.key_usage_stats[key]
            report['key_stats'][key[:10] + '...'] = {
                'requests': stats['requests'],
                'tokens': stats['tokens'],
                'errors': stats['errors'],
                'quota_exceeded': stats['quota_exceeded'],
                'last_used': stats['last_used'].isoformat() if stats['last_used'] else None,
                'is_failed': key in self.failed_keys
            }
        
        return report
    
    async def generate_content_with_failover(
        self, 
        prompt: str, 
        max_retries: int = 3,
        **kwargs
    ) -> Optional[str]:
        """
        Generate content with automatic failover between API keys and models.
        """
        for attempt in range(max_retries):
            try:
                config = self.get_current_config()
                api_key = config['api_key']
                model_name = config['model']
                
                # Check quota limits
                if not self.check_quota_limits(api_key):
                    logger.warning(f"API key {api_key[:10]}... quota exceeded, switching...")
                    if not self.switch_to_next_key():
                        logger.error("No available API keys")
                        return None
                    continue
                
                # Configure Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)
                
                # Generate content
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    },
                    **kwargs
                )
                
                if response and response.text:
                    # Update usage stats
                    tokens_used = len(prompt.split()) + len(response.text.split())
                    self.update_usage_stats(api_key, tokens_used)
                    
                    logger.info(f"Successfully generated content using {model_name} with key {api_key[:10]}...")
                    return response.text
                else:
                    logger.warning(f"Empty response from {model_name}")
                    if attempt < max_retries - 1:
                        self.switch_to_next_model()
                        continue
                
            except Exception as e:
                error_msg = str(e).lower()
                logger.error(f"Error generating content (attempt {attempt + 1}): {e}")
                
                # Check for specific error types
                if 'quota' in error_msg or 'limit' in error_msg:
                    self.mark_key_failed(api_key, f"Quota exceeded: {e}")
                    if not self.switch_to_next_key():
                        logger.error("No available API keys after quota error")
                        return None
                elif 'api_key' in error_msg or 'authentication' in error_msg:
                    self.mark_key_failed(api_key, f"Authentication error: {e}")
                    if not self.switch_to_next_key():
                        logger.error("No available API keys after auth error")
                        return None
                elif 'model' in error_msg:
                    logger.warning(f"Model error, switching model: {e}")
                    if not self.switch_to_next_model():
                        logger.error("No available models")
                        return None
                else:
                    # Generic error, try next key
                    if not self.switch_to_next_key():
                        logger.error("No available API keys after generic error")
                        return None
                
                # Wait before retry
                await asyncio.sleep(1)
        
        logger.error(f"Failed to generate content after {max_retries} attempts")
        return None
    
    async def generate_embedding_with_failover(
        self, 
        text: str, 
        max_retries: int = 3
    ) -> Optional[List[float]]:
        """
        Generate embedding with automatic failover between API keys.
        """
        for attempt in range(max_retries):
            try:
                config = self.get_current_config()
                api_key = config['api_key']
                
                # Check quota limits
                if not self.check_quota_limits(api_key):
                    logger.warning(f"API key {api_key[:10]}... quota exceeded, switching...")
                    if not self.switch_to_next_key():
                        logger.error("No available API keys")
                        return None
                    continue
                
                # Configure Gemini
                genai.configure(api_key=api_key)
                
                # Generate embedding
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
                
                if result and result['embedding']:
                    # Update usage stats
                    tokens_used = len(text.split())
                    self.update_usage_stats(api_key, tokens_used)
                    
                    logger.info(f"Successfully generated embedding with key {api_key[:10]}...")
                    return result['embedding']
                
            except Exception as e:
                error_msg = str(e).lower()
                logger.error(f"Error generating embedding (attempt {attempt + 1}): {e}")
                
                # Check for specific error types
                if 'quota' in error_msg or 'limit' in error_msg:
                    self.mark_key_failed(api_key, f"Quota exceeded: {e}")
                    if not self.switch_to_next_key():
                        logger.error("No available API keys after quota error")
                        return None
                elif 'api_key' in error_msg or 'authentication' in error_msg:
                    self.mark_key_failed(api_key, f"Authentication error: {e}")
                    if not self.switch_to_next_key():
                        logger.error("No available API keys after auth error")
                        return None
                else:
                    # Generic error, try next key
                    if not self.switch_to_next_key():
                        logger.error("No available API keys after generic error")
                        return None
                
                # Wait before retry
                await asyncio.sleep(1)
        
        logger.error(f"Failed to generate embedding after {max_retries} attempts")
        return None

# Global instance
_gemini_manager = None

def get_gemini_manager() -> GeminiAPIManager:
    """Get the global Gemini API manager instance."""
    global _gemini_manager
    if _gemini_manager is None:
        _gemini_manager = GeminiAPIManager()
    return _gemini_manager
