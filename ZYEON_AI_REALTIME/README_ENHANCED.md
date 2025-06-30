# ZYEON AI Enhanced - Real-time Voice Assistant

A complete, production-ready real-time voice-powered AI assistant with React frontend, Flask backend, MongoDB integration, OpenAI GPT integration, and comprehensive voice I/O capabilities.

## 🚀 Features

### Core Features
- **Real-time Chat Interface**: Beautiful futuristic dark mode design with real-time messaging
- **Voice Input**: Advanced speech recognition for hands-free interaction
- **Text-to-Speech**: AI responses with natural voice synthesis
- **OpenAI Integration**: Powered by GPT models for intelligent responses
- **MongoDB Storage**: Comprehensive conversation history and user management
- **Socket.IO**: Real-time bidirectional communication with auto-reconnection
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### Enhanced Features (v2.0)
- **User Session Management**: Persistent user sessions with unique IDs
- **Conversation Threading**: Organized conversation history with context
- **Advanced Analytics**: Usage statistics and conversation insights
- **Voice Settings**: Customizable speech rate, volume, and recognition settings
- **Error Handling**: Robust error handling with graceful degradation
- **Health Monitoring**: Comprehensive health checks and status monitoring
- **Rate Limiting**: Built-in API rate limiting for stability
- **Logging System**: Detailed logging with rotation and error tracking
- **Docker Support**: Complete containerization for easy deployment
- **Production Ready**: Optimized for production deployment

## 🛠️ Tech Stack

### Frontend
- **React 19**: Latest React with hooks and modern features
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/UI**: High-quality UI components
- **Framer Motion**: Smooth animations and transitions
- **Socket.IO Client**: Real-time communication
- **Lucide Icons**: Beautiful icon library

### Backend
- **Flask**: Lightweight Python web framework
- **Flask-SocketIO**: Real-time WebSocket communication
- **OpenAI API**: GPT integration for AI responses
- **MongoDB**: NoSQL database for data persistence
- **PyTTSx3**: Text-to-speech synthesis
- **SpeechRecognition**: Voice input processing
- **Python 3.11**: Latest Python features

### Infrastructure
- **Docker**: Containerization and deployment
- **Gunicorn**: Production WSGI server
- **MongoDB Atlas**: Cloud database (or local MongoDB)
- **Render/Heroku**: Cloud deployment platforms

## 📁 Project Structure

```
ZYEON_AI_REALTIME/
├── backend/
│   ├── src/
│   │   ├── main.py                 # Enhanced main Flask application
│   │   ├── models/
│   │   │   ├── conversation.py     # MongoDB conversation model
│   │   │   └── user.py            # User management model
│   │   ├── services/
│   │   │   ├── ai_service.py      # Enhanced OpenAI service
│   │   │   └── voice_service.py   # Advanced voice processing
│   │   ├── routes/
│   │   │   └── user.py           # User management routes
│   │   └── static/               # Built React frontend files
│   ├── logs/                     # Application logs
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Enhanced React application
│   │   ├── components/ui/       # Shadcn/UI components
│   │   ├── hooks/               # Custom React hooks
│   │   └── lib/                 # Utility functions
│   ├── dist/                    # Built frontend files
│   └── package.json             # Node.js dependencies
├── .env                         # Environment variables
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Docker build configuration
├── deploy.sh                    # Enhanced deployment script
├── render.yaml                  # Render deployment config
└── README_ENHANCED.md           # This file
```

## 🔧 Quick Start

### Prerequisites

- **Node.js 18+**
- **Python 3.11+**
- **Git**
- **OpenAI API Key** (from [OpenAI Platform](https://platform.openai.com/api-keys))
- **MongoDB** (local or [MongoDB Atlas](https://www.mongodb.com/atlas))

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd ZYEON_AI_REALTIME

# Make deployment script executable
chmod +x deploy.sh
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```env
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
PORT=5000
```

### 3. Development Deployment

```bash
# Install dependencies, build, and start development server
./deploy.sh dev
```

### 4. Production Deployment

```bash
# Deploy for production
./deploy.sh prod
```

### 5. Docker Deployment

```bash
# Deploy with Docker
./deploy.sh docker
```

## 🚀 Deployment Options

### Option 1: Local Development

```bash
# Install frontend dependencies
cd frontend
npm install --legacy-peer-deps
npm run build

# Install backend dependencies
cd ../backend
pip install -r requirements.txt

# Start the application
python src/main.py
```

### Option 2: Production Server

```bash
# Use the deployment script
./deploy.sh prod

# Or manually with Gunicorn
pip install gunicorn
cd backend
gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class eventlet src.main:app
```

### Option 3: Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t zyeon-ai-enhanced .
docker run -d -p 5000:5000 --env-file .env zyeon-ai-enhanced
```

### Option 4: Cloud Deployment (Render)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Set environment variables in Render dashboard
   - Deploy!

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT integration | Yes | - |
| `MONGODB_URI` | MongoDB connection string | Yes | - |
| `FLASK_ENV` | Flask environment (development/production) | No | development |
| `SECRET_KEY` | Flask secret key for sessions | No | auto-generated |
| `PORT` | Server port | No | 5000 |

### Voice Settings

The application supports customizable voice settings:

- **Speech Rate**: 50-300 WPM (default: 150)
- **Speech Volume**: 0-100% (default: 90%)
- **Recognition Timeout**: 1-10 seconds (default: 5)
- **Phrase Timeout**: 1-5 seconds (default: 2)

### MongoDB Configuration

The application automatically creates the following collections:
- `conversations`: Chat history and AI responses
- `users`: User profiles and session data
- `sessions`: Active user sessions

Indexes are automatically created for optimal performance.

## 🎯 Usage

### Text Chat
1. Type your message in the input field
2. Press Enter or click the send button
3. ZYEON will respond in real-time with context awareness

### Voice Input
1. Click the microphone button to start listening
2. Speak your message clearly
3. ZYEON will process and respond with voice output
4. Click the microphone button again to stop listening

### Voice Output
1. Click the "Speak" button on any AI response
2. ZYEON will read the message aloud
3. Adjust voice settings in the settings panel

### Analytics
- View conversation statistics
- Monitor voice vs text usage
- Track session duration
- Export conversation history

## 🔧 Advanced Features

### Real-time Communication
- WebSocket-based real-time messaging
- Automatic reconnection on connection loss
- Typing indicators and status updates
- Message delivery confirmation

### Voice Processing
- Automatic noise adjustment
- Google Speech Recognition integration
- Cross-platform TTS support
- Voice activity detection

### Database Integration
- Automatic conversation logging
- User session management
- Conversation threading
- Data export capabilities

### Error Handling
- Graceful degradation on service failures
- Comprehensive error logging
- User-friendly error messages
- Automatic retry mechanisms

## 🐛 Troubleshooting

### Common Issues

#### Audio Issues (Local Development)
- **Linux**: Install audio dependencies:
  ```bash
  sudo apt-get install -y pulseaudio alsa-utils portaudio19-dev
  ```
- **macOS**: Audio should work out of the box
- **Windows**: Install PyAudio manually if needed

#### OpenAI API Issues
- Verify API key is correct and has sufficient credits
- Check API usage limits in OpenAI dashboard
- Ensure billing is set up for API access

#### MongoDB Connection
- Verify MongoDB URI is correct
- Check network connectivity
- Ensure IP whitelist includes your deployment IP
- For MongoDB Atlas, check cluster status

#### Frontend Build Issues
- Use `--legacy-peer-deps` flag with npm install
- Clear node_modules and reinstall if needed
- Check Node.js version compatibility

#### Voice Recognition Issues
- Ensure microphone permissions are granted
- Check system audio settings
- Verify microphone is working in other applications

### Logs and Debugging

Application logs are stored in:
- `backend/logs/zyeon_ai.log` - General application logs
- `backend/logs/zyeon_ai_errors.log` - Error logs only

Enable debug mode:
```bash
export FLASK_ENV=development
```

## 📝 API Documentation

### Health Check
```
GET /api/health
```
Returns comprehensive system status including:
- Service health
- Feature availability
- Connected clients
- Database status
- AI service status

### Chat API
```
POST /api/chat
Content-Type: application/json

{
  "message": "Hello ZYEON",
  "conversation_id": "optional_conversation_id",
  "context_type": "default"
}
```

### Voice API
```
POST /api/voice/start    # Start voice listening
POST /api/voice/stop     # Stop voice listening
POST /api/speak          # Text-to-speech
GET /api/voice/settings  # Get voice settings
POST /api/voice/settings # Update voice settings
```

### Conversation API
```
GET /api/conversations   # Get conversation history
GET /api/analytics      # Get usage analytics
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/React code
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure Docker builds work correctly

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT API
- MongoDB for database services
- React and Flask communities
- Shadcn/UI for beautiful components
- All contributors and testers

## 📞 Support

For issues and questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the [API documentation](#api-documentation)
3. Check application logs for errors
4. Verify environment configuration
5. Create an issue on GitHub with detailed information

## 🔄 Version History

### v2.0.0 (Enhanced)
- Complete rewrite with enhanced features
- Advanced user session management
- Comprehensive analytics and monitoring
- Docker support and production optimization
- Enhanced voice processing
- Improved error handling and logging

### v1.0.0 (Original)
- Basic chat functionality
- Simple voice input/output
- MongoDB integration
- React frontend with Flask backend

---

**ZYEON AI Enhanced** - Your Advanced Voice Assistant 🤖✨

Built with ❤️ for the future of AI interaction

