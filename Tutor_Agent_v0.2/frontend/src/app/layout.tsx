import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Tutor GPT - AI-Powered Docker & Kubernetes Learning',
  description: 'Master Docker and Kubernetes with personalized AI tutoring, collaborative learning, and real-time feedback.',
  keywords: ['Docker', 'Kubernetes', 'AI Tutor', 'Learning', 'DevOps', 'Cloud Native'],
  authors: [{ name: 'Tutor GPT Team' }],
  robots: 'index, follow',
  metadataBase: new URL('http://localhost:3000'),
  openGraph: {
    title: 'Tutor GPT - AI-Powered Docker & Kubernetes Learning',
    description: 'Master Docker and Kubernetes with personalized AI tutoring, collaborative learning, and real-time feedback.',
    type: 'website',
    locale: 'en_US',
    images: ['/og.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Tutor GPT - AI-Powered Docker & Kubernetes Learning',
    description: 'Master Docker and Kubernetes with personalized AI tutoring, collaborative learning, and real-time feedback.',
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
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
        </Providers>
      </body>
    </html>
  )
}
