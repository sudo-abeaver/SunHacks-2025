import './globals.css'
import { Inter, Patrick_Hand, Nunito } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })
const patrickHand = Patrick_Hand({ 
  subsets: ['latin'],
  weight: '400',
  variable: '--font-patrick-hand'
})
const nunito = Nunito({ 
  subsets: ['latin'],
  weight: ['400', '600'],
  variable: '--font-nunito'
})

export const metadata = {
  title: 'Concept2Comic',
  description: 'Turn any concept into a playful, fun comic strip that makes learning awesome! 🎨📚✨',
  keywords: 'education, comics, learning, fun, educational comics, concept learning',
  authors: [{ name: 'Concept2Comic Team' }],
  creator: 'Concept2Comic',
  publisher: 'Concept2Comic',
  robots: 'index, follow',
  icons: {
    icon: '/android-chrome-512x512.png',
    shortcut: '/android-chrome-512x512.png',
    apple: '/android-chrome-512x512.png',
  },
  openGraph: {
    title: 'Concept2Comic',
    description: 'Turn any concept into a playful, fun comic strip that makes learning awesome!',
    type: 'website',
  },
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.className} ${patrickHand.variable} ${nunito.variable}`}>
        {children}
      </body>
    </html>
  )
}
