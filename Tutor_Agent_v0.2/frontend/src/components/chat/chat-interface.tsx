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
  const { socket, isConnected } = useApp()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const agents = [
    { id: 'orchestrator', name: 'Orchestrator', avatar: '🎭', color: 'bg-purple-100 text-purple-600' },
    { id: 'tutor', name: 'Olivia (Tutor)', avatar: '🎓', color: 'bg-blue-100 text-blue-600' },
    { id: 'planning', name: 'Alex (Planning)', avatar: '📋', color: 'bg-green-100 text-green-600' },
    { id: 'assessment', name: 'Sam (Assessment)', avatar: '🧠', color: 'bg-yellow-100 text-yellow-600' },
    { id: 'quiz', name: 'Max (Quiz)', avatar: '📝', color: 'bg-red-100 text-red-600' },
    { id: 'feedback', name: 'Dr. Smith (Feedback)', avatar: '📊', color: 'bg-indigo-100 text-indigo-600' },
  ]

  useEffect(() => {
    if (socket) {
      // Listen for messages from agents
      socket.on('agent_message', (data: any) => {
        const newMessage: Message = {
          id: Date.now().toString(),
          content: data.content,
          sender: 'agent',
          agentName: data.agent_name,
          timestamp: new Date(),
          type: 'text',
          metadata: data.metadata,
        }
        setMessages(prev => [...prev, newMessage])
        setIsTyping(false)
      })

      // Listen for agent typing indicators
      socket.on('agent_typing', (data: any) => {
        setCurrentAgent(data.agent_name)
        setIsTyping(true)
      })

      // Listen for agent handoffs
      socket.on('agent_handoff', (data: any) => {
        const systemMessage: Message = {
          id: Date.now().toString(),
          content: `Handing off to ${data.to_agent}...`,
          sender: 'agent',
          agentName: data.from_agent,
          timestamp: new Date(),
          type: 'system',
        }
        setMessages(prev => [...prev, systemMessage])
      })

      // Listen for session updates
      socket.on('session_update', (data: any) => {
        const systemMessage: Message = {
          id: Date.now().toString(),
          content: `Session state updated: ${data.state}`,
          sender: 'agent',
          agentName: 'System',
          timestamp: new Date(),
          type: 'system',
        }
        setMessages(prev => [...prev, systemMessage])
      })

      return () => {
        socket.off('agent_message')
        socket.off('agent_typing')
        socket.off('agent_handoff')
        socket.off('session_update')
      }
    }
  }, [socket])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!inputMessage.trim() || !socket || !isConnected) {
      toast.error('Unable to send message. Please check your connection.')
      return
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')

    // Send message to backend
    try {
      socket.emit('user_message', {
        content: inputMessage,
        user_id: user.id,
        session_id: user.session_id,
      })
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage(e)
    }
  }

  const formatMessage = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm">$1</code>')
      .replace(/\n/g, '<br>')
  }

  const getAgentInfo = (agentName?: string) => {
    return agents.find(agent => agent.name === agentName) || agents[0]
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
            <CpuChipIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">AI Learning Chat</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success-500' : 'bg-error-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
        
        {currentAgent && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <SparklesIcon className="w-4 h-4 animate-pulse" />
            <span>{currentAgent} is typing...</span>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CpuChipIcon className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to Tutor GPT!
            </h3>
            <p className="text-gray-600 mb-4">
              Start a conversation with your AI tutors. Ask questions, request lessons, or get help with Docker and Kubernetes.
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {['Hello!', 'Start learning', 'Help me with Docker', 'Take assessment'].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInputMessage(suggestion)}
                  className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        <AnimatePresence>
          {messages.map((message) => {
            const agentInfo = getAgentInfo(message.agentName)
            
            return (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  {/* Avatar */}
                  <div className={`flex-shrink-0 ${message.sender === 'user' ? 'ml-3' : 'mr-3'}`}>
                    {message.sender === 'user' ? (
                      <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                        <UserIcon className="w-5 h-5 text-white" />
                      </div>
                    ) : (
                      <div className={`w-8 h-8 ${agentInfo.color} rounded-full flex items-center justify-center`}>
                        <span className="text-sm">{agentInfo.avatar}</span>
                      </div>
                    )}
                  </div>

                  {/* Message Content */}
                  <div className={`flex flex-col ${message.sender === 'user' ? 'items-end' : 'items-start'}`}>
                    {message.sender === 'agent' && message.agentName && (
                      <span className="text-xs text-gray-500 mb-1">{message.agentName}</span>
                    )}
                    
                    <div className={`px-4 py-2 rounded-2xl ${
                      message.sender === 'user'
                        ? 'bg-primary-600 text-white'
                        : message.type === 'system'
                        ? 'bg-gray-100 text-gray-700'
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      {message.type === 'text' ? (
                        <div 
                          className="prose prose-sm max-w-none"
                          dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                        />
                      ) : (
                        <p>{message.content}</p>
                      )}
                    </div>
                    
                    <span className="text-xs text-gray-500 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>

        {/* Typing Indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <span className="text-sm">🤖</span>
              </div>
              <div className="bg-gray-100 px-4 py-2 rounded-2xl">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex items-center space-x-3">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask your AI tutors anything..."
            className="flex-1 input"
            disabled={!isConnected}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || !isConnected}
            className="btn-primary p-2"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </form>
        
        {!isConnected && (
          <p className="text-sm text-error-600 mt-2">
            Connection lost. Please refresh the page to reconnect.
          </p>
        )}
      </div>
    </div>
  )
}
