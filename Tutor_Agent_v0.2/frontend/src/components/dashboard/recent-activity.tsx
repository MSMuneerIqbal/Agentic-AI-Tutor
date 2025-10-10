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
  const activities = [
    {
      id: 1,
      type: 'lesson',
      title: 'Completed Docker Container Basics',
      description: 'Finished lesson on container lifecycle and management',
      time: '2 hours ago',
      icon: AcademicCapIcon,
      color: 'text-success-600',
      bgColor: 'bg-success-100',
    },
    {
      id: 2,
      type: 'chat',
      title: 'Chat with Olivia (Tutor Agent)',
      description: 'Asked about Docker networking concepts',
      time: '4 hours ago',
      icon: ChatBubbleLeftRightIcon,
      color: 'text-primary-600',
      bgColor: 'bg-primary-100',
    },
    {
      id: 3,
      type: 'achievement',
      title: 'Earned "Container Master" Badge',
      description: 'Completed 10 Docker lessons successfully',
      time: '1 day ago',
      icon: TrophyIcon,
      color: 'text-warning-600',
      bgColor: 'bg-warning-100',
    },
    {
      id: 4,
      type: 'group',
      title: 'Joined "Docker Beginners" Study Group',
      description: 'Connected with 24 other learners',
      time: '2 days ago',
      icon: UserGroupIcon,
      color: 'text-accent-600',
      bgColor: 'bg-accent-100',
    },
  ]

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
