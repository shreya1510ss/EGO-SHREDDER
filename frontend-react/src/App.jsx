import { useState } from 'react'
import Header from './components/Header'
import ChatWindow from './components/ChatWindow'
import InputBar from './components/InputBar'

const BACKEND = 'https://ego-shredder-backend.onrender.com'

function App() {
  const [history, setHistory]   = useState([])
  const [language, setLanguage] = useState('english')
  const [messages, setMessages] = useState([])
  const [thinking, setThinking] = useState(false)
  const [error, setError]       = useState('')

  async function send(text) {
    setMessages(prev => [...prev, { type: 'user', text }])
    setThinking(true)
    setError('')

    try {
      const res = await fetch(`${BACKEND}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_input: text,
          conversation_history: history,
          language,
        }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }

      const data = await res.json()
      setMessages(prev => [...prev, { type: 'system', state: data.state }])
      setHistory(prev => [
        ...prev,
        { role: 'user',      content: text },
        { role: 'assistant', content: data.response_text },
      ])
    } catch (err) {
      setError('Error: ' + err.message)
      setTimeout(() => setError(''), 5000)
      console.error(err)
    } finally {
      setThinking(false)
    }
  }

  function toggleLanguage() {
    setLanguage(l => l === 'english' ? 'hindi' : 'english')
  }

  return (
    <>
      <Header language={language} onToggle={toggleLanguage} />
      <ChatWindow messages={messages} thinking={thinking} language={language} />
      <InputBar onSend={send} disabled={thinking} language={language} />
      {error && <div id="error-toast" style={{ display: 'block' }}>{error}</div>}
    </>
  )
}

export default App
