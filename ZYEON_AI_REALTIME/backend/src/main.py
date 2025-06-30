"""
Enhanced ZYEON AI Main Application
Production-ready Flask application with comprehensive features
"""

import os
import sys
import threading
import time
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import json

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, disconnect
from pymongo import MongoClient
import openai

# Import our enhanced services
from models.conversation import ConversationModel
from services.ai_service import ZyeonAIService
from services.voice_service import VoiceService

# Configure logging
def setup_logging():
    """Setup comprehensive logging"""
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'zyeon_ai.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'zyeon_ai_errors.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

setup_logging()
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'zyeon_ai_secret_key_2024')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# Enable CORS for all routes
CORS(app, cors_allowed_origins="*", supports_credentials=True)

# Initialize SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

# Global services
conversation_model = None
ai_service = None
voice_service = None
connected_clients = {}

def initialize_services():
    """Initialize all services"""
    global conversation_model, ai_service, voice_service
    
    try:
        # Initialize MongoDB
        mongo_uri = os.getenv('MONGODB_URI')
        if mongo_uri:
            mongo_client = MongoClient(mongo_uri)
            conversation_model = ConversationModel(mongo_client)
            logger.info("MongoDB connected successfully")
        else:
            logger.warning("MongoDB URI not provided")
        
        # Initialize AI Service
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            ai_service = ZyeonAIService(openai_key)
            logger.info("AI Service initialized successfully")
        else:
            logger.warning("OpenAI API key not provided")
        
        # Initialize Voice Service
        voice_service = VoiceService()
        
        # Set up voice callbacks
        voice_service.set_callbacks(
            on_speech_recognized=handle_voice_input,
            on_speech_error=handle_voice_error,
            on_listening_started=lambda: socketio.emit('voice_status', {'listening': True}),
            on_listening_stopped=lambda: socketio.emit('voice_status', {'listening': False}),
            on_speaking_started=lambda text: socketio.emit('speaking_status', {'speaking': True, 'text': text}),
            on_speaking_finished=lambda: socketio.emit('speaking_status', {'speaking': False})
        )
        
        logger.info("Voice Service initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing services: {e}")

def handle_voice_input(text):
    """Handle voice input from voice service"""
    try:
        # Emit voice input to all connected clients
        socketio.emit('voice_input_received', {'text': text})
        
        # Process with AI
        if ai_service:
            user_id = "voice_user"  # In production, get from session
            conversation_history = []
            
            if conversation_model:
                conversation_history = conversation_model.get_conversation_history(
                    user_id=user_id, limit=10
                )
            
            ai_response, metadata = ai_service.get_ai_response(
                text, 
                conversation_history, 
                context_type="voice"
            )
            
            # Save conversation
            if conversation_model:
                conversation_model.create_conversation(
                    user_message=text,
                    ai_response=ai_response,
                    user_id=user_id,
                    message_type="voice",
                    metadata=metadata
                )
            
            # Emit AI response
            socketio.emit('ai_response', {
                'text': ai_response,
                'timestamp': datetime.now().isoformat(),
                'type': 'voice',
                'metadata': metadata
            })
            
            # Speak the response
            if voice_service:
                voice_service.speak_text(ai_response)
        
    except Exception as e:
        logger.error(f"Error handling voice input: {e}")

def handle_voice_error(error):
    """Handle voice recognition errors"""
    logger.warning(f"Voice recognition error: {error}")
    socketio.emit('voice_error', {'error': error})

# Utility functions
def get_user_id():
    """Get or create user ID from session"""
    if 'user_id' not in session:
        session['user_id'] = f"user_{uuid.uuid4().hex[:8]}"
    return session['user_id']

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = f"session_{uuid.uuid4().hex[:8]}"
    return session['session_id']

# API Routes
@app.route('/api/health')
def health_check():
    """Comprehensive health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "service": "ZYEON AI Assistant Enhanced",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - app.start_time if hasattr(app, 'start_time') else 0,
            "features": {
                "mongodb_available": conversation_model is not None,
                "ai_service_available": ai_service is not None,
                "voice_service_available": voice_service is not None,
                "tts_available": voice_service.tts_engine is not None if voice_service else False,
                "speech_recognition_available": voice_service.recognizer is not None if voice_service else False,
                "openai_configured": bool(os.getenv('OPENAI_API_KEY'))
            },
            "connected_clients": len(connected_clients),
            "environment": os.getenv('FLASK_ENV', 'development')
        }
        
        # Add AI service health if available
        if ai_service:
            ai_health = ai_service.health_check()
            health_status["ai_service"] = ai_health
        
        # Add voice service status if available
        if voice_service:
            voice_status = voice_service.get_status()
            health_status["voice_service"] = voice_status
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with full conversation management"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        context_type = data.get('context_type', 'default')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        if not ai_service:
            return jsonify({"error": "AI service not available"}), 503
        
        # Get user info
        user_id = get_user_id()
        session_id = get_session_id()
        
        # Update user activity
        if conversation_model:
            conversation_model.update_user_activity(user_id)
        
        # Get conversation history for context
        conversation_history = []
        if conversation_model:
            conversation_history = conversation_model.get_conversation_history(
                user_id=user_id,
                conversation_id=conversation_id,
                limit=10
            )
        
        # Get AI response
        ai_response, metadata = ai_service.get_ai_response(
            user_message, 
            conversation_history, 
            context_type
        )
        
        # Save conversation
        if conversation_model:
            conversation_model.create_conversation(
                user_message=user_message,
                ai_response=ai_response,
                user_id=user_id,
                conversation_id=conversation_id,
                session_id=session_id,
                message_type="text",
                metadata=metadata
            )
        
        # Get suggested responses
        suggestions = []
        if ai_service and len(conversation_history) > 0:
            suggestions = ai_service.get_suggested_responses(conversation_history + [{
                "user_message": user_message,
                "ai_response": ai_response
            }])
        
        return jsonify({
            "response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "type": "text",
            "metadata": metadata,
            "suggestions": suggestions,
            "user_id": user_id,
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/conversations')
def get_conversations():
    """Get conversation history with filtering"""
    try:
        if not conversation_model:
            return jsonify({"conversations": [], "total": 0})
        
        # Get query parameters
        user_id = request.args.get('user_id', get_user_id())
        conversation_id = request.args.get('conversation_id')
        session_id = request.args.get('session_id')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        conversations = conversation_model.get_conversation_history(
            user_id=user_id,
            conversation_id=conversation_id,
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        
        # Get stats
        stats = conversation_model.get_conversation_stats(user_id)
        
        return jsonify({
            "conversations": conversations,
            "total": len(conversations),
            "stats": stats,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(conversations) == limit
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/voice/start', methods=['POST'])
def start_voice_listening():
    """Start voice listening with enhanced error handling"""
    try:
        if not voice_service:
            return jsonify({"error": "Voice service not available"}), 503
        
        if not voice_service.recognizer or not voice_service.microphone:
            return jsonify({"error": "Voice recognition not available"}), 400
        
        success = voice_service.start_listening()
        
        if success:
            return jsonify({
                "status": "Voice listening started",
                "listening": True,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to start voice listening"}), 500
            
    except Exception as e:
        logger.error(f"Error starting voice listening: {e}")
        return jsonify({"error": "Failed to start voice listening"}), 500

@app.route('/api/voice/stop', methods=['POST'])
def stop_voice_listening():
    """Stop voice listening"""
    try:
        if not voice_service:
            return jsonify({"error": "Voice service not available"}), 503
        
        success = voice_service.stop_listening()
        
        return jsonify({
            "status": "Voice listening stopped",
            "listening": False,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error stopping voice listening: {e}")
        return jsonify({"error": "Failed to stop voice listening"}), 500

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Enhanced text-to-speech endpoint"""
    try:
        if not voice_service or not voice_service.tts_engine:
            return jsonify({"error": "Text-to-speech not available"}), 400
            
        data = request.get_json()
        text = data.get('text', '').strip()
        interrupt_current = data.get('interrupt', False)
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        success = voice_service.speak_text(text, interrupt_current)
        
        if success:
            return jsonify({
                "status": "Speaking text",
                "text": text,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to start speech"}), 500
        
    except Exception as e:
        logger.error(f"Error in speak endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/voice/settings', methods=['GET', 'POST'])
def voice_settings():
    """Get or update voice settings"""
    try:
        if not voice_service:
            return jsonify({"error": "Voice service not available"}), 503
        
        if request.method == 'GET':
            return jsonify({
                "settings": voice_service.settings,
                "available_voices": voice_service.get_available_voices(),
                "status": voice_service.get_status()
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            settings = data.get('settings', {})
            
            voice_service.update_settings(settings)
            
            return jsonify({
                "status": "Settings updated",
                "settings": voice_service.settings
            })
            
    except Exception as e:
        logger.error(f"Error in voice settings endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/analytics')
def get_analytics():
    """Get usage analytics"""
    try:
        if not conversation_model:
            return jsonify({"error": "Analytics not available"}), 503
        
        user_id = request.args.get('user_id', get_user_id())
        
        # Get comprehensive stats
        stats = conversation_model.get_conversation_stats(user_id)
        
        # Get recent activity (last 7 days)
        # This would require additional aggregation queries
        
        return jsonify({
            "stats": stats,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection with session management"""
    try:
        client_id = request.sid
        user_id = get_user_id()
        session_id = get_session_id()
        
        # Store client info
        connected_clients[client_id] = {
            "user_id": user_id,
            "session_id": session_id,
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        # Create session in database
        if conversation_model:
            conversation_model.create_session(
                user_id=user_id,
                session_id=session_id,
                metadata={"client_id": client_id}
            )
        
        logger.info(f"Client connected: {client_id} (User: {user_id})")
        
        emit('connected', {
            'status': 'Connected to ZYEON AI Enhanced',
            'user_id': user_id,
            'session_id': session_id,
            'features': {
                'voice_available': voice_service is not None,
                'ai_available': ai_service is not None,
                'history_available': conversation_model is not None
            }
        })
        
    except Exception as e:
        logger.error(f"Error handling connection: {e}")
        emit('error', {'message': 'Connection error'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        client_id = request.sid
        
        if client_id in connected_clients:
            client_info = connected_clients[client_id]
            
            # End session in database
            if conversation_model:
                conversation_model.end_session(client_info["session_id"])
            
            del connected_clients[client_id]
            logger.info(f"Client disconnected: {client_id}")
        
    except Exception as e:
        logger.error(f"Error handling disconnection: {e}")

@socketio.on('send_message')
def handle_socket_message(data):
    """Handle real-time messages via Socket.IO"""
    try:
        client_id = request.sid
        
        # Update client activity
        if client_id in connected_clients:
            connected_clients[client_id]["last_activity"] = datetime.now().isoformat()
        
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        context_type = data.get('context_type', 'realtime')
        
        if not user_message:
            emit('error', {'message': 'Message is required'})
            return
        
        if not ai_service:
            emit('error', {'message': 'AI service not available'})
            return
        
        # Get user info
        user_id = get_user_id()
        session_id = get_session_id()
        
        # Get conversation history
        conversation_history = []
        if conversation_model:
            conversation_history = conversation_model.get_conversation_history(
                user_id=user_id,
                conversation_id=conversation_id,
                limit=10
            )
        
        # Get AI response
        ai_response, metadata = ai_service.get_ai_response(
            user_message, 
            conversation_history, 
            context_type
        )
        
        # Save conversation
        if conversation_model:
            conversation_model.create_conversation(
                user_message=user_message,
                ai_response=ai_response,
                user_id=user_id,
                conversation_id=conversation_id,
                session_id=session_id,
                message_type="realtime",
                metadata=metadata
            )
        
        # Emit response
        emit('ai_response', {
            'text': ai_response,
            'timestamp': datetime.now().isoformat(),
            'type': 'realtime',
            'metadata': metadata
        })
        
    except Exception as e:
        logger.error(f"Error handling socket message: {e}")
        emit('error', {'message': 'Error processing message'})

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React frontend with better error handling"""
    try:
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
                return jsonify({
                    "error": "Frontend not built",
                    "message": "Please build the frontend first using 'npm run build'",
                    "api_available": True
                }), 404
                
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        return "Internal server error", 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Record start time
    app.start_time = time.time()
    
    # Initialize services
    logger.info("Initializing ZYEON AI Enhanced...")
    initialize_services()
    
    # Log configuration
    logger.info(f"MongoDB URI: {'Configured' if os.getenv('MONGODB_URI') else 'Not configured'}")
    logger.info(f"OpenAI API Key: {'Configured' if os.getenv('OPENAI_API_KEY') else 'Not configured'}")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    # Run application
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting ZYEON AI Enhanced on port {port}")
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        use_reloader=False  # Disable reloader to prevent double initialization
    )

