# Tutor GPT Frontend

A modern, responsive frontend application for the Tutor GPT AI-powered learning platform.

## 🚀 Features

- **Modern UI/UX**: Built with Next.js 14, TypeScript, and Tailwind CSS
- **Real-time Chat**: WebSocket integration with AI agents
- **Responsive Design**: Mobile-first approach with beautiful animations
- **Professional Dashboard**: Comprehensive learning analytics and progress tracking
- **Collaborative Learning**: Study groups and peer interaction features
- **Authentication**: Secure user management and session handling

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Animations**: Framer Motion
- **Icons**: Heroicons
- **HTTP Client**: Axios
- **WebSocket**: Socket.io-client
- **Forms**: React Hook Form
- **Notifications**: React Hot Toast
- **Charts**: Recharts

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── dashboard/          # Dashboard pages
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Landing page
│   ├── components/             # React components
│   │   ├── auth/               # Authentication components
│   │   ├── chat/               # Chat interface
│   │   ├── dashboard/          # Dashboard components
│   │   ├── landing/            # Landing page components
│   │   └── providers.tsx       # Context providers
│   └── lib/                    # Utilities and API
│       └── api.ts              # API integration
├── public/                     # Static assets
├── package.json                # Dependencies
├── tailwind.config.js          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
└── next.config.js              # Next.js configuration
```

## 🎨 Design System

### Colors
- **Primary**: Blue gradient for main actions
- **Secondary**: Gray tones for neutral elements
- **Accent**: Cyan for highlights and accents
- **Success**: Green for positive actions
- **Warning**: Orange for attention
- **Error**: Red for errors

### Components
- **Buttons**: Primary, secondary, success, warning, error variants
- **Cards**: Consistent shadow and border styling
- **Inputs**: Form elements with focus states
- **Badges**: Status indicators and labels
- **Modals**: Overlay dialogs with animations

## 🔧 Setup and Installation

1. **Install Dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Environment Configuration**
   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Build for Production**
   ```bash
   npm run build
   npm start
   ```

## 🌐 Pages and Routes

- **`/`** - Landing page with features and signup
- **`/dashboard`** - Main learning dashboard
- **`/dashboard/learning`** - Learning interface
- **`/dashboard/groups`** - Study groups
- **`/dashboard/chat`** - AI chat interface
- **`/dashboard/settings`** - User settings

## 🤖 AI Agent Integration

The frontend integrates with 6 specialized AI agents:

1. **Orchestrator** - Manages learning flow and agent handoffs
2. **Tutor (Olivia)** - Delivers personalized lessons
3. **Planning (Alex)** - Creates study plans
4. **Assessment (Sam)** - Conducts learning evaluations
5. **Quiz (Max)** - Generates and evaluates quizzes
6. **Feedback (Dr. Smith)** - Monitors and improves the system

## 📱 Responsive Design

- **Mobile**: Optimized for phones and tablets
- **Tablet**: Enhanced layout for medium screens
- **Desktop**: Full-featured experience for large screens
- **Touch**: Touch-friendly interactions and gestures

## 🔐 Authentication

- **Registration**: User signup with email validation
- **Login**: Secure authentication with JWT tokens
- **Session Management**: Automatic token refresh and logout
- **Protected Routes**: Dashboard requires authentication

## 💬 Real-time Features

- **WebSocket Chat**: Real-time communication with AI agents
- **Typing Indicators**: Shows when agents are responding
- **Message History**: Persistent chat history
- **Agent Handoffs**: Seamless transitions between agents

## 📊 Analytics and Progress

- **Learning Analytics**: Track progress and performance
- **Achievement System**: Badges and milestones
- **Study Time Tracking**: Monitor learning hours
- **Progress Visualization**: Charts and graphs

## 🎯 Key Features

### Landing Page
- Hero section with compelling value proposition
- Feature showcase with icons and descriptions
- AI agent introductions
- Call-to-action sections
- Professional footer

### Dashboard
- **Overview**: Stats cards, progress, recent activity
- **Learning**: Interactive learning path and lessons
- **Study Groups**: Collaborative learning features
- **AI Chat**: Real-time chat with AI tutors
- **Settings**: User preferences and profile management

### Chat Interface
- Real-time messaging with AI agents
- Typing indicators and message history
- Agent identification and handoffs
- Message formatting and code highlighting
- Connection status indicators

## 🚀 Performance Optimizations

- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Lazy Loading**: Components loaded on demand
- **Caching**: API response caching
- **Bundle Analysis**: Optimized bundle sizes

## 🔧 Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Code Quality
- **TypeScript**: Full type safety
- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting (if configured)
- **Husky**: Git hooks for quality checks

## 🌟 Best Practices

- **Component Architecture**: Reusable and composable components
- **State Management**: Context API for global state
- **Error Handling**: Comprehensive error boundaries
- **Loading States**: Skeleton screens and spinners
- **Accessibility**: ARIA labels and keyboard navigation
- **SEO**: Meta tags and structured data

## 📈 Future Enhancements

- **PWA Support**: Progressive Web App capabilities
- **Offline Mode**: Cached content for offline learning
- **Voice Integration**: Speech-to-text and text-to-speech
- **Video Lessons**: Embedded video content
- **Mobile App**: React Native mobile application
- **Advanced Analytics**: Machine learning insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the Tutor GPT learning platform.