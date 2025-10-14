'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  PaperAirplaneIcon, 
  UserIcon,
  CpuChipIcon,
  SparklesIcon,
  StopIcon
} from '@heroicons/react/24/outline'
import { useApp } from '@/components/providers'
import toast from 'react-hot-toast'

interface Message {
  id: string
  content: string
  sender: 'user' | 'agent'
  agentName?: string
  timestamp: Date
  type: 'text' | 'code' | 'image' | 'system'
  metadata?: any
}

interface ChatInterfaceProps {
  user: any
}

export function ChatInterface({ user }: ChatInterfaceProps) {
  const { websocket, isConnected } = useApp()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Add welcome message when component mounts
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        content: `Welcome to Tutor GPT, ${user?.name || 'Student'}! I'm your AI teacher and I'm here to guide you through mastering Docker and Kubernetes. I can explain concepts, provide hands-on exercises, assess your progress, and help you build real-world projects. What would you like to learn first?`,
        sender: 'agent',
        agentName: 'AI Teacher',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages([welcomeMessage])
    }
  }, [user, messages.length])

  // WebSocket message handler for real AI responses
  useEffect(() => {
    if (websocket) {
      const handleMessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data)
          console.log('Received WebSocket message:', data)
          
          if (data.type === 'agent_message') {
            const agentMessage: Message = {
              id: Date.now().toString(),
              content: data.text,
              sender: 'agent',
              agentName: data.agent === 'orchestrator' ? 'AI Teacher' : data.agent,
              timestamp: new Date(data.timestamp),
              type: 'text'
            }
            setMessages(prev => [...prev, agentMessage])
            setIsTyping(false)
          } else if (data.type === 'error') {
            const errorMessage: Message = {
              id: Date.now().toString(),
              content: data.message || 'An error occurred with the AI tutor.',
              sender: 'agent',
              agentName: 'System',
              timestamp: new Date(),
              type: 'text'
            }
            setMessages(prev => [...prev, errorMessage])
            setIsTyping(false)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
          setIsTyping(false)
        }
      }

      websocket.addEventListener('message', handleMessage)
      
      return () => {
        websocket.removeEventListener('message', handleMessage)
      }
    }
  }, [websocket])

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !websocket || websocket.readyState !== WebSocket.OPEN) {
      toast.error('Connection not available')
      return
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsTyping(true)

    try {
      // Send message via WebSocket
      websocket.send(JSON.stringify({
        message: inputMessage,
        type: 'user_message',
        timestamp: new Date().toISOString(),
        user_id: user?.id
      }))

      // Real AI responses will come via WebSocket message handler
      // No simulated response needed - the backend provides real AI responses

    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message')
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
            <SparklesIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">AI Tutor</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-500">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
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
              <div className={`flex max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.sender === 'user' 
                    ? 'bg-primary-600 ml-3' 
                    : 'bg-gray-600 mr-3'
                }`}>
                  {message.sender === 'user' ? (
                    <UserIcon className="w-4 h-4 text-white" />
                  ) : (
                    <CpuChipIcon className="w-4 h-4 text-white" />
                  )}
                </div>
                <div className={`px-4 py-2 rounded-2xl ${
                  message.sender === 'user'
                    ? 'bg-primary-600 text-white'
                    : message.type === 'system'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  {message.agentName && message.sender === 'agent' && (
                    <div className="text-xs font-medium mb-1 opacity-75">
                      {message.agentName}
                    </div>
                  )}
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  <div className={`text-xs mt-1 ${
                    message.sender === 'user' ? 'text-primary-100' : 'text-gray-500'
                  }`}>
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex max-w-[80%]">
              <div className="w-8 h-8 rounded-full bg-gray-600 mr-3 flex items-center justify-center">
                <CpuChipIcon className="w-4 h-4 text-white" />
              </div>
              <div className="px-4 py-2 rounded-2xl bg-gray-100 text-gray-900">
                <div className="flex items-center space-x-1">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                  <span className="text-sm text-gray-500 ml-2">
                    {currentAgent || 'AI Tutor'} is typing...
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about Docker or Kubernetes..."
              className="w-full px-4 py-3 border border-gray-300 rounded-2xl resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || !isConnected}
            className="p-3 bg-primary-600 text-white rounded-2xl hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}