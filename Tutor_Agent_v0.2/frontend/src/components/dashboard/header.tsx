'use client'

import { BellIcon, ChatBubbleLeftRightIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { useApp } from '@/components/providers'

interface HeaderProps {
  user: any
  onChatClick: () => void
}

export function Header({ user, onChatClick }: HeaderProps) {
  const { setUser } = useApp()

  const handleLogout = () => {
    setUser(null)
    window.location.href = '/'
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-lg">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search lessons, topics, or study groups..."
              className="input pl-10 w-full"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-4">
          {/* Chat Button */}
          <button
            onClick={onChatClick}
            className="p-2 text-gray-400 hover:text-primary-600 transition-colors relative"
          >
            <ChatBubbleLeftRightIcon className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-primary-600 rounded-full"></span>
          </button>

          {/* Notifications */}
          <button className="p-2 text-gray-400 hover:text-primary-600 transition-colors relative">
            <BellIcon className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-warning-500 rounded-full"></span>
          </button>

          {/* User Menu */}
          <div className="relative group">
            <button className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.name?.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="text-sm font-medium text-gray-700">{user?.name}</span>
            </button>
            
            {/* Dropdown Menu */}
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
              <div className="py-1">
                <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Profile Settings
                </a>
                <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Learning Preferences
                </a>
                <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                  Study Groups
                </a>
                <hr className="my-1" />
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
