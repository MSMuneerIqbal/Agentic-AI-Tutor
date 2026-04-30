'use client'

import { motion } from 'framer-motion'
import { 
  AcademicCapIcon, 
  ClockIcon, 
  TrophyIcon, 
  FireIcon,
  ChartBarIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline'

interface StatsCardsProps {
  user: any
  session: any
}

export function StatsCards({ user, session }: StatsCardsProps) {
  // Real data for new students - start fresh
  const isNewUser = !user?.learningStreak && !user?.totalStudyTime && !user?.achievements
  
  const stats = [
    {
      name: 'Learning Streak',
      value: user?.learningStreak || '0 days',
      change: isNewUser ? 'Start your journey!' : '+1 day',
      changeType: isNewUser ? 'neutral' : 'positive',
      icon: FireIcon,
      color: 'text-warning-600',
      bgColor: 'bg-warning-100',
    },
    {
      name: 'Study Time',
      value: user?.totalStudyTime || '0h 0m',
      change: isNewUser ? 'Begin learning' : '+30m today',
      changeType: isNewUser ? 'neutral' : 'positive',
      icon: ClockIcon,
      color: 'text-primary-600',
      bgColor: 'bg-primary-100',
    },
    {
      name: 'Achievements',
      value: user?.achievements || '0',
      change: isNewUser ? 'Earn your first badge!' : '+1 this week',
      changeType: isNewUser ? 'neutral' : 'positive',
      icon: TrophyIcon,
      color: 'text-success-600',
      bgColor: 'bg-success-100',
    },
    {
      name: 'Progress',
      value: `${user?.progress || 0}%`,
      change: isNewUser ? 'Complete your first lesson' : '+2% this week',
      changeType: isNewUser ? 'neutral' : 'positive',
      icon: ChartBarIcon,
      color: 'text-accent-600',
      bgColor: 'bg-accent-100',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon
        
        return (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="card hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                <p className={`text-sm mt-1 ${
                  stat.changeType === 'positive' ? 'text-success-600' : 
                  stat.changeType === 'neutral' ? 'text-gray-600' : 'text-error-600'
                }`}>
                  {stat.change}
                </p>
              </div>
              <div className={`w-12 h-12 ${stat.bgColor} rounded-lg flex items-center justify-center`}>
                <Icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
