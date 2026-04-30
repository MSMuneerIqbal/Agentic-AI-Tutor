'use client'

import { motion } from 'framer-motion'
import { 
  ChatBubbleLeftRightIcon, 
  AcademicCapIcon, 
  TrophyIcon, 
  UserGroupIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

interface RecentActivityProps {
  user: any
}

export function RecentActivity({ user }: RecentActivityProps) {
  // Real activities for new students
  const isNewUser = !user?.activities || user?.activities.length === 0
  
  const defaultActivities = [
    {
      id: 1,
      type: 'welcome',
      title: 'Welcome to Tutor GPT!',
      description: 'Your personalised AI learning journey starts here',
      time: 'Just now',
      icon: AcademicCapIcon,
      color: 'text-primary-600',
      bgColor: 'bg-primary-100',
    },
    {
      id: 2,
      type: 'tip',
      title: 'Getting Started Tip',
      description: 'Open the chat and tell the tutor what you want to learn',
      time: 'Just now',
      icon: ChatBubbleLeftRightIcon,
      color: 'text-accent-600',
      bgColor: 'bg-accent-100',
    },
  ]
  
  const activities = isNewUser ? defaultActivities : (user?.activities || defaultActivities)

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'lesson':
        return AcademicCapIcon
      case 'chat':
        return ChatBubbleLeftRightIcon
      case 'achievement':
        return TrophyIcon
      case 'group':
        return UserGroupIcon
      case 'welcome':
        return AcademicCapIcon
      case 'tip':
        return ChatBubbleLeftRightIcon
      default:
        return ClockIcon
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View All
        </button>
      </div>

      <div className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = getActivityIcon(activity.type)
          
          return (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className={`w-8 h-8 ${activity.bgColor} rounded-lg flex items-center justify-center flex-shrink-0`}>
                <Icon className={`w-4 h-4 ${activity.color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-gray-900">{activity.title}</h3>
                <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
                <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
