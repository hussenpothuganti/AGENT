# ZYEON AI - Real-time Voice Assistant

A complete, fully functional real-time voice-powered AI assistant with React frontend, Flask backend, MongoDB integration, OpenAI GPT-3.5-Turbo, and voice I/O capabilities.

## 🚀 Features

- **Real-time Chat Interface**: Beautiful futuristic dark mode design with real-time messaging
- **Voice Input**: Speech recognition for hands-free interaction
- **Text-to-Speech**: AI responses can be spoken aloud
- **OpenAI Integration**: Powered by GPT-3.5-Turbo for intelligent responses
- **MongoDB Storage**: Conversation history saved to cloud database
- **Socket.IO**: Real-time bidirectional communication
- **Responsive Design**: Works on desktop and mobile devices
- **Production Ready**: Configured for deployment on Render

## 🛠️ Tech Stack

- **Frontend**: React, Tailwind CSS, Socket.IO Client, Framer Motion
- **Backend**: Flask, Flask-SocketIO, OpenAI API, MongoDB
- **Voice**: SpeechRecognition, pyttsx3
- **Deployment**: Render (with render.yaml configuration)

## 📁 Project Structure

```
ZYEON_AI_REALTIME/
├── backend/
│   ├── src/
│   │   ├── main.py              # Main Flask application
│   │   └── static/              # Built React frontend files
│   ├── venv/                    # Python virtual environment
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   └── App.css             # Styles
│   ├── dist/                   # Built frontend files
│   └── package.json            # Node.js dependencies
├── .env                        # Environment variables
├── render.yaml                 # Render deployment config
└── README.md                   # This file
```

## 🔧 Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

1. **Clone and navigate to project**:
   ```bash
   cd ZYEON_AI_REALTIME/backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install system dependencies** (Linux/Ubuntu):
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential portaudio19-dev python3-dev espeak espeak-data libespeak1 libespeak-dev
   ```

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Build frontend**:
   ```bash
   npm run build
   # or
   pnpm run build
   ```

4. **Copy build to backend static folder**:
   ```bash
   cp -r dist/* ../backend/src/static/
   ```

### Environment Configuration

1. **Create `.env` file in project root**:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MONGODB_URI=mongodb+srv://personalagent2319:8bx6yULU9i5lURhu@cluster0.j3gddli.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   FLASK_ENV=development
   SECRET_KEY=zyeon_ai_secret_key_2024
   PORT=5000
   ```

2. **Get OpenAI API Key**:
   - Visit [OpenAI API](https://platform.openai.com/api-keys)
   - Create a new API key
   - Replace `your_openai_api_key_here` in `.env`

### Running Locally

1. **Start the Flask server**:
   ```bash
   cd backend
   source venv/bin/activate
   python src/main.py
   ```

2. **Open browser**:
   - Navigate to `http://localhost:5000`
   - You should see the ZYEON AI interface

## 🌐 Deployment on Render

### Method 1: Using render.yaml (Recommended)

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
   - Set environment variable `OPENAI_API_KEY`
   - Deploy!

### Method 2: Manual Deployment

1. **Create Web Service on Render**:
   - Environment: Python
   - Build Command:
     ```bash
     cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build && cp -r dist/* ../backend/src/static/
     ```
   - Start Command:
     ```bash
     cd backend && python src/main.py
     ```

2. **Set Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `MONGODB_URI`: (Already set in code)
   - `PORT`: 10000
   - `FLASK_ENV`: production

## 🎯 Usage

### Text Chat
1. Type your message in the input field
2. Press Enter or click the send button
3. ZYEON will respond in real-time

### Voice Input
1. Click the microphone button to start listening
2. Speak your message clearly
3. ZYEON will process and respond
4. Click the microphone button again to stop listening

### Text-to-Speech
1. Click the "Speak" button on any AI response
2. ZYEON will read the message aloud

## 🔧 Advanced Features

### Real-time Communication
- Uses Socket.IO for instant messaging
- Automatic reconnection on connection loss
- Real-time status indicators

### Voice Processing
- Automatic noise adjustment
- Google Speech Recognition
- Cross-platform TTS support

### Database Integration
- Automatic conversation logging
- MongoDB cloud storage
- Conversation history API

## 🐛 Troubleshooting

### Audio Issues (Local Development)
- **Linux**: Install audio dependencies:
  ```bash
  sudo apt-get install -y pulseaudio alsa-utils
  ```
- **macOS**: Audio should work out of the box
- **Windows**: Install PyAudio manually if needed

### OpenAI API Issues
- Verify API key is correct
- Check API usage limits
- Ensure billing is set up

### MongoDB Connection
- Verify MongoDB URI is correct
- Check network connectivity
- Ensure IP whitelist includes your deployment

## 📝 API Endpoints

- `GET /api/health` - Health check and feature status
- `POST /api/chat` - Send text message
- `GET /api/conversations` - Get conversation history
- `POST /api/voice/start` - Start voice listening
- `POST /api/voice/stop` - Stop voice listening
- `POST /api/speak` - Text-to-speech

## 🔒 Security

- Environment variables for sensitive data
- CORS configured for production
- MongoDB connection with authentication
- Secret key for session management

## 📄 License

This project is created for demonstration purposes. Please ensure you comply with OpenAI's usage policies and MongoDB's terms of service.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check server logs for errors
4. Verify environment configuration

---

**ZYEON AI** - Your Advanced Voice Assistant 🤖✨

