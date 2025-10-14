'use client'

import { motion } from 'framer-motion'
import { UserGroupIcon, UsersIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'

interface StudyGroupsProps {
  user: any
}

export function StudyGroups({ user }: StudyGroupsProps) {
  const groups = [
    {
      id: 1,
      name: 'Docker Beginners',
      description: 'Learning Docker fundamentals together',
      members: 24,
      activeMembers: 8,
      lastActivity: '2 hours ago',
      level: 'Beginner',
      isJoined: true,
    },
    {
      id: 2,
      name: 'Kubernetes Study Group',
      description: 'Advanced Kubernetes concepts and best practices',
      members: 18,
      activeMembers: 5,
      lastActivity: '1 day ago',
      level: 'Advanced',
      isJoined: false,
    },
    {
      id: 3,
      name: 'DevOps Community',
      description: 'General DevOps discussions and learning',
      members: 45,
      activeMembers: 12,
      lastActivity: '30 minutes ago',
      level: 'All Levels',
      isJoined: true,
    },
  ]

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'Beginner':
        return 'badge-success'
      case 'Intermediate':
        return 'badge-warning'
      case 'Advanced':
        return 'badge-error'
      default:
        return 'badge-secondary'
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Study Groups</h2>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          Create Group
        </button>
      </div>

      <div className="space-y-4">
        {groups.map((group, index) => (
          <motion.div
            key={group.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className={`p-4 rounded-lg border ${
              group.isJoined 
                ? 'border-primary-200 bg-primary-50' 
                : 'border-gray-200 bg-white'
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  group.isJoined ? 'bg-primary-600' : 'bg-gray-400'
                }`}>
                  <UserGroupIcon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{group.name}</h3>
                  <p className="text-sm text-gray-600">{group.description}</p>
                </div>
              </div>
              <span className={`badge ${getLevelColor(group.level)}`}>
                {group.level}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
              <div className="flex items-center space-x-4">
                <span className="flex items-center">
                  <UsersIcon className="w-4 h-4 mr-1" />
                  {group.members} members
                </span>
                <span className="flex items-center text-success-600">
                  <div className="w-2 h-2 bg-success-500 rounded-full mr-1"></div>
                  {group.activeMembers} online
                </span>
              </div>
              <span className="text-xs">{group.lastActivity}</span>
            </div>

            <div className="flex items-center justify-between">
              <button className={`btn text-sm ${
                group.isJoined 
                  ? 'btn-secondary' 
                  : 'btn-primary'
              }`}>
                {group.isJoined ? 'Open Chat' : 'Join Group'}
              </button>
              <button className="p-2 text-gray-400 hover:text-primary-600">
                <ChatBubbleLeftRightIcon className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
