'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  ChartBarIcon, 
  AcademicCapIcon, 
  UserGroupIcon, 
  ChatBubbleLeftRightIcon,
  CogIcon,
  BellIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  FireIcon,
  TrophyIcon,
  ClockIcon,
  BookOpenIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { useApp } from '@/components/providers'
import { Sidebar } from '@/components/dashboard/sidebar'
import { Header } from '@/components/dashboard/header'
import { StatsCards } from '@/components/dashboard/stats-cards'
import { LearningProgress } from '@/components/dashboard/learning-progress'
import { RecentActivity } from '@/components/dashboard/recent-activity'
import { StudyGroups } from '@/components/dashboard/study-groups'
import { QuickActions } from '@/components/dashboard/quick-actions'
import { ChatInterface } from '@/components/chat/chat-interface'

export function Dashboard() {
  const { user, session, setUser } = useApp()
  const [activeTab, setActiveTab] = useState('overview')
  const [showChat, setShowChat] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Check user authentication with loading state
  useEffect(() => {
    const checkAuth = () => {
      const savedUser = localStorage.getItem('tutor-gpt-user') || sessionStorage.getItem('tutor-gpt-user')
      
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser)
          if (!user) {
            setUser(userData)
          }
          // Ensure both storages have the data
          localStorage.setItem('tutor-gpt-user', savedUser)
          sessionStorage.setItem('tutor-gpt-user', savedUser)
          setIsLoading(false)
          return true
        } catch (error) {
          console.error('Error parsing user data:', error)
          localStorage.removeItem('tutor-gpt-user')
          sessionStorage.removeItem('tutor-gpt-user')
          return false
        }
      } else if (user) {
        setIsLoading(false)
        return true
      } else {
        return false
      }
    }

    const isAuth = checkAuth()
    
    if (!isAuth) {
      const timeoutId = setTimeout(() => {
        window.location.href = '/'
      }, 500)
      
      return () => clearTimeout(timeoutId)
    }
  }, [user, setUser])

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'learning', name: 'Learning', icon: AcademicCapIcon },
    { id: 'groups', name: 'Study Groups', icon: UserGroupIcon },
    { id: 'chat', name: 'AI Chat', icon: ChatBubbleLeftRightIcon },
    { id: 'settings', name: 'Settings', icon: CogIcon },
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            <StatsCards user={user} session={session} />
            <div className="grid lg:grid-cols-2 gap-6">
              <LearningProgress user={user} onTabChange={setActiveTab} />
              <RecentActivity user={user} />
            </div>
            <div className="grid lg:grid-cols-2 gap-6">
              <StudyGroups user={user} />
              <QuickActions user={user} onTabChange={setActiveTab} />
            </div>
          </div>
        )
      case 'learning':
        return (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Learning Path</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-primary-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                      <BookOpenIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">Docker Fundamentals</h3>
                      <p className="text-sm text-gray-600">Container basics and Docker commands</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-primary-600">In Progress</div>
                    <div className="text-xs text-gray-500">65% Complete</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-400 rounded-full flex items-center justify-center">
                      <BookOpenIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">Kubernetes Basics</h3>
                      <p className="text-sm text-gray-600">Pods, services, and deployments</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-500">Locked</div>
                    <div className="text-xs text-gray-500">Complete Docker first</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      case 'groups':
        return (
          <div className="space-y-6">
            <StudyGroups user={user} />
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Join Study Groups</h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { name: 'Docker Beginners', members: 24, level: 'Beginner' },
                  { name: 'Kubernetes Advanced', members: 18, level: 'Advanced' },
                  { name: 'DevOps Study Group', members: 32, level: 'Intermediate' },
                ].map((group, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors">
                    <h3 className="font-medium text-gray-900 mb-2">{group.name}</h3>
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>{group.members} members</span>
                      <span className="badge badge-secondary">{group.level}</span>
                    </div>
                    <button 
                      onClick={() => {
                        // TODO: Implement actual join group functionality
                        alert(`Joining ${group.name}...`)
                      }}
                      className="btn-primary w-full mt-3 text-sm"
                    >
                      Join Group
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )
      case 'chat':
        return (
          <div className="h-[600px]">
            <ChatInterface user={user} />
          </div>
        )
      case 'settings':
        return (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Profile Settings</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                  <input type="text" className="input" defaultValue={user.name} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input type="email" className="input" defaultValue={user.email} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Learning Style</label>
                  <select className="select" defaultValue={user.learningStyle || 'V'}>
                    <option value="V">Visual</option>
                    <option value="A">Auditory</option>
                    <option value="R">Reading/Writing</option>
                    <option value="K">Kinesthetic</option>
                  </select>
                </div>
                <button 
                  onClick={() => {
                    // TODO: Implement actual save functionality
                    alert('Settings saved!')
                  }}
                  className="btn-primary"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        {/* Sidebar */}
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} tabs={tabs} />
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <Header user={user} onChatClick={() => setShowChat(true)} />
          
          {/* Content */}
          <main className="flex-1 p-6">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {renderContent()}
            </motion.div>
          </main>
        </div>
      </div>

      {/* Chat Modal */}
      {showChat && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setShowChat(false)} />
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl h-[80vh]">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">AI Chat</h2>
              <button
                onClick={() => setShowChat(false)}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <div className="h-[calc(100%-80px)]">
              <ChatInterface user={user} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
