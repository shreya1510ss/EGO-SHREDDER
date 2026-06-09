import { useState } from 'react'
import { STRINGS } from '../strings'

function InputBar({ onSend, disabled, language }) {
  const [text, setText] = useState('')
  const L = STRINGS[language] || STRINGS.english

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function submit() {
    if (!text.trim() || disabled) return
    onSend(text)
    setText('')
  }

  return (
    <div className="input-area">
      <textarea
        id="input"
        rows={1}
        value={text}
        placeholder={L.placeholder}
        disabled={disabled}
        onChange={e => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        autoFocus
      />
      <button id="send-btn" onClick={submit} disabled={disabled} title="Send">
        <svg viewBox="0 0 24 24">
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </div>
  )
}

export default InputBar
