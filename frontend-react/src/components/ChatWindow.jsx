import { useEffect, useRef } from 'react'
import { STRINGS } from '../strings'
import MessageBubble from './MessageBubble'
import ThinkingDots from './ThinkingDots'

function ChatWindow({ messages, thinking, language }) {
  const chatRef = useRef(null)
  const L = STRINGS[language] || STRINGS.english

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight
    }
  }, [messages, thinking])

  return (
    <div id="chat" ref={chatRef}>
      {messages.length === 0 && (
        <div className="welcome">
          <div className="glyph">◈</div>
          <h2>{L.welcomeH2}</h2>
          <p>{L.welcomeP}</p>
        </div>
      )}
      {messages.map((msg, i) => (
        <MessageBubble key={i} message={msg} language={language} />
      ))}
      {thinking && <ThinkingDots />}
    </div>
  )
}

export default ChatWindow
