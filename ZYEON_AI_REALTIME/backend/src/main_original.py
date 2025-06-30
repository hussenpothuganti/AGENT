import os
import sys
import threading
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import openai
from pymongo import MongoClient
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'zyeon_ai_secret_key_2024')

# Enable CORS for all routes
CORS(app, cors_allowed_origins="*")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize MongoDB
try:
    mongo_client = MongoClient(os.getenv('MONGODB_URI'))
    db = mongo_client.zyeon_ai
    conversations_collection = db.conversations
    logger.info("MongoDB connected successfully")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    conversations_collection = None

# Initialize Text-to-Speech (with error handling)
tts_engine = None
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)
    tts_engine.setProperty('volume', 0.9)
    logger.info("Text-to-speech initialized successfully")
except Exception as e:
    logger.warning(f"Text-to-speech initialization failed: {e}")
    logger.info("TTS functionality will be disabled")

# Initialize Speech Recognition (with error handling)
recognizer = None
microphone = None
try:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    logger.info("Speech recognition initialized successfully")
except Exception as e:
    logger.warning(f"Speech recognition initialization failed: {e}")
    logger.info("Voice input functionality will be disabled")

# Global variables for voice processing
is_listening = False
voice_thread = None

class ZyeonAI:
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """You are ZYEON, an advanced AI assistant with a futuristic personality. 
        You are helpful, intelligent, and slightly mysterious. Keep responses concise but informative.
        You have access to real-time capabilities and can process voice commands.
        Always maintain a professional yet engaging tone."""

    def get_ai_response(self, user_input, conversation_id=None):
        """Get response from OpenAI GPT-3.5-Turbo"""
        try:
            # Check if OpenAI API key is set
            if not openai.api_key:
                return "I apologize, but my AI capabilities are not configured. Please set up the OpenAI API key."
            
            # Prepare conversation history for context
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add recent conversation history for context
            for msg in self.conversation_history[-10:]:  # Last 10 messages for context
                messages.append(msg)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Save to MongoDB
            if conversations_collection:
                self.save_conversation(user_input, ai_response, conversation_id)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again."

    def save_conversation(self, user_message, ai_response, conversation_id=None):
        """Save conversation to MongoDB"""
        try:
            conversation_data = {
                "conversation_id": conversation_id or str(int(time.time())),
                "timestamp": datetime.utcnow(),
                "user_message": user_message,
                "ai_response": ai_response,
                "session_type": "voice" if is_listening else "text"
            }
            conversations_collection.insert_one(conversation_data)
            logger.info("Conversation saved to MongoDB")
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")

    def speak_text(self, text):
        """Convert text to speech"""
        try:
            if tts_engine:
                tts_engine.say(text)
                tts_engine.runAndWait()
            else:
                logger.warning("TTS engine not available")
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")

    def listen_for_voice(self):
        """Listen for voice input"""
        global is_listening
        if not recognizer or not microphone:
            logger.error("Voice recognition not available")
            return
            
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Listening for voice input...")
                
            while is_listening:
                try:
                    with microphone as source:
                        # Listen for audio with timeout
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Recognize speech
                    text = recognizer.recognize_google(audio)
                    logger.info(f"Voice input recognized: {text}")
                    
                    # Emit voice input to frontend
                    socketio.emit('voice_input_received', {'text': text})
                    
                    # Process the voice input
                    response = self.get_ai_response(text)
                    
                    # Emit AI response to frontend
                    socketio.emit('ai_response', {
                        'text': response,
                        'timestamp': datetime.now().isoformat(),
                        'type': 'voice'
                    })
                    
                    # Speak the response
                    threading.Thread(target=self.speak_text, args=(response,)).start()
                    
                except sr.WaitTimeoutError:
                    pass  # Continue listening
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error in voice listening: {e}")
        finally:
            is_listening = False

# Initialize ZYEON AI
zyeon = ZyeonAI()

# API Routes
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ZYEON AI Assistant",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "tts_available": tts_engine is not None,
            "voice_recognition_available": recognizer is not None and microphone is not None,
            "mongodb_available": conversations_collection is not None,
            "openai_configured": bool(openai.api_key)
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle text chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get AI response
        ai_response = zyeon.get_ai_response(user_message, conversation_id)
        
        return jsonify({
            "response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "type": "text"
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/conversations')
def get_conversations():
    """Get conversation history"""
    try:
        if not conversations_collection:
            return jsonify({"conversations": []})
        
        conversations = list(conversations_collection.find(
            {},
            {"_id": 0}
        ).sort("timestamp", -1).limit(50))
        
        return jsonify({"conversations": conversations})
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/voice/start', methods=['POST'])
def start_voice_listening():
    """Start voice listening"""
    global is_listening, voice_thread
    
    if not recognizer or not microphone:
        return jsonify({"error": "Voice recognition not available"}), 400
    
    try:
        if not is_listening:
            is_listening = True
            voice_thread = threading.Thread(target=zyeon.listen_for_voice)
            voice_thread.daemon = True
            voice_thread.start()
            
            return jsonify({
                "status": "Voice listening started",
                "listening": True
            })
        else:
            return jsonify({
                "status": "Already listening",
                "listening": True
            })
            
    except Exception as e:
        logger.error(f"Error starting voice listening: {e}")
        return jsonify({"error": "Failed to start voice listening"}), 500

@app.route('/api/voice/stop', methods=['POST'])
def stop_voice_listening():
    """Stop voice listening"""
    global is_listening
    
    try:
        is_listening = False
        
        return jsonify({
            "status": "Voice listening stopped",
            "listening": False
        })
        
    except Exception as e:
        logger.error(f"Error stopping voice listening: {e}")
        return jsonify({"error": "Failed to stop voice listening"}), 500

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Speak given text"""
    try:
        if not tts_engine:
            return jsonify({"error": "Text-to-speech not available"}), 400
            
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Speak in a separate thread to avoid blocking
        threading.Thread(target=zyeon.speak_text, args=(text,)).start()
        
        return jsonify({
            "status": "Speaking text",
            "text": text
        })
        
    except Exception as e:
        logger.error(f"Error in speak endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('connected', {'status': 'Connected to ZYEON AI'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")

@socketio.on('send_message')
def handle_message(data):
    """Handle real-time messages"""
    try:
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if user_message:
            # Get AI response
            ai_response = zyeon.get_ai_response(user_message, conversation_id)
            
            # Emit response back to client
            emit('ai_response', {
                'text': ai_response,
                'timestamp': datetime.now().isoformat(),
                'type': 'realtime'
            })
            
    except Exception as e:
        logger.error(f"Error handling socket message: {e}")
        emit('error', {'message': 'Error processing message'})

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React frontend"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    logger.info("Starting ZYEON AI Assistant...")
    logger.info(f"MongoDB URI: {os.getenv('MONGODB_URI')[:50]}...")
    logger.info(f"OpenAI API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not Set'}")
    logger.info(f"TTS Available: {tts_engine is not None}")
    logger.info(f"Voice Recognition Available: {recognizer is not None and microphone is not None}")
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)

