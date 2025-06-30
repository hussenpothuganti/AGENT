import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Mic, MicOff, Send, Volume2, VolumeX, Zap, Brain, MessageCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import io from 'socket.io-client'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [conversationId] = useState(() => `conv_${Date.now()}`)
  const [isLoading, setIsLoading] = useState(false)
  
  const socketRef = useRef(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Initialize Socket.IO connection
  useEffect(() => {
    const socket = io('/', {
      transports: ['websocket', 'polling']
    })
    
    socketRef.current = socket

    socket.on('connect', () => {
      setIsConnected(true)
      console.log('Connected to ZYEON AI')
    })

    socket.on('disconnect', () => {
      setIsConnected(false)
      console.log('Disconnected from ZYEON AI')
    })

    socket.on('connected', (data) => {
      console.log('Server connection confirmed:', data)
    })

    socket.on('ai_response', (data) => {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: data.text,
        sender: 'ai',
        timestamp: data.timestamp,
        type: data.type
      }])
      setIsLoading(false)
    })

    socket.on('voice_input_received', (data) => {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: data.text,
        sender: 'user',
        timestamp: new Date().toISOString(),
        type: 'voice'
      }])
    })

    socket.on('error', (data) => {
      console.error('Socket error:', data)
      setIsLoading(false)
    })

    return () => {
      socket.disconnect()
    }
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Add welcome message
  useEffect(() => {
    setMessages([{
      id: 0,
      text: "Hello! I'm ZYEON, your advanced AI assistant. I can process both text and voice commands. How can I help you today?",
      sender: 'ai',
      timestamp: new Date().toISOString(),
      type: 'system'
    }])
  }, [])

  const sendMessage = async (message = inputMessage) => {
    if (!message.trim()) return

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date().toISOString(),
      type: 'text'
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Send via Socket.IO for real-time response
      if (socketRef.current && isConnected) {
        socketRef.current.emit('send_message', {
          message: message,
          conversation_id: conversationId
        })
      } else {
        // Fallback to REST API
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: message,
            conversation_id: conversationId
          }),
        })

        if (response.ok) {
          const data = await response.json()
          setMessages(prev => [...prev, {
            id: Date.now() + 1,
            text: data.response,
            sender: 'ai',
            timestamp: data.timestamp,
            type: data.type
          }])
        } else {
          throw new Error('Failed to get response')
        }
        setIsLoading(false)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: "I apologize, but I'm experiencing technical difficulties. Please try again.",
        sender: 'ai',
        timestamp: new Date().toISOString(),
        type: 'error'
      }])
      setIsLoading(false)
    }
  }

  const toggleVoiceListening = async () => {
    try {
      if (isListening) {
        const response = await fetch('/api/voice/stop', {
          method: 'POST',
        })
        if (response.ok) {
          setIsListening(false)
        }
      } else {
        const response = await fetch('/api/voice/start', {
          method: 'POST',
        })
        if (response.ok) {
          setIsListening(true)
        }
      }
    } catch (error) {
      console.error('Error toggling voice:', error)
    }
  }

  const speakText = async (text) => {
    try {
      setIsSpeaking(true)
      const response = await fetch('/api/speak', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      })
      
      if (response.ok) {
        // Simulate speaking duration
        setTimeout(() => setIsSpeaking(false), text.length * 50)
      } else {
        setIsSpeaking(false)
      }
    } catch (error) {
      console.error('Error speaking text:', error)
      setIsSpeaking(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 dark">
      {/* Header */}
      <motion.header 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="border-b border-purple-500/20 bg-black/20 backdrop-blur-lg"
      >
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="w-10 h-10 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-full flex items-center justify-center"
              >
                <Brain className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                  ZYEON AI
                </h1>
                <p className="text-sm text-purple-300">Advanced Voice Assistant</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant={isConnected ? "default" : "destructive"} className="animate-pulse">
                <Zap className="w-3 h-3 mr-1" />
                {isConnected ? 'Connected' : 'Disconnected'}
              </Badge>
              
              {isListening && (
                <Badge variant="secondary" className="bg-red-500/20 text-red-400 animate-pulse">
                  <Mic className="w-3 h-3 mr-1" />
                  Listening
                </Badge>
              )}
              
              {isSpeaking && (
                <Badge variant="secondary" className="bg-blue-500/20 text-blue-400 animate-pulse">
                  <Volume2 className="w-3 h-3 mr-1" />
                  Speaking
                </Badge>
              )}
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Chat Area */}
      <main className="container mx-auto px-4 py-6 max-w-4xl">
        <Card className="h-[calc(100vh-200px)] bg-black/40 border-purple-500/30 backdrop-blur-lg">
          <CardHeader className="border-b border-purple-500/20">
            <CardTitle className="flex items-center space-x-2 text-purple-300">
              <MessageCircle className="w-5 h-5" />
              <span>Conversation</span>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="p-0 h-full flex flex-col">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] ${
                      message.sender === 'user' 
                        ? 'bg-gradient-to-r from-purple-600 to-purple-700' 
                        : 'bg-gradient-to-r from-slate-700 to-slate-800'
                    } rounded-lg p-4 shadow-lg border ${
                      message.sender === 'user' 
                        ? 'border-purple-500/30' 
                        : 'border-slate-600/30'
                    }`}>
                      <div className="flex items-start space-x-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          message.sender === 'user' 
                            ? 'bg-purple-500' 
                            : 'bg-gradient-to-r from-cyan-500 to-purple-500'
                        }`}>
                          {message.sender === 'user' ? (
                            <span className="text-white text-sm font-bold">U</span>
                          ) : (
                            <Brain className="w-4 h-4 text-white" />
                          )}
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-sm font-medium text-white">
                              {message.sender === 'user' ? 'You' : 'ZYEON'}
                            </span>
                            <span className="text-xs text-gray-400">
                              {formatTimestamp(message.timestamp)}
                            </span>
                            {message.type === 'voice' && (
                              <Badge variant="outline" className="text-xs">
                                <Mic className="w-3 h-3 mr-1" />
                                Voice
                              </Badge>
                            )}
                          </div>
                          <p className="text-white leading-relaxed">{message.text}</p>
                          
                          {message.sender === 'ai' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => speakText(message.text)}
                              className="mt-2 text-purple-400 hover:text-purple-300 hover:bg-purple-500/10"
                              disabled={isSpeaking}
                            >
                              {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                              <span className="ml-1">Speak</span>
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-gradient-to-r from-slate-700 to-slate-800 rounded-lg p-4 border border-slate-600/30">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 flex items-center justify-center">
                        <Brain className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-purple-500/20 p-4">
              <div className="flex items-center space-x-3">
                <div className="flex-1 relative">
                  <Input
                    ref={inputRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message or use voice input..."
                    className="bg-slate-800/50 border-purple-500/30 text-white placeholder-gray-400 pr-12 focus:border-purple-400 focus:ring-purple-400"
                    disabled={isLoading}
                  />
                </div>
                
                <Button
                  onClick={toggleVoiceListening}
                  variant={isListening ? "destructive" : "secondary"}
                  size="icon"
                  className={`${
                    isListening 
                      ? 'bg-red-600 hover:bg-red-700 animate-pulse' 
                      : 'bg-purple-600 hover:bg-purple-700'
                  } transition-all duration-200`}
                >
                  {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </Button>
                
                <Button
                  onClick={() => sendMessage()}
                  disabled={!inputMessage.trim() || isLoading}
                  className="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 transition-all duration-200"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="mt-2 text-xs text-gray-400 text-center">
                Press Enter to send • Click mic for voice input • ZYEON is listening...
              </div>
            </div>
          </CardContent>
        </Card>
      </main>

      {/* Floating Status Indicators */}
      <AnimatePresence>
        {isListening && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="fixed bottom-6 right-6 w-16 h-16 bg-red-500 rounded-full flex items-center justify-center shadow-lg animate-pulse"
          >
            <Mic className="w-8 h-8 text-white" />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default App

