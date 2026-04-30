'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  AcademicCapIcon, 
  ChatBubbleLeftRightIcon, 
  UserGroupIcon, 
  ChartBarIcon,
  PlayIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  SparklesIcon,
  RocketLaunchIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'
import { useApp } from '@/components/providers'
import { LoginModal } from '@/components/auth/login-modal'
import { RegisterModal } from '@/components/auth/register-modal'

export function LandingPage() {
  const { user } = useApp()
  const [showLogin, setShowLogin] = useState(false)
  const [showRegister, setShowRegister] = useState(false)

  const features = [
    {
      icon: AcademicCapIcon,
      title: 'AI-Powered Tutoring',
      description: 'Personalized learning with advanced AI agents that adapt to your learning style and pace.',
      color: 'text-primary-600',
      bgColor: 'bg-primary-100',
    },
    {
      icon: ChatBubbleLeftRightIcon,
      title: 'Real-time Interaction',
      description: 'Interactive chat with AI tutors, instant feedback, and dynamic lesson adjustments.',
      color: 'text-accent-600',
      bgColor: 'bg-accent-100',
    },
    {
      icon: UserGroupIcon,
      title: 'Collaborative Learning',
      description: 'Join study groups, peer learning sessions, and collaborative projects with other students.',
      color: 'text-success-600',
      bgColor: 'bg-success-100',
    },
    {
      icon: ChartBarIcon,
      title: 'Progress Analytics',
      description: 'Track your learning journey with detailed analytics, achievements, and performance insights.',
      color: 'text-warning-600',
      bgColor: 'bg-warning-100',
    },
  ]

  const agents = [
    {
      name: 'Olivia - Tutor Agent',
      role: 'Personalized Learning',
      description: 'Delivers adaptive lessons tailored to your learning style with real-world examples.',
      avatar: '🎓',
    },
    {
      name: 'Alex - Planning Agent',
      role: 'Study Planning',
      description: 'Creates comprehensive study plans and learning paths based on your goals.',
      avatar: '📋',
    },
    {
      name: 'Sam - Assessment Agent',
      role: 'Learning Evaluation',
      description: 'Conducts VARK assessments and evaluates your understanding with smart quizzes.',
      avatar: '🧠',
    },
    {
      name: 'Max - Quiz Agent',
      role: 'Knowledge Testing',
      description: 'Generates adaptive quizzes and provides detailed feedback on your progress.',
      avatar: '📝',
    },
    {
      name: 'Casey - Orchestrator',
      role: 'Learning Flow',
      description: 'Coordinates your learning journey and manages seamless transitions between agents.',
      avatar: '🎭',
    },
    {
      name: 'Dr. Smith - Feedback Agent',
      role: 'System Principal',
      description: 'Monitors your progress and continuously improves the learning experience.',
      avatar: '📊',
    },
  ]

  const stats = [
    { label: 'Active Students', value: '10,000+' },
    { label: 'Learning Hours', value: '50,000+' },
    { label: 'Success Rate', value: '95%' },
    { label: 'AI Agents', value: '6' },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <CpuChipIcon className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gradient">Tutor GPT</span>
            </div>
            
            <div className="flex items-center space-x-4">
              {user ? (
                <a
                  href="/dashboard"
                  className="btn-primary"
                >
                  Go to Dashboard
                </a>
              ) : (
                <>
                  <button
                    onClick={() => setShowLogin(true)}
                    className="btn-secondary"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => setShowRegister(true)}
                    className="btn-primary"
                  >
                    Get Started
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-20 pb-16 bg-gradient-to-br from-primary-50 via-white to-accent-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary-100 text-primary-800 text-sm font-medium mb-6">
                <SparklesIcon className="w-4 h-4 mr-2" />
                AI-Powered Learning Platform
              </div>
              
              <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
                Learn{' '}
                <span className="text-gradient">Anything, Faster</span>
                <br />
                with AI Tutors
              </h1>

              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                Upload any course content and learn with personalised AI agents that adapt to your
                learning style. Get assessments, study plans, quizzes, and real-time feedback — all in one place.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => setShowRegister(true)}
                  className="btn-primary text-lg px-8 py-3 shadow-glow"
                >
                  Start Learning Free
                  <ArrowRightIcon className="w-5 h-5 ml-2" />
                </button>
                <button className="btn-secondary text-lg px-8 py-3">
                  <PlayIcon className="w-5 h-5 mr-2" />
                  Watch Demo
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-primary-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose Tutor GPT?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Experience the future of learning with our advanced AI-powered tutoring system.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card hover:shadow-lg transition-shadow"
              >
                <div className={`w-12 h-12 ${feature.bgColor} rounded-lg flex items-center justify-center mb-4`}>
                  <feature.icon className={`w-6 h-6 ${feature.color}`} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Agents Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Meet Your AI Learning Team
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Six specialized AI agents work together to provide you with the ultimate learning experience.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {agents.map((agent, index) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center text-2xl mr-4">
                    {agent.avatar}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {agent.name}
                    </h3>
                    <p className="text-sm text-primary-600 font-medium">
                      {agent.role}
                    </p>
                  </div>
                </div>
                <p className="text-gray-600">
                  {agent.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-primary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Transform Your Learning?
            </h2>
            <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
              Join thousands of students who are already mastering their subjects with AI-powered personalised tutoring.
            </p>
            <button
              onClick={() => setShowRegister(true)}
              className="btn bg-white text-primary-600 hover:bg-gray-50 text-lg px-8 py-3 shadow-glow"
            >
              <RocketLaunchIcon className="w-5 h-5 mr-2" />
              Start Your Journey Today
            </button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                  <CpuChipIcon className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">Tutor GPT</span>
              </div>
              <p className="text-gray-400">
                AI-powered learning platform for mastering any subject.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Learning</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Getting Started</a></li>
                <li><a href="#" className="hover:text-white">VARK Assessment</a></li>
                <li><a href="#" className="hover:text-white">Study Plans</a></li>
                <li><a href="#" className="hover:text-white">Quizzes & Practice</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Features</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">AI Tutoring</a></li>
                <li><a href="#" className="hover:text-white">Collaborative Learning</a></li>
                <li><a href="#" className="hover:text-white">Progress Tracking</a></li>
                <li><a href="#" className="hover:text-white">Real-time Chat</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Contact Us</a></li>
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Tutor GPT. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Modals */}
      {showLogin && (
        <LoginModal
          onClose={() => setShowLogin(false)}
          onSwitchToRegister={() => {
            setShowLogin(false)
            setShowRegister(true)
          }}
        />
      )}
      
      {showRegister && (
        <RegisterModal
          onClose={() => setShowRegister(false)}
          onSwitchToLogin={() => {
            setShowRegister(false)
            setShowLogin(true)
          }}
        />
      )}
    </div>
  )
}
