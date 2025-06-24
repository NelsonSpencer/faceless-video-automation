'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

interface ListicleResponse {
  success: boolean
  message: string
  images: string[]
  download_url?: string
}

interface FormatOption {
  name: string
  width: number
  height: number
  description: string
}

interface FormatsResponse {
  formats: Record<string, FormatOption>
  background_types: Record<string, string>
}

export default function Home() {
  const [topic, setTopic] = useState('')
  const [format, setFormat] = useState('landscape')
  const [background, setBackground] = useState('color')
  const [numSlides, setNumSlides] = useState(5)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<ListicleResponse | null>(null)
  const [error, setError] = useState('')
  const [formats, setFormats] = useState<FormatsResponse | null>(null)

  const loadFormats = async () => {
    try {
      const response = await axios.get('/api/formats')
      setFormats(response.data)
    } catch (err) {
      console.error('Failed to load formats:', err)
    }
  }

  // Load available formats on component mount
  useEffect(() => {
    loadFormats()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!topic.trim()) {
      setError('Please enter a topic')
      return
    }

    setLoading(true)
    setError('')
    setResults(null)

    try {
      const response = await axios.post('/api/generate', {
        topic: topic.trim(),
        format_type: format,
        background_type: background,
        num_slides: numSlides
      })

      setResults(response.data)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to generate listicle'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">Faceless Content Generator</h1>
        <p className="subtitle">
          Create engaging listicles for social media platforms
        </p>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label htmlFor="topic" className="label">
              Topic *
            </label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Top 5 Productivity Tips"
              className="input"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="format" className="label">
              Format
            </label>
            <select
              id="format"
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="select"
            >
              <option value="landscape">YouTube/Landscape (1920x1080)</option>
              <option value="portrait">TikTok/Portrait (1080x1920)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="background" className="label">
              Background Type
            </label>
            <select
              id="background"
              value={background}
              onChange={(e) => setBackground(e.target.value)}
              className="select"
            >
              <option value="color">Color Gradients</option>
              <option value="stock">Stock Images</option>
              <option value="ai">AI Generated (slower)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="numSlides" className="label">
              Number of Slides
            </label>
            <select
              id="numSlides"
              value={numSlides}
              onChange={(e) => setNumSlides(parseInt(e.target.value))}
              className="select"
            >
              {[3, 4, 5, 6, 7, 8].map(num => (
                <option key={num} value={num}>{num} slides</option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="button"
          >
            {loading ? 'Generating...' : 'Generate Listicle'}
          </button>
        </form>

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <span>Creating your listicle...</span>
          </div>
        )}

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {results && results.success && (
          <div className="results">
            <h3 className="results-title">Generated Listicle</h3>
            
            <div className="success">
              {results.message}
            </div>

            <div className="image-grid">
              {results.images.map((imageUrl, index) => (
                <div key={index} className="image-preview">
                  <img
                    src={imageUrl}
                    alt={`Slide ${index + 1}`}
                    onError={(e) => {
                      console.error(`Failed to load image: ${imageUrl}`)
                      e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4='
                    }}
                  />
                  <div style={{textAlign: 'center', padding: '8px', fontSize: '14px', color: '#666'}}>
                    Slide {index + 1}
                  </div>
                </div>
              ))}
            </div>

            <div style={{display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '2rem'}}>
              <button
                onClick={() => {
                  setResults(null)
                  setError('')
                }}
                className="button"
                style={{background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}}
              >
                Generate New Listicle
              </button>

              {results.download_url && (
                <a
                  href={results.download_url}
                  download
                  className="download-button"
                >
                  Download All Images (.zip)
                </a>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}