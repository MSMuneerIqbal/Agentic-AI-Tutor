'use client'

import { createContext, useContext, useEffect, useState } from 'react'

// Types
interface User {
  id: string
  name: string
  email: string
  avatar?: string
  learningStyle?: 'V' | 'A' | 'R' | 'K'
  progress?: number
  level?: 'beginner' | 'intermediate' | 'advanced'
}

interface Session {
  id: string
  userId: string
  state: 'GREETING' | 'ASSESSING' | 'PLANNING' | 'TUTORING' | 'QUIZZING' | 'COLLABORATING' | 'COMPLETED'
  topic?: string
  progress: number
  startTime: Date
  lastActivity: Date
}

interface AppContextType {
  user: User | null
  session: Session | null
  websocket: WebSocket | null
  isConnected: boolean
  setUser: (user: User | null) => void
  setSession: (session: Session | null) => void
  connectWebSocket: () => void
  disconnectWebSocket: () => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within a Providers')
  }
  return context
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [websocket, setWebSocket] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  const connectWebSocket = () => {
    if (websocket?.readyState === WebSocket.OPEN) return

    try {
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
      const newWebSocket = new WebSocket(`${wsUrl}/ws/sessions/${user?.id || 'default'}`)

      newWebSocket.onopen = () => {
        console.log('Connected to server')
        setIsConnected(true)
      }

      newWebSocket.onclose = () => {
        console.log('Disconnected from server')
        setIsConnected(false)
      }

      newWebSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('WebSocket message received:', data)
          
          if (data.type === 'session_update') {
            setSession(data)
          } else if (data.type === 'user_update') {
            setUser(data)
          } else if (data.type === 'agent_message') {
            // Agent messages are handled by the chat component
            console.log('Agent message received:', data.text)
          } else if (data.type === 'error') {
            console.error('WebSocket error:', data.message)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      newWebSocket.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
      }

      setWebSocket(newWebSocket)
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }

  const disconnectWebSocket = () => {
    if (websocket) {
      websocket.close()
      setWebSocket(null)
      setIsConnected(false)
    }
  }

  useEffect(() => {
    // Load user from localStorage on mount (fallback)
    const loadUser = () => {
      const savedUser = localStorage.getItem('tutor-gpt-user') || sessionStorage.getItem('tutor-gpt-user')
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser)
          setUser(userData)
          // Ensure both localStorage and sessionStorage have the data
          localStorage.setItem('tutor-gpt-user', savedUser)
          sessionStorage.setItem('tutor-gpt-user', savedUser)
          return true
        } catch (error) {
          console.error('Error parsing saved user:', error)
          localStorage.removeItem('tutor-gpt-user')
          sessionStorage.removeItem('tutor-gpt-user')
          return false
        }
      }
      return false
    }

    // Add a small delay to handle Fast Refresh timing issues
    const timeoutId = setTimeout(() => {
      const userLoaded = loadUser()
      if (userLoaded) {
        connectWebSocket()
      }
    }, 50)

    return () => {
      clearTimeout(timeoutId)
      disconnectWebSocket()
    }
  }, [])

  useEffect(() => {
    // Save user to both localStorage and sessionStorage when it changes
    if (user) {
      const userData = JSON.stringify(user)
      localStorage.setItem('tutor-gpt-user', userData)
      sessionStorage.setItem('tutor-gpt-user', userData)
      
      // Store user data in backend session for agent context
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
          type: 'user_data_update',
          user_data: user,
          timestamp: new Date().toISOString()
        }))
      }
      
      if (websocket?.readyState !== WebSocket.OPEN) {
        connectWebSocket()
      }
    } else {
      localStorage.removeItem('tutor-gpt-user')
      sessionStorage.removeItem('tutor-gpt-user')
      disconnectWebSocket()
    }
  }, [user])

  const value: AppContextType = {
    user,
    session,
    websocket,
    isConnected,
    setUser,
    setSession,
    connectWebSocket,
    disconnectWebSocket,
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}
