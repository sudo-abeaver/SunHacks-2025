'use client'

import { useState, useRef, useEffect } from 'react'
import Image from 'next/image'

// Import html2canvas dynamically for client-side use only
let html2canvas = null
const loadHtml2Canvas = async () => {
  if (!html2canvas && typeof window !== 'undefined') {
    const module = await import('html2canvas')
    html2canvas = module.default
  }
  return html2canvas
}

const API_BASE = typeof window !== 'undefined' && window.location.port === '5001' ? '' : 'http://localhost:5001'

const tips = [
  'Party Cat is warming up the drawing paws...',
  'Sharpening the magical crayons...',
  'Sketching your educational adventure...',
  'Composing the learning panels...',
  'Balancing colors and fun vibes...',
  'Adding a dash of educational whimsy...',
  'Leaving paw prints of knowledge...',
  'Creating comic book magic...'
]

export default function Home() {
  const [concept, setConcept] = useState('')
  const [usePartyCat, setUsePartyCat] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [status, setStatus] = useState('')
  const [showResults, setShowResults] = useState(false)
  const [showLoader, setShowLoader] = useState(false)
  const [currentTip, setCurrentTip] = useState(0)
  const [comicData, setComicData] = useState({
    title: '',
    panels: [],
    further_exploration: ''
  })
  const [showLearnMore, setShowLearnMore] = useState(false)
  const [showPartyCatBubble, setShowPartyCatBubble] = useState(false)
  const [partyCatMessage, setPartyCatMessage] = useState('')
  const [pawTrails, setPawTrails] = useState([])
  const [mascotClicks, setMascotClicks] = useState(0)
  const [usedCatSounds, setUsedCatSounds] = useState([])
  const [showConfetti, setShowConfetti] = useState(false)
  const [isConfettiPlaying, setIsConfettiPlaying] = useState(false)
  const [isClickDisabled, setIsClickDisabled] = useState(false)

  const comicCanvasRef = useRef(null)
  const tipIntervalRef = useRef(null)
  const bubbleTimeoutRef = useRef(null)
  const catSoundRefs = useRef([])
  const confettiSoundRef = useRef(null)
  const confettiTimeoutRef = useRef(null)
  const clickDebounceRef = useRef(null)

  // Preload audio files
  useEffect(() => {
    // Only preload on client side
    if (typeof window === 'undefined') return

    // Preload cat sounds
    const catSounds = [
      '/catSounds/Cat_idle1.ogg.mp3',
      '/catSounds/Cat_idle2.ogg.mp3', 
      '/catSounds/Cat_idle3.ogg.mp3',
      '/catSounds/Cat_idle4.ogg.mp3'
    ]
    
    catSoundRefs.current = catSounds.map(src => {
      const audio = new Audio(src)
      audio.preload = 'metadata' // Changed from 'auto' to 'metadata' for faster loading
      audio.volume = 0.6
      return audio
    })

    // Preload confetti sound
    confettiSoundRef.current = new Audio('/confetti-pop-sound.mp3')
    confettiSoundRef.current.preload = 'metadata' // Changed from 'auto' to 'metadata'
    confettiSoundRef.current.volume = 0.7

    return () => {
      // Clean up audio references
      catSoundRefs.current = []
      confettiSoundRef.current = null
      
      // Clean up timers
      if (confettiTimeoutRef.current) {
        clearTimeout(confettiTimeoutRef.current)
      }
      if (clickDebounceRef.current) {
        clearTimeout(clickDebounceRef.current)
      }
    }
  }, [])

  useEffect(() => {
    if (showLoader) {
      setCurrentTip(0)
      tipIntervalRef.current = setInterval(() => {
        setCurrentTip(prev => (prev + 1) % tips.length)
      }, 3000) // Matches CSS animation duration for smooth transitions
    } else {
      if (tipIntervalRef.current) {
        clearInterval(tipIntervalRef.current)
        tipIntervalRef.current = null
      }
    }

    return () => {
      if (tipIntervalRef.current) {
        clearInterval(tipIntervalRef.current)
      }
    }
  }, [showLoader])

  // Simple effect to track when results are shown
  useEffect(() => {
    // Any additional effects when comic data changes can go here
  }, [showResults, showLoader, comicData])

  // Party Cat interactions
  useEffect(() => {
    const partyCatMessages = [
      "Hey party people! Ready to learn something new?",
      "Let's create some educational magic!",
      "Learning is purr-fect with comics!",
      "Party Cat is here to help you learn!",
      "Awesome learning adventures await!"
    ]

    const showRandomMessage = () => {
      const randomMessage = partyCatMessages[Math.floor(Math.random() * partyCatMessages.length)]
      showPartyCatMessage(randomMessage, 4000)
    }

    // Show initial message after 3 seconds
    const initialTimer = setTimeout(showRandomMessage, 3000)
    
    // Show random messages every 45 seconds (increased from 30 to reduce frequency)
    const intervalTimer = setInterval(showRandomMessage, 45000)

    return () => {
      clearTimeout(initialTimer)
      clearInterval(intervalTimer)
      // Clean up bubble timeout when component unmounts
      if (bubbleTimeoutRef.current) {
        clearTimeout(bubbleTimeoutRef.current)
      }
      // Clean up confetti and click timeouts
      if (confettiTimeoutRef.current) {
        clearTimeout(confettiTimeoutRef.current)
      }
      if (clickDebounceRef.current) {
        clearTimeout(clickDebounceRef.current)
      }
    }
  }, [])

  // Paw trail effect on mouse move
  useEffect(() => {
    let pawTrailTimeout

    const handleMouseMove = (e) => {
      if (Math.random() > 0.95) { // Only occasionally show paw prints
        const newPaw = {
          id: Date.now(),
          x: e.clientX,
          y: e.clientY
        }
        
        setPawTrails(prev => [...prev.slice(-5), newPaw]) // Keep only last 5 paw prints
        
        // Remove paw print after animation
        pawTrailTimeout = setTimeout(() => {
          setPawTrails(prev => prev.filter(paw => paw.id !== newPaw.id))
        }, 4000)
      }
    }

    document.addEventListener('mousemove', handleMouseMove)
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      clearTimeout(pawTrailTimeout)
    }
  }, [])

  const generateComic = async () => {
    if (!concept.trim()) {
      setStatus('Please enter a concept.')
      return
    }

    setIsGenerating(true)
    setStatus('Generating comic... this can take ~20–40 seconds.')
    setShowResults(true)
    setShowLoader(true)
    setShowLearnMore(false)
    setComicData({ title: '', panels: [], further_exploration: '' })

    try {
      const res = await fetch(`${API_BASE}/generate_comic`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept, use_party_cat: usePartyCat }),
      })

      if (!res.ok) {
        const errorText = await res.text()
        throw new Error(`API error (${res.status}): ${errorText}`)
      }

      const data = await res.json()
      setComicData(data)
      setShowLoader(false)
      
      if (data.further_exploration && data.further_exploration.trim()) {
        setShowLearnMore(true)
      }
      
      setStatus('Done!')
    } catch (err) {
      console.error(err)
      setStatus(`Something went wrong: ${err.message}`)
      setShowLoader(false)
    } finally {
      setIsGenerating(false)
    }
  }

  const showPartyCatMessage = (message, duration = 4000) => {
    // Clear any existing timeout
    if (bubbleTimeoutRef.current) {
      clearTimeout(bubbleTimeoutRef.current)
    }
    
    // Set the new message and show bubble
    setPartyCatMessage(message)
    setShowPartyCatBubble(true)
    
    // Set timeout to hide bubble
    bubbleTimeoutRef.current = setTimeout(() => {
      setShowPartyCatBubble(false)
      bubbleTimeoutRef.current = null
    }, duration)
  }

  const playRandomCatSound = () => {
    if (catSoundRefs.current.length === 0) return

    let availableSounds = []
    
    // If we've used all sounds, reset the used array
    if (usedCatSounds.length >= catSoundRefs.current.length) {
      setUsedCatSounds([])
      availableSounds = [...Array(catSoundRefs.current.length).keys()]
    } else {
      // Get sounds that haven't been used yet
      availableSounds = [...Array(catSoundRefs.current.length).keys()].filter(
        index => !usedCatSounds.includes(index)
      )
    }

    if (availableSounds.length === 0) return

    // Pick a random sound from available ones
    const randomIndex = availableSounds[Math.floor(Math.random() * availableSounds.length)]
    const soundToPlay = catSoundRefs.current[randomIndex]

    try {
      soundToPlay.currentTime = 0 // Reset to beginning
      soundToPlay.play().catch(e => console.log('Sound play failed:', e))
      
      // Mark this sound as used
      setUsedCatSounds(prev => [...prev, randomIndex])
    } catch (error) {
      console.log('Error playing cat sound:', error)
    }
  }

  const playConfettiEffect = () => {
    // Prevent overlapping confetti animations
    if (isConfettiPlaying) {
      return
    }

    // Set confetti state
    setIsConfettiPlaying(true)
    setIsClickDisabled(true)

    // Clear any existing confetti timeout
    if (confettiTimeoutRef.current) {
      clearTimeout(confettiTimeoutRef.current)
    }

    // Play confetti sound
    if (confettiSoundRef.current) {
      try {
        confettiSoundRef.current.currentTime = 0
        confettiSoundRef.current.play().catch(e => console.log('Confetti sound failed:', e))
      } catch (error) {
        console.log('Error playing confetti sound:', error)
      }
    }

    // Show confetti animation
    setShowConfetti(true)
    
    // Clean up confetti after animation completes
    confettiTimeoutRef.current = setTimeout(() => {
      setShowConfetti(false)
      setIsConfettiPlaying(false)
      
      // Re-enable clicks immediately after confetti finishes
      setIsClickDisabled(false)
    }, 2500) // Reduced to 2.5 seconds for faster recovery
  }

  const downloadComic = async () => {
    if (!comicCanvasRef.current) {
      setStatus('Comic not ready for download. Please try again.')
      return
    }

    try {
      setStatus('Preparing download...')
      
      // Ensure html2canvas is loaded
      html2canvas = await loadHtml2Canvas()
      
      // Wait a bit for images to fully load
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const scale = 2
      const canvas = await html2canvas(comicCanvasRef.current, {
        backgroundColor: '#ffffff',
        scale,
        useCORS: true,
        allowTaint: true,
        foreignObjectRendering: true,
        logging: false,
        width: comicCanvasRef.current.offsetWidth,
        height: comicCanvasRef.current.offsetHeight
      })
      
      // Create download link
      const link = document.createElement('a')
      const filename = `${(comicData.title || 'concept2comic').replace(/[^a-zA-Z0-9]/g, '_')}.png`
      link.download = filename
      link.href = canvas.toDataURL('image/png', 0.9)
      
      // Trigger download
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      setStatus('Download successful!')
      setTimeout(() => setStatus(''), 3000)
      
    } catch (err) {
      console.error('Download failed:', err)
      
      // Fallback: Try to create a simple download with comic data
      try {
        setStatus('Trying alternative download method...')
        await downloadComicFallback()
      } catch (fallbackErr) {
        console.error('Fallback download also failed:', fallbackErr)
        setStatus('Download failed. Please try again.')
        setTimeout(() => setStatus(''), 5000)
      }
    }
  }

  const downloadComicFallback = async () => {
    // Create a simple canvas with the comic panels arranged in a grid
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    // Set canvas size
    canvas.width = 800
    canvas.height = 800
    
    // Fill background
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // Add title
    ctx.fillStyle = '#000000'
    ctx.font = 'bold 24px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(comicData.title || 'My Comic', canvas.width / 2, 40)
    
    // Add panels with text
    const panelSize = 350
    const startY = 80
    const panelPositions = [
      { x: 50, y: startY },
      { x: 400, y: startY },
      { x: 50, y: startY + 360 },
      { x: 400, y: startY + 360 }
    ]
    
    comicData.panels.forEach((panel, index) => {
      if (index < 4) {
        const pos = panelPositions[index]
        
        // Draw panel border
        ctx.strokeStyle = '#000000'
        ctx.lineWidth = 2
        ctx.strokeRect(pos.x, pos.y, panelSize, panelSize)
        
        // Add panel number
        ctx.fillStyle = '#ffffff'
        ctx.fillRect(pos.x, pos.y, 30, 30)
        ctx.fillStyle = '#000000'
        ctx.font = 'bold 16px Arial'
        ctx.textAlign = 'center'
        ctx.fillText((index + 1).toString(), pos.x + 15, pos.y + 20)
        
        // Add panel text (wrapped)
        if (panel.text) {
          ctx.font = '14px Arial'
          ctx.textAlign = 'left'
          const words = panel.text.split(' ')
          let line = ''
          let y = pos.y + panelSize - 60
          
          for (let n = 0; n < words.length; n++) {
            const testLine = line + words[n] + ' '
            const metrics = ctx.measureText(testLine)
            const testWidth = metrics.width
            
            if (testWidth > panelSize - 20 && n > 0) {
              ctx.fillText(line, pos.x + 10, y)
              line = words[n] + ' '
              y += 20
            } else {
              line = testLine
            }
          }
          ctx.fillText(line, pos.x + 10, y)
        }
        
        // Add placeholder for image
        ctx.fillStyle = '#f0f0f0'
        ctx.fillRect(pos.x + 10, pos.y + 40, panelSize - 20, panelSize - 120)
        ctx.fillStyle = '#999999'
        ctx.font = '12px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('Comic Panel Image', pos.x + panelSize/2, pos.y + panelSize/2)
      }
    })
    
    // Download the canvas
    const link = document.createElement('a')
    const filename = `${(comicData.title || 'concept2comic').replace(/[^a-zA-Z0-9]/g, '_')}_fallback.png`
    link.download = filename
    link.href = canvas.toDataURL('image/png', 0.9)
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    setStatus('Download successful (simplified version)!')
    setTimeout(() => setStatus(''), 3000)
  }

  const handleMascotClick = () => {
    // Prevent clicks during confetti or if disabled
    if (isClickDisabled || isConfettiPlaying) {
      return
    }

    // Clear any existing debounce
    if (clickDebounceRef.current) {
      clearTimeout(clickDebounceRef.current)
    }

    // Basic debounce to prevent rapid clicking
    clickDebounceRef.current = setTimeout(() => {
      const clickMessages = [
        "Hey party people! Thanks for the pets!",
        "Party time! Let's learn something new!",
        "Purr-fect! You found the secret click!",
        "Ready to create more comics?",
        "*happy cat noises*",
        "Learning is fun with friends!",
        "You're awesome!",
        "Let's make education magical!"
      ]
      
      const newClickCount = mascotClicks + 1
      setMascotClicks(newClickCount)
      
      // Play random cat sound
      playRandomCatSound()
      
      // Special milestone celebrations (5, 10, 15, 20, 25, etc.)
      if (newClickCount % 5 === 0) {
        // For milestones, show celebration immediately
        playConfettiEffect()
        
        // Show celebration message after a short delay
        setTimeout(() => {
          showPartyCatMessage(`🎉 AMAZING! ${newClickCount} clicks! You really love Party Cat! 🎉`, 5000)
        }, 500)
      } else {
        // For regular clicks, show random message
        const randomMessage = clickMessages[Math.floor(Math.random() * clickMessages.length)]
        showPartyCatMessage(randomMessage, 3000)
      }
    }, 100) // Reduced debounce to 100ms for better responsiveness
  }

  return (
    <>
      <header className="site-header">
        <div className="container">
          <h1 className="brand">Concept2Comic</h1>
          <p className="tagline">Join Party Cat on educational adventures! Turn any concept into a playful comic strip</p>
        </div>
      </header>

      <main className="container">
        <section className="generator-card">
          <div className="form-row">
            <label htmlFor="concept" className="label">What would you like to learn about?</label>
            <textarea 
              id="concept" 
              className="input" 
              rows="3" 
              placeholder="Try something like: What is gravity? How does photosynthesis work? Explain the water cycle."
              value={concept}
              onChange={(e) => setConcept(e.target.value)}
            />
          </div>
          <div className="form-row options">
            <label className="checkbox">
              <input 
                type="checkbox" 
                id="usePartyCat"
                checked={usePartyCat}
                onChange={(e) => setUsePartyCat(e.target.checked)}
              />
              <span>Include Party Cat in the comic adventure!</span>
            </label>
          </div>
          <div className="actions">
            <button 
              className="btn primary" 
              onClick={generateComic}
              disabled={isGenerating}
            >
Create Comic Magic!
            </button>
            <button 
              className="btn" 
              onClick={downloadComic}
              disabled={!showResults || showLoader || isGenerating}
            >
Download My Comic
            </button>
          </div>
          <p className="status" aria-live="polite">{status}</p>
        </section>

        {showResults && (
          <section className="results">
            <div className="canvas-scale-wrapper">
              <div ref={comicCanvasRef} className="comic-canvas">
              <h2 className="comic-title">{comicData.title || 'Your Comic'}</h2>
              
              {showLoader && (
                <div className="loader-block fadeable">
                  <div className="spinner large"></div>
                  <div className="tips">
                    <p key={currentTip} className="tip-text">{tips[currentTip]}</p>
                  </div>
                </div>
              )}
              
              {!showLoader && (
                <div className="comic-grid fadeable">
                  {[0, 1, 2, 3].map((i) => (
                    <div key={i} className="comic-panel">
                      <div className="panel-image">
                        {comicData.panels[i]?.image ? (
                          <Image
                            alt={`Panel ${i + 1}`}
                            src={`data:image/png;base64,${comicData.panels[i].image}`}
                            fill
                            style={{ objectFit: 'cover' }}
                          />
                        ) : (
                          <div className="empty-panel">
                            <span className="panel-number">{i + 1}</span>
                          </div>
                        )}
                      </div>
                      <div className="panel-caption">
                        <span className="panel-badge">{i + 1}</span>
                        <p>{comicData.panels[i]?.text || `Panel ${i + 1} loading...`}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              </div>
            </div>
          </section>
        )}

        {showLearnMore && (
          <section className="learn-more-section">
            <div className="learn-more-content">
              <h3>Party Cat's Extra Learning Tips!</h3>
              <div className="further" dangerouslySetInnerHTML={{
                __html: comicData.further_exploration?.replace(
                  /\[([^\]]+)\]\(([^)]+)\)/g, 
                  '<a href="$2" target="_blank" rel="noopener noreferrer" class="wiki-link">$1</a>'
                ) || ''
              }} />
            </div>
          </section>
        )}
      </main>

      {/* Spacer to push footer down on initial load, hidden during generation */}
      {!showResults && (
        <div className="footer-spacer"></div>
      )}

      <footer className="site-footer">
        <div className="container">
          <div className="footer-content">
            {/* How It Works Section */}
            <div className="footer-section">
              <h3>🎨 How It Works</h3>
              <p>
                Concept2Comic uses advanced AI to transform educational concepts into engaging comic strips! 
                Simply enter any topic you'd like to learn about, and our system creates a fun 4-panel comic 
                that makes learning memorable and enjoyable. Perfect for visual learners of all ages!
              </p>
            </div>

            {/* Mission Statement */}
            <div className="footer-section">
              <h3>🚀 Our Mission</h3>
              <p>
                We believe learning should be fun, accessible, and engaging for everyone. By combining the power 
                of generative AI with the timeless appeal of comics, we're making education more interactive 
                and helping kids (and adults!) discover the joy of learning through visual storytelling.
              </p>
            </div>

            {/* Team Section */}
            <div className="footer-section">
              <h3>👥 Our Team</h3>
              <div className="team-members">
                <span className="team-member">Aaron Beaver</span>
                <span className="team-member">Malaika Kamran Khan</span>
                <span className="team-member">Nagasai Arul Karumuri</span>
                <span className="team-member">Anthony Marcel</span>
              </div>
            </div>

            {/* Copyright and License */}
            <div className="footer-section footer-legal">
              <p>© 2025 Concept2Comic Team. All rights reserved.</p>
              <p>Licensed under the MIT License - Open source and free to use!</p>
            </div>
          </div>
        </div>
      </footer>

      {/* Party Cat Speech Bubble */}
      {showPartyCatBubble && (
        <div className="party-cat-bubble">
          {partyCatMessage}
        </div>
      )}

      {/* Paw Print Trails */}
      {pawTrails.map(paw => (
        <div 
          key={paw.id}
          className="paw-trail"
          style={{ left: paw.x - 10, top: paw.y - 10 }}
        >
          🐾
        </div>
      ))}

      {/* Comic Sound Effects */}
      <div className="comic-sound-effect" style={{ top: '15%', left: '5%' }}>
        POW!
      </div>
      <div className="comic-sound-effect" style={{ top: '25%', right: '8%', animationDelay: '1s' }}>
        ZAP!
      </div>
      <div className="comic-sound-effect" style={{ bottom: '20%', left: '10%', animationDelay: '2s' }}>
        BOOM!
      </div>

      {/* Party Cat Mascot */}
      <div 
        className={`party-cat-mascot ${isClickDisabled ? 'disabled' : ''} ${isConfettiPlaying ? 'celebrating' : ''}`} 
        onClick={handleMascotClick}
        style={{ cursor: isClickDisabled ? 'not-allowed' : 'pointer' }}
      >
        <Image
          src="/partycat.png"
          alt="Party Cat Mascot - Click me!"
          width={120}
          height={120}
          className="party-cat-image"
        />
      </div>

      {/* Confetti Effect */}
      {showConfetti && (
        <div className="confetti-container">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="confetti-piece"
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                backgroundColor: `hsl(${Math.random() * 360}, 70%, 60%)`
              }}
            />
          ))}
        </div>
      )}
    </>
  )
}
