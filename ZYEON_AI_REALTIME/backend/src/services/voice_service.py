"""
Enhanced Voice Service for ZYEON AI
Provides robust speech recognition and text-to-speech capabilities
"""

import threading
import time
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import queue
import json

logger = logging.getLogger(__name__)

class VoiceService:
    """Enhanced voice service with improved error handling and features"""
    
    def __init__(self):
        self.is_listening = False
        self.is_speaking = False
        self.voice_thread = None
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.audio_queue = queue.Queue()
        
        # Voice settings
        self.settings = {
            "speech_rate": 150,
            "speech_volume": 0.9,
            "recognition_timeout": 5,
            "phrase_timeout": 2,
            "ambient_noise_duration": 1,
            "energy_threshold": 300,
            "dynamic_energy_threshold": True
        }
        
        # Initialize components
        self._initialize_tts()
        self._initialize_speech_recognition()
        
        # Callbacks
        self.on_speech_recognized = None
        self.on_speech_error = None
        self.on_listening_started = None
        self.on_listening_stopped = None
        self.on_speaking_started = None
        self.on_speaking_finished = None
    
    def _initialize_tts(self):
        """Initialize text-to-speech engine"""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            self.tts_engine.setProperty('rate', self.settings['speech_rate'])
            self.tts_engine.setProperty('volume', self.settings['speech_volume'])
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            logger.info("Text-to-speech initialized successfully")
            
        except Exception as e:
            logger.warning(f"Text-to-speech initialization failed: {e}")
            self.tts_engine = None
    
    def _initialize_speech_recognition(self):
        """Initialize speech recognition"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Configure recognition settings
            self.recognizer.energy_threshold = self.settings['energy_threshold']
            self.recognizer.dynamic_energy_threshold = self.settings['dynamic_energy_threshold']
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(
                    source, 
                    duration=self.settings['ambient_noise_duration']
                )
            
            logger.info("Speech recognition initialized successfully")
            
        except Exception as e:
            logger.warning(f"Speech recognition initialization failed: {e}")
            self.recognizer = None
            self.microphone = None
    
    def set_callbacks(self, 
                     on_speech_recognized: Callable = None,
                     on_speech_error: Callable = None,
                     on_listening_started: Callable = None,
                     on_listening_stopped: Callable = None,
                     on_speaking_started: Callable = None,
                     on_speaking_finished: Callable = None):
        """Set callback functions for voice events"""
        self.on_speech_recognized = on_speech_recognized
        self.on_speech_error = on_speech_error
        self.on_listening_started = on_listening_started
        self.on_listening_stopped = on_listening_stopped
        self.on_speaking_started = on_speaking_started
        self.on_speaking_finished = on_speaking_finished
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update voice service settings"""
        self.settings.update(settings)
        
        # Apply TTS settings
        if self.tts_engine:
            if 'speech_rate' in settings:
                self.tts_engine.setProperty('rate', settings['speech_rate'])
            if 'speech_volume' in settings:
                self.tts_engine.setProperty('volume', settings['speech_volume'])
        
        # Apply speech recognition settings
        if self.recognizer:
            if 'energy_threshold' in settings:
                self.recognizer.energy_threshold = settings['energy_threshold']
            if 'dynamic_energy_threshold' in settings:
                self.recognizer.dynamic_energy_threshold = settings['dynamic_energy_threshold']
        
        logger.info(f"Voice settings updated: {settings}")
    
    def start_listening(self) -> bool:
        """Start listening for voice input"""
        if not self.recognizer or not self.microphone:
            logger.error("Speech recognition not available")
            return False
        
        if self.is_listening:
            logger.warning("Already listening")
            return True
        
        try:
            self.is_listening = True
            self.voice_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.voice_thread.start()
            
            if self.on_listening_started:
                self.on_listening_started()
            
            logger.info("Voice listening started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting voice listening: {e}")
            self.is_listening = False
            return False
    
    def stop_listening(self) -> bool:
        """Stop listening for voice input"""
        try:
            self.is_listening = False
            
            if self.voice_thread and self.voice_thread.is_alive():
                self.voice_thread.join(timeout=2)
            
            if self.on_listening_stopped:
                self.on_listening_stopped()
            
            logger.info("Voice listening stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping voice listening: {e}")
            return False
    
    def _listen_loop(self):
        """Main listening loop"""
        logger.info("Starting voice recognition loop")
        
        try:
            while self.is_listening:
                try:
                    with self.microphone as source:
                        # Listen for audio with timeout
                        audio = self.recognizer.listen(
                            source, 
                            timeout=self.settings['recognition_timeout'],
                            phrase_time_limit=self.settings['phrase_timeout']
                        )
                    
                    # Process audio in background
                    threading.Thread(
                        target=self._process_audio, 
                        args=(audio,), 
                        daemon=True
                    ).start()
                    
                except Exception as e:
                    if self.is_listening:  # Only log if we're still supposed to be listening
                        logger.debug(f"Listening timeout or error: {e}")
                    
        except Exception as e:
            logger.error(f"Error in voice listening loop: {e}")
            if self.on_speech_error:
                self.on_speech_error(str(e))
        finally:
            self.is_listening = False
    
    def _process_audio(self, audio):
        """Process captured audio"""
        try:
            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Speech recognized: {text}")
            
            if self.on_speech_recognized:
                self.on_speech_recognized(text)
                
        except Exception as e:
            logger.warning(f"Speech recognition error: {e}")
            if self.on_speech_error:
                self.on_speech_error(str(e))
    
    def speak_text(self, text: str, interrupt_current: bool = False) -> bool:
        """Convert text to speech"""
        if not self.tts_engine:
            logger.warning("TTS engine not available")
            return False
        
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return False
        
        try:
            # Stop current speech if requested
            if interrupt_current and self.is_speaking:
                self.stop_speaking()
            
            # Start speaking in a separate thread
            speech_thread = threading.Thread(
                target=self._speak_text_thread, 
                args=(text.strip(),), 
                daemon=True
            )
            speech_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting text-to-speech: {e}")
            return False
    
    def _speak_text_thread(self, text: str):
        """Text-to-speech thread"""
        try:
            self.is_speaking = True
            
            if self.on_speaking_started:
                self.on_speaking_started(text)
            
            # Clean text for better speech
            clean_text = self._clean_text_for_speech(text)
            
            self.tts_engine.say(clean_text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
        finally:
            self.is_speaking = False
            if self.on_speaking_finished:
                self.on_speaking_finished()
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        # Remove markdown formatting
        import re
        
        # Remove markdown links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'`([^`]+)`', r'\1', text)         # Code
        
        # Remove special characters that don't speak well
        text = re.sub(r'[#\*\-\+\=\>\<\|\[\]{}]', ' ', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def stop_speaking(self) -> bool:
        """Stop current speech"""
        try:
            if self.tts_engine and self.is_speaking:
                self.tts_engine.stop()
                self.is_speaking = False
                logger.info("Speech stopped")
                return True
            return False
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
            return False
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        try:
            if not self.tts_engine:
                return []
            
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_info = {
                    "id": voice.id,
                    "name": voice.name,
                    "languages": getattr(voice, 'languages', []),
                    "gender": getattr(voice, 'gender', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """Set TTS voice by ID"""
        try:
            if not self.tts_engine:
                return False
            
            self.tts_engine.setProperty('voice', voice_id)
            logger.info(f"Voice set to: {voice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get current voice service status"""
        return {
            "tts_available": self.tts_engine is not None,
            "speech_recognition_available": self.recognizer is not None and self.microphone is not None,
            "is_listening": self.is_listening,
            "is_speaking": self.is_speaking,
            "settings": self.settings.copy(),
            "timestamp": datetime.now().isoformat()
        }
    
    def test_voice_capabilities(self) -> Dict:
        """Test voice capabilities"""
        results = {
            "tts_test": False,
            "speech_recognition_test": False,
            "microphone_test": False,
            "errors": []
        }
        
        # Test TTS
        try:
            if self.tts_engine:
                self.tts_engine.say("Testing text to speech")
                self.tts_engine.runAndWait()
                results["tts_test"] = True
        except Exception as e:
            results["errors"].append(f"TTS test failed: {e}")
        
        # Test microphone
        try:
            if self.microphone:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                results["microphone_test"] = True
        except Exception as e:
            results["errors"].append(f"Microphone test failed: {e}")
        
        # Test speech recognition
        try:
            if self.recognizer and self.microphone:
                results["speech_recognition_test"] = True
        except Exception as e:
            results["errors"].append(f"Speech recognition test failed: {e}")
        
        return results

