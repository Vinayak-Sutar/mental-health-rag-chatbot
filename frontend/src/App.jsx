import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi there! 👋 I'm here to listen and support you. How are you feeling today?" }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, session_id: sessionId })
      })

      if (!response.ok) throw new Error('API error')

      const data = await response.json()
      setSessionId(data.session_id)
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I'm having trouble connecting. Please try again 💙" 
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([
      { role: 'assistant', content: "Hi there! 👋 I'm here to listen and support you. How are you feeling today?" }
    ])
    setSessionId(null)
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-avatar">🧠</div>
        <div className="header-info">
          <h1>Mental Health Support</h1>
          <span className="status">Online • Here to help</span>
        </div>
        <button className="clear-btn" onClick={clearChat} title="New chat">
          🗑️
        </button>
      </header>

      {/* Messages */}
      <main className="messages-container">
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-bubble">
                {msg.content}
              </div>
              <span className="message-time">
                {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          ))}
          {loading && (
            <div className="message assistant">
              <div className="message-bubble typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input */}
      <footer className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          rows={1}
          disabled={loading}
        />
        <button 
          onClick={sendMessage} 
          disabled={!input.trim() || loading}
          className="send-btn"
        >
          ➤
        </button>
      </footer>

      {/* Crisis footer */}
      <div className="crisis-footer">
        💡 For crisis support: Call <strong>Tele-MANAS 14416</strong> (India)
      </div>
    </div>
  )
}

export default App
