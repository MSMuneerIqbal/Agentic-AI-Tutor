'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { io, Socket } from 'socket.io-client'

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
  socket: Socket | null
  isConnected: boolean
  setUser: (user: User | null) => void
  setSession: (session: Session | null) => void
  connectSocket: () => void
  disconnectSocket: () => void
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
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  const connectSocket = () => {
    if (socket?.connected) return

    const newSocket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000', {
      transports: ['websocket'],
      autoConnect: true,
    })

    newSocket.on('connect', () => {
      console.log('Connected to server')
      setIsConnected(true)
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server')
      setIsConnected(false)
    })

    newSocket.on('session_update', (data: Session) => {
      setSession(data)
    })

    newSocket.on('user_update', (data: User) => {
      setUser(data)
    })

    setSocket(newSocket)
  }

  const disconnectSocket = () => {
    if (socket) {
      socket.disconnect()
      setSocket(null)
      setIsConnected(false)
    }
  }

  useEffect(() => {
    // Load user from localStorage on mount
    const savedUser = localStorage.getItem('tutor-gpt-user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (error) {
        console.error('Error parsing saved user:', error)
        localStorage.removeItem('tutor-gpt-user')
      }
    }

    // Connect to socket if user exists
    if (savedUser) {
      connectSocket()
    }

    return () => {
      disconnectSocket()
    }
  }, [])

  useEffect(() => {
    // Save user to localStorage when it changes
    if (user) {
      localStorage.setItem('tutor-gpt-user', JSON.stringify(user))
      if (!socket?.connected) {
        connectSocket()
      }
    } else {
      localStorage.removeItem('tutor-gpt-user')
      disconnectSocket()
    }
  }, [user])

  const value: AppContextType = {
    user,
    session,
    socket,
    isConnected,
    setUser,
    setSession,
    connectSocket,
    disconnectSocket,
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}
