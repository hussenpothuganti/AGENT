"""
Enhanced AI Service for ZYEON AI
Provides robust OpenAI integration with conversation context and error handling
"""

import openai
from openai import OpenAI
import logging
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 60, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self) -> bool:
        """Check if a call can be made within rate limits"""
        now = time.time()
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record a new API call"""
        self.calls.append(time.time())

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

class ZyeonAIService:
    """Enhanced AI service with robust conversation management"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.rate_limiter = RateLimiter(max_calls=50, time_window=60)
        
        # Initialize OpenAI client (new format)
        self.client = OpenAI(api_key=api_key)
        
        # System prompts for different contexts
        self.system_prompts = {
            "default": """You are ZYEON, an advanced AI assistant with a futuristic personality. 
            You are helpful, intelligent, and slightly mysterious. Keep responses concise but informative.
            You have access to real-time capabilities and can process voice commands.
            Always maintain a professional yet engaging tone. You can remember context from previous messages.""",
            
            "voice": """You are ZYEON, an advanced AI assistant optimized for voice interaction.
            Keep responses brief and conversational, suitable for text-to-speech.
            Avoid using special characters, markdown, or complex formatting.
            Speak naturally as if having a conversation.""",
            
            "technical": """You are ZYEON, a technical AI assistant specializing in programming and technology.
            Provide detailed, accurate technical information. Use code examples when helpful.
            Explain complex concepts clearly and offer practical solutions."""
        }
        
        # Conversation context management
        self.max_context_messages = 20
        self.max_tokens_per_request = 1000
        
        logger.info(f"ZYEON AI Service initialized with model: {model}")
    
    def _get_system_prompt(self, context_type: str = "default") -> str:
        """Get appropriate system prompt based on context"""
        return self.system_prompts.get(context_type, self.system_prompts["default"])
    
    def _prepare_conversation_context(self, 
                                    conversation_history: List[Dict],
                                    context_type: str = "default") -> List[Dict]:
        """Prepare conversation context for OpenAI API"""
        messages = [{"role": "system", "content": self._get_system_prompt(context_type)}]
        
        # Add recent conversation history
        recent_history = conversation_history[-self.max_context_messages:]
        
        for msg in recent_history:
            if "user_message" in msg and "ai_response" in msg:
                messages.append({"role": "user", "content": msg["user_message"]})
                messages.append({"role": "assistant", "content": msg["ai_response"]})
        
        return messages
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_ai_response(self, 
                       user_input: str,
                       conversation_history: List[Dict] = None,
                       context_type: str = "default",
                       temperature: float = 0.7,
                       max_tokens: int = None) -> Tuple[str, Dict]:
        """
        Get AI response with enhanced error handling and context management
        
        Returns:
            Tuple of (response_text, metadata)
        """
        try:
            # Check rate limits
            if not self.rate_limiter.can_make_call():
                raise Exception("Rate limit exceeded. Please try again later.")
            
            # Validate input
            if not user_input or not user_input.strip():
                raise ValueError("User input cannot be empty")
            
            if not self.api_key:
                raise ValueError("OpenAI API key not configured")
            
            # Prepare conversation context
            conversation_history = conversation_history or []
            messages = self._prepare_conversation_context(conversation_history, context_type)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input.strip()})
            
            # Set token limits
            if max_tokens is None:
                max_tokens = self.max_tokens_per_request
            
            # Record API call for rate limiting
            self.rate_limiter.record_call()
            
            # Make API call (new format)
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            end_time = time.time()
            
            # Extract response
            ai_response = response.choices[0].message.content.strip()
            
            # Prepare metadata
            metadata = {
                "model": self.model,
                "context_type": context_type,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_time": round(end_time - start_time, 2),
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"AI response generated in {metadata['response_time']}s using {metadata['tokens_used']} tokens")
            
            return ai_response, metadata
            
        except Exception as e:
            logger.error(f"Error in AI service: {e}")
            
            # Handle specific OpenAI errors
            if "rate_limit" in str(e).lower():
                return "I'm experiencing high demand right now. Please try again in a moment.", {}
            elif "invalid" in str(e).lower():
                return "I'm having trouble processing your request. Please try rephrasing it.", {}
            elif "authentication" in str(e).lower():
                return "I'm experiencing authentication issues. Please contact support.", {}
            elif "connection" in str(e).lower():
                return "I'm having trouble connecting to my AI services. Please try again.", {}
            else:
                return "I apologize, but I'm experiencing technical difficulties. Please try again.", {}
    
    def get_conversation_summary(self, conversation_history: List[Dict]) -> str:
        """Generate a summary of the conversation"""
        try:
            if not conversation_history:
                return "No conversation to summarize."
            
            # Prepare messages for summarization
            messages = [
                {
                    "role": "system", 
                    "content": "Summarize the following conversation in 2-3 sentences. Focus on the main topics discussed and key outcomes."
                }
            ]
            
            # Add conversation history
            conversation_text = ""
            for msg in conversation_history[-10:]:  # Last 10 exchanges
                if "user_message" in msg and "ai_response" in msg:
                    conversation_text += f"User: {msg['user_message']}\nAI: {msg['ai_response']}\n\n"
            
            messages.append({"role": "user", "content": conversation_text})
            
            # Get summary
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return "Unable to generate conversation summary."
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of user input"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Analyze the sentiment of the following text. Respond with a JSON object containing 'sentiment' (positive/negative/neutral), 'confidence' (0-1), and 'emotions' (array of detected emotions)."
                },
                {"role": "user", "content": text}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=100,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": []
            }
    
    def get_suggested_responses(self, conversation_history: List[Dict]) -> List[str]:
        """Generate suggested follow-up responses"""
        try:
            if not conversation_history:
                return []
            
            last_ai_response = conversation_history[-1].get("ai_response", "") if conversation_history else ""
            
            messages = [
                {
                    "role": "system",
                    "content": "Based on the AI's last response, suggest 3 brief follow-up questions or responses the user might want to ask. Return as a JSON array of strings."
                },
                {"role": "user", "content": f"Last AI response: {last_ai_response}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,
                temperature=0.8
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            return suggestions[:3]  # Limit to 3 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
    
    def health_check(self) -> Dict:
        """Check the health of the AI service"""
        try:
            # Simple test request
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return {
                "status": "healthy",
                "model": self.model,
                "api_accessible": True,
                "rate_limit_remaining": self.rate_limiter.max_calls - len(self.rate_limiter.calls),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI service health check failed: {e}")
            return {
                "status": "unhealthy",
                "model": self.model,
                "api_accessible": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

