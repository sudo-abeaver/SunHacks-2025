'use client'

import { useEffect, useState } from 'react'

export default function HalftoneParticles() {
  const [particles, setParticles] = useState([])

  useEffect(() => {
    // Generate halftone particles with varying sizes and positions
    const generateParticles = () => {
      const newParticles = []
      // Responsive particle count based on screen size
      const isMobile = typeof window !== 'undefined' && window.innerWidth < 768
      const particleCount = isMobile ? 40 : 80 // Fewer particles on mobile
      
      for (let i = 0; i < particleCount; i++) {
        newParticles.push({
          id: i,
          x: Math.random() * 100, // Percentage position
          y: Math.random() * 100,
          size: Math.random() * 8 + 2, // 2-10px diameter
          opacity: Math.random() * 0.3 + 0.05, // 0.05-0.35 opacity (more subtle)
          animationDelay: Math.random() * 10, // 0-10s delay
          animationDuration: Math.random() * 15 + 10, // 10-25s duration
          color: Math.floor(Math.random() * 6), // 0-5 for different colors
          blur: Math.random() > 0.7, // 30% chance of blur effect
        })
      }
      setParticles(newParticles)
    }

    generateParticles()

    // Regenerate particles on window resize (for responsive behavior)
    const handleResize = () => {
      generateParticles()
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('resize', handleResize)
      return () => window.removeEventListener('resize', handleResize)
    }
  }, [])

  const getParticleColor = (colorIndex) => {
    const colors = [
      'var(--comic-blue)',
      'var(--party-cat-pink)', 
      'var(--comic-yellow)',
      'var(--comic-purple)',
      'var(--comic-green)',
      'var(--comic-orange)'
    ]
    return colors[colorIndex]
  }

  return (
    <div className="halftone-particles">
      {particles.map((particle) => (
        <div
          key={particle.id}
          className={`halftone-particle ${particle.blur ? 'blur-effect' : ''}`}
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            backgroundColor: getParticleColor(particle.color),
            opacity: particle.opacity,
            animationDelay: `${particle.animationDelay}s`,
            animationDuration: `${particle.animationDuration}s`,
          }}
        />
      ))}
    </div>
  )
}
