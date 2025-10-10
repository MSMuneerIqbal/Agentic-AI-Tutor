'use client'

import { motion } from 'framer-motion'
import { BookOpenIcon, CheckCircleIcon, ClockIcon } from '@heroicons/react/24/outline'

interface LearningProgressProps {
  user: any
}

export function LearningProgress({ user }: LearningProgressProps) {
  const learningPath = [
    {
      id: 1,
      title: 'Docker Fundamentals',
      description: 'Container basics and Docker commands',
      progress: 75,
      status: 'in-progress',
      estimatedTime: '2h 30m',
      completedLessons: 6,
      totalLessons: 8,
    },
    {
      id: 2,
      title: 'Docker Compose',
      description: 'Multi-container applications',
      progress: 0,
      status: 'locked',
      estimatedTime: '1h 45m',
      completedLessons: 0,
      totalLessons: 5,
    },
    {
      id: 3,
      title: 'Kubernetes Basics',
      description: 'Pods, services, and deployments',
      progress: 0,
      status: 'locked',
      estimatedTime: '3h 15m',
      completedLessons: 0,
      totalLessons: 10,
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success-600 bg-success-100'
      case 'in-progress':
        return 'text-primary-600 bg-primary-100'
      case 'locked':
        return 'text-gray-500 bg-gray-100'
      default:
        return 'text-gray-500 bg-gray-100'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed'
      case 'in-progress':
        return 'In Progress'
      case 'locked':
        return 'Locked'
      default:
        return 'Not Started'
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Learning Progress</h2>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View All
        </button>
      </div>

      <div className="space-y-4">
        {learningPath.map((course, index) => (
          <motion.div
            key={course.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className={`p-4 rounded-lg border ${
              course.status === 'in-progress' 
                ? 'border-primary-200 bg-primary-50' 
                : course.status === 'completed'
                ? 'border-success-200 bg-success-50'
                : 'border-gray-200 bg-gray-50'
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  course.status === 'in-progress' 
                    ? 'bg-primary-600' 
                    : course.status === 'completed'
                    ? 'bg-success-600'
                    : 'bg-gray-400'
                }`}>
                  {course.status === 'completed' ? (
                    <CheckCircleIcon className="w-5 h-5 text-white" />
                  ) : (
                    <BookOpenIcon className="w-5 h-5 text-white" />
                  )}
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{course.title}</h3>
                  <p className="text-sm text-gray-600">{course.description}</p>
                </div>
              </div>
              <span className={`badge ${getStatusColor(course.status)}`}>
                {getStatusText(course.status)}
              </span>
            </div>

            {course.status !== 'locked' && (
              <>
                <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                  <span>{course.completedLessons} of {course.totalLessons} lessons</span>
                  <span className="flex items-center">
                    <ClockIcon className="w-4 h-4 mr-1" />
                    {course.estimatedTime}
                  </span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    className={`h-2 rounded-full ${
                      course.status === 'completed' ? 'bg-success-600' : 'bg-primary-600'
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${course.progress}%` }}
                    transition={{ duration: 1, delay: index * 0.2 }}
                  />
                </div>
              </>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  )
}
