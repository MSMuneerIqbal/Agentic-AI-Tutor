import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Tutor GPT - AI-Powered Docker & Kubernetes Learning',
  description: 'Master Docker and Kubernetes with personalized AI tutoring, collaborative learning, and real-time feedback.',
  keywords: ['Docker', 'Kubernetes', 'AI Tutor', 'Learning', 'DevOps', 'Cloud Native'],
  authors: [{ name: 'Tutor GPT Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: 'Tutor GPT - AI-Powered Docker & Kubernetes Learning',
    description: 'Master Docker and Kubernetes with personalized AI tutoring, collaborative learning, and real-time feedback.',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Tutor GPT - AI-Powered Docker & Kubernetes Learning',
    description: 'Master Docker and Kubernetes with personalized AI tutoring, collaborative learning, and real-time feedback.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full antialiased`}>
        <Providers>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}
