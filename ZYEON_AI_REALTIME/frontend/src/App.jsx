import { useState, useEffect, useRef, useCallback } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Mic, MicOff, Send, Volume2, VolumeX, Zap, Brain, MessageCircle, 
  Settings, History, User, Moon, Sun, Wifi, WifiOff, AlertCircle,
  Copy, Download, Trash2, RefreshCw, MoreVertical, ChevronDown
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import io from 'socket.io-client'
import './App.css'

// Enhanced Message Component
const MessageBubble = ({ message, onSpeak, isSpeaking, onCopy, onDelete }) => {
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} group`}
    >
      <div className={`max-w-[80%] ${
        message.sender === 'user' 
          ? 'bg-gradient-to-r from-purple-600 to-purple-700' 
          : 'bg-gradient-to-r from-slate-700 to-slate-800'
      } rounded-lg p-4 shadow-lg border ${
        message.sender === 'user' 
          ? 'border-purple-500/30' 
          : 'border-slate-600/30'
      } relative`}>
        <div className="flex items-start space-x-3">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            message.sender === 'user' 
              ? 'bg-purple-500' 
              : 'bg-gradient-to-r from-cyan-500 to-purple-500'
          }`}>
            {message.sender === 'user' ? (
              <User className="w-4 h-4 text-white" />
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
              {message.metadata?.tokens_used && (
                <Badge variant="outline" className="text-xs">
                  {message.metadata.tokens_used} tokens
                </Badge>
              )}
            </div>
            <p className="text-white leading-relaxed whitespace-pre-wrap">{message.text}</p>
            
            {/* Action buttons */}
            <div className="flex items-center space-x-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onCopy(message.text)}
                className="text-purple-400 hover:text-purple-300 hover:bg-purple-500/10 h-6 px-2"
              >
                <Copy className="w-3 h-3" />
              </Button>
              
              {message.sender === 'ai' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onSpeak(message.text)}
                  className="text-purple-400 hover:text-purple-300 hover:bg-purple-500/10 h-6 px-2"
                  disabled={isSpeaking}
                >
                  {isSpeaking ? <VolumeX className="w-3 h-3" /> : <Volume2 className="w-3 h-3" />}
                </Button>
              )}
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(message.id)}
                className="text-red-400 hover:text-red-300 hover:bg-red-500/10 h-6 px-2"
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// Settings Panel Component
const SettingsPanel = ({ settings, onSettingsChange, voiceSettings, onVoiceSettingsChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">General Settings</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm text-gray-300">Dark Mode</label>
            <Switch
              checked={settings.darkMode}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, darkMode: checked })}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <label className="text-sm text-gray-300">Auto-scroll</label>
            <Switch
              checked={settings.autoScroll}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, autoScroll: checked })}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <label className="text-sm text-gray-300">Sound Effects</label>
            <Switch
              checked={settings.soundEffects}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, soundEffects: checked })}
            />
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">Voice Settings</h3>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-300 block mb-2">Speech Rate</label>
            <Slider
              value={[voiceSettings.speech_rate]}
              onValueChange={([value]) => onVoiceSettingsChange({ ...voiceSettings, speech_rate: value })}
              min={50}
              max={300}
              step={10}
              className="w-full"
            />
            <span className="text-xs text-gray-400">{voiceSettings.speech_rate} WPM</span>
          </div>
          
          <div>
            <label className="text-sm text-gray-300 block mb-2">Speech Volume</label>
            <Slider
              value={[voiceSettings.speech_volume * 100]}
              onValueChange={([value]) => onVoiceSettingsChange({ ...voiceSettings, speech_volume: value / 100 })}
              min={0}
              max={100}
              step={5}
              className="w-full"
            />
            <span className="text-xs text-gray-400">{Math.round(voiceSettings.speech_volume * 100)}%</span>
          </div>
          
          <div>
            <label className="text-sm text-gray-300 block mb-2">Recognition Timeout</label>
            <Slider
              value={[voiceSettings.recognition_timeout]}
              onValueChange={([value]) => onVoiceSettingsChange({ ...voiceSettings, recognition_timeout: value })}
              min={1}
              max={10}
              step={1}
              className="w-full"
            />
            <span className="text-xs text-gray-400">{voiceSettings.recognition_timeout}s</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Main App Component
function App() {
  // State management
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [conversationId] = useState(() => `conv_${Date.now()}`)
  const [isLoading, setIsLoading] = useState(false)
  const [connectionError, setConnectionError] = useState(null)
  const [userId, setUserId] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  
  // Settings state
  const [settings, setSettings] = useState({
    darkMode: true,
    autoScroll: true,
    soundEffects: true,
    notifications: true
  })
  
  const [voiceSettings, setVoiceSettings] = useState({
    speech_rate: 150,
    speech_volume: 0.9,
    recognition_timeout: 5,
    phrase_timeout: 2
  })
  
  // UI state
  const [showSettings, setShowSettings] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [activeTab, setActiveTab] = useState('chat')
  
  // Refs
  const socketRef = useRef(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  // Socket connection with auto-reconnect
  const connectSocket = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect()
    }

    const socket = io('/', {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      forceNew: true
    })
    
    socketRef.current = socket

    socket.on('connect', () => {
      setIsConnected(true)
      setConnectionError(null)
      console.log('Connected to ZYEON AI Enhanced')
    })

    socket.on('disconnect', (reason) => {
      setIsConnected(false)
      console.log('Disconnected from ZYEON AI:', reason)
      
      // Auto-reconnect after 3 seconds
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, don't reconnect
        setConnectionError('Server disconnected')
      } else {
        setConnectionError('Connection lost, reconnecting...')
        reconnectTimeoutRef.current = setTimeout(() => {
          connectSocket()
        }, 3000)
      }
    })

    socket.on('connected', (data) => {
      console.log('Server connection confirmed:', data)
      setUserId(data.user_id)
      setSessionId(data.session_id)
    })

    socket.on('ai_response', (data) => {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: data.text,
        sender: 'ai',
        timestamp: data.timestamp,
        type: data.type,
        metadata: data.metadata
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

    socket.on('voice_status', (data) => {
      setIsListening(data.listening)
    })

    socket.on('speaking_status', (data) => {
      setIsSpeaking(data.speaking)
    })

    socket.on('voice_error', (data) => {
      console.error('Voice error:', data)
      setConnectionError(`Voice error: ${data.error}`)
    })

    socket.on('error', (data) => {
      console.error('Socket error:', data)
      setIsLoading(false)
      setConnectionError(data.message || 'Unknown error')
    })

    socket.on('connect_error', (error) => {
      console.error('Connection error:', error)
      setConnectionError('Failed to connect to server')
    })

  }, [])

  // Initialize connection
  useEffect(() => {
    connectSocket()
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [connectSocket])

  // Auto-scroll to bottom
  useEffect(() => {
    if (settings.autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, settings.autoScroll])

  // Add welcome message
  useEffect(() => {
    setMessages([{
      id: 0,
      text: "Hello! I'm ZYEON, your advanced AI assistant. I can process both text and voice commands with enhanced features like conversation history, voice settings, and real-time communication. How can I help you today?",
      sender: 'ai',
      timestamp: new Date().toISOString(),
      type: 'system'
    }])
  }, [])

  // Load conversation history
  const loadConversationHistory = async () => {
    try {
      const response = await fetch('/api/conversations')
      if (response.ok) {
        const data = await response.json()
        // Process and display history
        console.log('Conversation history:', data)
      }
    } catch (error) {
      console.error('Error loading history:', error)
    }
  }

  // Send message function
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
      if (socketRef.current && isConnected) {
        socketRef.current.emit('send_message', {
          message: message,
          conversation_id: conversationId,
          context_type: 'enhanced'
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
            conversation_id: conversationId,
            context_type: 'enhanced'
          }),
        })

        if (response.ok) {
          const data = await response.json()
          setMessages(prev => [...prev, {
            id: Date.now() + 1,
            text: data.response,
            sender: 'ai',
            timestamp: data.timestamp,
            type: data.type,
            metadata: data.metadata
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

  // Voice functions
  const toggleVoiceListening = async () => {
    try {
      if (isListening) {
        const response = await fetch('/api/voice/stop', { method: 'POST' })
        if (response.ok) {
          setIsListening(false)
        }
      } else {
        const response = await fetch('/api/voice/start', { method: 'POST' })
        if (response.ok) {
          setIsListening(true)
        }
      }
    } catch (error) {
      console.error('Error toggling voice:', error)
      setConnectionError('Voice service error')
    }
  }

  const speakText = async (text) => {
    try {
      setIsSpeaking(true)
      const response = await fetch('/api/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, interrupt: true }),
      })
      
      if (!response.ok) {
        throw new Error('TTS request failed')
      }
      
      // Simulate speaking duration
      setTimeout(() => setIsSpeaking(false), text.length * 50)
    } catch (error) {
      console.error('Error speaking text:', error)
      setIsSpeaking(false)
      setConnectionError('Text-to-speech error')
    }
  }

  // Update voice settings
  const updateVoiceSettings = async (newSettings) => {
    try {
      const response = await fetch('/api/voice/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings: newSettings }),
      })
      
      if (response.ok) {
        setVoiceSettings(newSettings)
      }
    } catch (error) {
      console.error('Error updating voice settings:', error)
    }
  }

  // Utility functions
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    // Could add a toast notification here
  }

  const deleteMessage = (messageId) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId))
  }

  const clearAllMessages = () => {
    setMessages([{
      id: 0,
      text: "Conversation cleared. How can I help you?",
      sender: 'ai',
      timestamp: new Date().toISOString(),
      type: 'system'
    }])
  }

  const exportConversation = () => {
    const conversationText = messages.map(msg => 
      `[${new Date(msg.timestamp).toLocaleString()}] ${msg.sender === 'user' ? 'You' : 'ZYEON'}: ${msg.text}`
    ).join('\n\n')
    
    const blob = new Blob([conversationText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `zyeon-conversation-${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className={`min-h-screen ${settings.darkMode ? 'dark' : ''} bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900`}>
      {/* Header */}
      <motion.header 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="border-b border-purple-500/20 bg-black/20 backdrop-blur-lg sticky top-0 z-50"
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
                  ZYEON AI Enhanced
                </h1>
                <p className="text-sm text-purple-300">Advanced Voice Assistant v2.0</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <Badge variant={isConnected ? "default" : "destructive"} className="animate-pulse">
                {isConnected ? <Wifi className="w-3 h-3 mr-1" /> : <WifiOff className="w-3 h-3 mr-1" />}
                {isConnected ? 'Connected' : 'Disconnected'}
              </Badge>
              
              {/* Voice Status */}
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

              {/* Action Buttons */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHistory(true)}
                className="text-purple-400 hover:text-purple-300"
              >
                <History className="w-4 h-4" />
              </Button>

              <Dialog open={showSettings} onOpenChange={setShowSettings}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="text-purple-400 hover:text-purple-300">
                    <Settings className="w-4 h-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-slate-800 border-purple-500/30 text-white max-w-md">
                  <DialogHeader>
                    <DialogTitle>Settings</DialogTitle>
                  </DialogHeader>
                  <SettingsPanel
                    settings={settings}
                    onSettingsChange={setSettings}
                    voiceSettings={voiceSettings}
                    onVoiceSettingsChange={updateVoiceSettings}
                  />
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Error Alert */}
      <AnimatePresence>
        {connectionError && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="container mx-auto px-4 pt-4"
          >
            <Alert className="bg-red-500/10 border-red-500/30 text-red-400">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {connectionError}
                {!isConnected && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={connectSocket}
                    className="ml-2 text-red-400 hover:text-red-300"
                  >
                    <RefreshCw className="w-3 h-3 mr-1" />
                    Retry
                  </Button>
                )}
              </AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 max-w-6xl">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-slate-800/50 border-purple-500/30">
            <TabsTrigger value="chat" className="data-[state=active]:bg-purple-600">
              <MessageCircle className="w-4 h-4 mr-2" />
              Chat
            </TabsTrigger>
            <TabsTrigger value="analytics" className="data-[state=active]:bg-purple-600">
              <Brain className="w-4 h-4 mr-2" />
              Analytics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="mt-6">
            <Card className="h-[calc(100vh-280px)] bg-black/40 border-purple-500/30 backdrop-blur-lg">
              <CardHeader className="border-b border-purple-500/20">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center space-x-2 text-purple-300">
                    <MessageCircle className="w-5 h-5" />
                    <span>Conversation</span>
                    {userId && (
                      <Badge variant="outline" className="text-xs">
                        ID: {userId.slice(-6)}
                      </Badge>
                    )}
                  </CardTitle>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={exportConversation}
                      className="text-purple-400 hover:text-purple-300"
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={clearAllMessages}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="p-0 h-full flex flex-col">
                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  <AnimatePresence>
                    {messages.map((message) => (
                      <MessageBubble
                        key={message.id}
                        message={message}
                        onSpeak={speakText}
                        isSpeaking={isSpeaking}
                        onCopy={copyToClipboard}
                        onDelete={deleteMessage}
                      />
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
                  <div className="flex items-end space-x-3">
                    <div className="flex-1">
                      <Textarea
                        ref={inputRef}
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your message or use voice input..."
                        className="bg-slate-800/50 border-purple-500/30 text-white placeholder-gray-400 resize-none focus:border-purple-400 focus:ring-purple-400 min-h-[40px] max-h-[120px]"
                        disabled={isLoading}
                        rows={1}
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
                      } transition-all duration-200 h-10 w-10`}
                      disabled={!isConnected}
                    >
                      {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                    </Button>
                    
                    <Button
                      onClick={() => sendMessage()}
                      disabled={!inputMessage.trim() || isLoading || !isConnected}
                      className="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 transition-all duration-200 h-10"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <div className="mt-2 text-xs text-gray-400 text-center">
                    {isConnected ? (
                      <>Press Enter to send • Click mic for voice input • ZYEON Enhanced is ready</>
                    ) : (
                      <>Connecting to ZYEON AI Enhanced...</>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="mt-6">
            <Card className="bg-black/40 border-purple-500/30 backdrop-blur-lg">
              <CardHeader>
                <CardTitle className="text-purple-300">Usage Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-800/50 p-4 rounded-lg border border-purple-500/20">
                    <h3 className="text-sm font-medium text-gray-400">Total Messages</h3>
                    <p className="text-2xl font-bold text-white">{messages.length}</p>
                  </div>
                  <div className="bg-slate-800/50 p-4 rounded-lg border border-purple-500/20">
                    <h3 className="text-sm font-medium text-gray-400">Voice Messages</h3>
                    <p className="text-2xl font-bold text-white">
                      {messages.filter(m => m.type === 'voice').length}
                    </p>
                  </div>
                  <div className="bg-slate-800/50 p-4 rounded-lg border border-purple-500/20">
                    <h3 className="text-sm font-medium text-gray-400">Session Time</h3>
                    <p className="text-2xl font-bold text-white">
                      {Math.floor((Date.now() - (messages[0]?.timestamp ? new Date(messages[0].timestamp).getTime() : Date.now())) / 60000)}m
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Floating Voice Indicator */}
      <AnimatePresence>
        {isListening && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="fixed bottom-6 right-6 w-16 h-16 bg-red-500 rounded-full flex items-center justify-center shadow-lg animate-pulse z-50"
          >
            <Mic className="w-8 h-8 text-white" />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default App

