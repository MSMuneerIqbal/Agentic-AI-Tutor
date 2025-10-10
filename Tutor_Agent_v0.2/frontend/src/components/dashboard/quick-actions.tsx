'use client'

import { motion } from 'framer-motion'
import { 
  PlayIcon, 
  BookOpenIcon, 
  ChatBubbleLeftRightIcon, 
  UserGroupIcon,
  ChartBarIcon,
  CogIcon
} from '@heroicons/react/24/outline'

interface QuickActionsProps {
  user: any
}

export function QuickActions({ user }: QuickActionsProps) {
  const actions = [
    {
      id: 1,
      title: 'Start Learning',
      description: 'Continue your current lesson',
      icon: PlayIcon,
      color: 'text-primary-600',
      bgColor: 'bg-primary-100',
      action: 'learn',
    },
    {
      id: 2,
      title: 'Chat with AI',
      description: 'Ask questions to your AI tutors',
      icon: ChatBubbleLeftRightIcon,
      color: 'text-accent-600',
      bgColor: 'bg-accent-100',
      action: 'chat',
    },
    {
      id: 3,
      title: 'Join Study Group',
      description: 'Connect with other learners',
      icon: UserGroupIcon,
      color: 'text-success-600',
      bgColor: 'bg-success-100',
      action: 'groups',
    },
    {
      id: 4,
      title: 'View Progress',
      description: 'Check your learning analytics',
      icon: ChartBarIcon,
      color: 'text-warning-600',
      bgColor: 'bg-warning-100',
      action: 'progress',
    },
  ]

  const handleAction = (action: string) => {
    switch (action) {
      case 'learn':
        // Navigate to learning interface
        console.log('Start learning')
        break
      case 'chat':
        // Open chat interface
        console.log('Open chat')
        break
      case 'groups':
        // Navigate to study groups
        console.log('Join study group')
        break
      case 'progress':
        // Navigate to progress page
        console.log('View progress')
        break
      default:
        break
    }
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">Quick Actions</h2>
      
      <div className="grid grid-cols-2 gap-4">
        {actions.map((action, index) => {
          const Icon = action.icon
          
          return (
            <motion.button
              key={action.id}
              onClick={() => handleAction(action.action)}
              className="p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all text-left group"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className={`w-10 h-10 ${action.bgColor} rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                <Icon className={`w-5 h-5 ${action.color}`} />
              </div>
              <h3 className="font-medium text-gray-900 mb-1">{action.title}</h3>
              <p className="text-sm text-gray-600">{action.description}</p>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}
