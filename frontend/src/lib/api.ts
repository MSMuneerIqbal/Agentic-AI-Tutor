import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const user = localStorage.getItem('tutor-gpt-user')
    if (user) {
      try {
        const userData = JSON.parse(user)
        if (userData.token) {
          config.headers.Authorization = `Bearer ${userData.token}`
        }
      } catch (error) {
        console.error('Error parsing user data:', error)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear user data and redirect to login
      localStorage.removeItem('tutor-gpt-user')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/api/v1/auth/login', { email, password }),
  
  register: (name: string, email: string, password: string) =>
    api.post('/api/v1/auth/register', { name, email, password }),
  
  logout: () => api.post('/api/v1/auth/logout'),
  
  refresh: () => api.post('/api/v1/auth/refresh'),
}

export const userAPI = {
  getProfile: () => api.get('/api/v1/users/profile'),
  
  updateProfile: (data: any) => api.put('/api/v1/users/profile', data),
  
  getProgress: () => api.get('/api/v1/users/progress'),
  
  updateProgress: (data: any) => api.put('/api/v1/users/progress', data),
}

export const sessionAPI = {
  createSession: () => api.post('/api/v1/sessions'),
  
  getSession: (sessionId: string) => api.get(`/api/v1/sessions/${sessionId}`),
  
  updateSession: (sessionId: string, data: any) =>
    api.put(`/api/v1/sessions/${sessionId}`, data),
  
  endSession: (sessionId: string) => api.delete(`/api/v1/sessions/${sessionId}`),
}

export const learningAPI = {
  getLearningPath: () => api.get('/api/v1/learning/path'),
  
  getLessons: (topic?: string) => api.get('/api/v1/learning/lessons', { params: { topic } }),
  
  getLesson: (lessonId: string) => api.get(`/api/v1/learning/lessons/${lessonId}`),
  
  completeLesson: (lessonId: string, data: any) =>
    api.post(`/api/v1/learning/lessons/${lessonId}/complete`, data),
}

export const assessmentAPI = {
  startAssessment: () => api.post('/api/v1/assessment/start'),
  
  submitAnswer: (questionId: string, answer: any) =>
    api.post(`/api/v1/assessment/questions/${questionId}/answer`, { answer }),
  
  getResults: (assessmentId: string) =>
    api.get(`/api/v1/assessment/${assessmentId}/results`),
}

export const quizAPI = {
  generateQuiz: (topic: string, difficulty?: string) =>
    api.post('/api/v1/quiz/generate', { topic, difficulty }),
  
  submitAnswer: (quizId: string, questionId: string, answer: any) =>
    api.post(`/api/v1/quiz/${quizId}/questions/${questionId}/answer`, { answer }),
  
  getResults: (quizId: string) => api.get(`/api/v1/quiz/${quizId}/results`),
}

export const ragAPI = {
  searchContent: (query: string, agentType?: string) =>
    api.get('/api/v1/rag/content', { params: { query, agent_type: agentType } }),
  
  getTopicContent: (topic: string) =>
    api.get(`/api/v1/rag/topic/${topic}`),
  
  getLiveExamples: (topic: string) =>
    api.get(`/api/v1/rag/live-examples/${topic}`),
}

export const collaborationAPI = {
  getStudyGroups: () => api.get('/api/v1/collaboration/groups'),
  
  createStudyGroup: (data: any) => api.post('/api/v1/collaboration/groups', data),
  
  joinStudyGroup: (groupId: string) => api.post(`/api/v1/collaboration/groups/${groupId}/join`),
  
  leaveStudyGroup: (groupId: string) => api.post(`/api/v1/collaboration/groups/${groupId}/leave`),
  
  getGroupMessages: (groupId: string) => api.get(`/api/v1/collaboration/groups/${groupId}/messages`),
  
  sendGroupMessage: (groupId: string, message: string) =>
    api.post(`/api/v1/collaboration/groups/${groupId}/messages`, { message }),
}

export const analyticsAPI = {
  getLearningAnalytics: () => api.get('/api/v1/analytics/learning'),
  
  getProgressAnalytics: () => api.get('/api/v1/analytics/progress'),
  
  getPerformanceMetrics: () => api.get('/api/v1/analytics/performance'),
}

export default api
