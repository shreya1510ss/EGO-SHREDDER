function Header({ language, onToggle }) {
  return (
    <header>
      <div className="dot"></div>
      <h1>Ego Shredder</h1>
      <div className="lang-toggle" onClick={onToggle} title="Switch language">
        <div className={`lang-opt ${language === 'english' ? 'active' : ''}`}>EN</div>
        <div className={`lang-opt ${language === 'hindi' ? 'active' : ''}`}>हिं</div>
      </div>
    </header>
  )
}

export default Header
