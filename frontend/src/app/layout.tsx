import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Faceless Video Automation',
  description: 'Generate social media listicles and content',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}