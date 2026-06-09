import { STRINGS } from '../strings'

function stripMarkdown(s) {
  return String(s)
    .replace(/\*\*\*(.*?)\*\*\*/g, '$1')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/__(.*?)__/g, '$1')
    .replace(/_(.*?)_/g, '$1')
}

function MessageBubble({ message, language }) {
  const L = STRINGS[language] || STRINGS.english

  if (message.type === 'user') {
    return (
      <div className="message user">
        <div className="role-tag">{L.roleUser}</div>
        <div className="bubble">{message.text}</div>
      </div>
    )
  }

  const { state } = message
  const body     = stripMarkdown(state.conversational_response || '')
  const question = stripMarkdown(state.closing_question || '')

  return (
    <div className="message system">
      <div className="role-tag">{L.roleTeacher}</div>
      <div className="bubble">
        <div className="response-body">{body}</div>
        {question && (
          <div className="response-question">{question}</div>
        )}
        <div className="analysis-panel">
          <div className="a-label">{L.labelNarr}</div>
          {state.narratives_identified.map((n, i) => (
            <div key={i} className="a-item">• {n}</div>
          ))}
          <div className="a-label">{L.labelFacts}</div>
          {state.facts_extracted.map((f, i) => (
            <div key={i} className="a-item">✓ {f}</div>
          ))}
          <div className="a-label">{L.labelDiss}</div>
          <div className="a-dissolving">{state.current_narrative_being_shredded}</div>
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
