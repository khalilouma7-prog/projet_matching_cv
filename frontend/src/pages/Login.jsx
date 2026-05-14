import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from "../services/api"

const FEATURES = [
  { icon: "🔍", text: "Web Scraping automatisé (Rekrute, Indeed…)" },
  { icon: "🧠", text: "Analyse NLP de votre CV avec spaCy + TF-IDF" },
  { icon: "📊", text: "Score pondéré : Cosinus + Jaccard + Exp + Géo" },
  { icon: "🗂️", text: "Clustering K-Means des offres par domaine" },
]

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [erreur, setErreur] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await api.post('/users/auth/login/', {
        email: form.email,
        password: form.password,
      })
      localStorage.setItem('user', JSON.stringify(res.data.user))
      navigate('/dashboard')
    } catch (err) {
      setErreur('Identifiants incorrects')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={S.page}>
      {/* ── Gauche ── */}
      <div style={S.left}>
        <div style={S.brand}>◆ CV&MATCH PLATFORM</div>
        <div style={S.hero}>
          <h1 style={S.heroTitle}>
            Trouvez l'offre<br />
            qui vous <span style={{ color: '#00e5a0' }}>correspond</span><br />
            vraiment.
          </h1>
          <p style={S.heroSub}>
            Intelligence artificielle et Data Mining pour matcher votre profil
            avec les meilleures offres du marché marocain et international.
          </p>
          <div style={S.features}>
            {FEATURES.map((f) => (
              <div key={f.text} style={S.feature}>
                <span style={S.fIcon}>{f.icon}</span>
                <span style={S.fText}>{f.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Droite ── */}
      <div style={S.right}>
        <div style={S.card}>
          <h2 style={S.cardTitle}>Connexion</h2>
          <p style={S.cardSub}>Accédez à votre tableau de bord</p>

          {erreur && <div style={S.error}>{erreur}</div>}

          <form onSubmit={handleSubmit}>
            <div style={S.group}>
              <label style={S.label}>EMAIL</label>
              <input style={S.input} type="email" placeholder="vous@email.com"
                value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
            </div>
            <div style={S.group}>
              <label style={S.label}>MOT DE PASSE</label>
              <input style={S.input} type="password" placeholder="••••••••"
                value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
            </div>
            <button style={S.btn} type="submit" disabled={loading}>
              {loading ? 'Connexion…' : 'Se connecter →'}
            </button>
          </form>

          <p style={S.linkRow}>
            Pas encore de compte ?{' '}
            <Link to="/register" style={{ color: '#00e5a0', fontWeight: 600 }}>S'inscrire</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

const S = {
  page:      { display: 'flex', minHeight: '100vh', background: '#0f1117' },
  left:      { flex: 1, padding: '60px', background: 'linear-gradient(135deg, #0f1117 60%, #0d1f1a)', display: 'flex', flexDirection: 'column', justifyContent: 'center' },
  brand:     { fontSize: 12, fontWeight: 700, color: '#00e5a0', letterSpacing: 2, marginBottom: 48 },
  hero:      { maxWidth: 520 },
  heroTitle: { fontSize: 52, fontWeight: 900, color: '#fff', lineHeight: 1.1, marginBottom: 20, margin: '0 0 20px' },
  heroSub:   { fontSize: 16, color: '#6b7280', lineHeight: 1.7, marginBottom: 40 },
  features:  { display: 'flex', flexDirection: 'column', gap: 14 },
  feature:   { display: 'flex', alignItems: 'center', gap: 14 },
  fIcon:     { width: 36, height: 36, borderRadius: 8, background: '#1a1d27', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, flexShrink: 0 },
  fText:     { fontSize: 14, color: '#9ca3af' },
  right:     { width: 480, background: '#13151c', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px' },
  card:      { width: '100%', maxWidth: 400 },
  cardTitle: { fontSize: 32, fontWeight: 900, color: '#fff', marginBottom: 6 },
  cardSub:   { fontSize: 14, color: '#6b7280', marginBottom: 32 },
  error:     { background: 'rgba(255,80,80,0.1)', border: '1px solid rgba(255,80,80,0.3)', color: '#ff8080', padding: '10px 14px', borderRadius: 8, marginBottom: 16, fontSize: 13 },
  group:     { marginBottom: 20 },
  label:     { display: 'block', fontSize: 11, fontWeight: 700, color: '#6b7280', letterSpacing: 1.2, marginBottom: 8 },
  input:     { width: '100%', padding: '14px 16px', background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, fontSize: 15, color: '#111', outline: 'none', boxSizing: 'border-box' },
  btn:       { width: '100%', padding: '15px', background: '#00e5a0', color: '#0f1117', border: 'none', borderRadius: 10, fontSize: 15, fontWeight: 800, cursor: 'pointer', marginTop: 8, transition: 'background 0.2s' },
  linkRow:   { textAlign: 'center', marginTop: 24, fontSize: 14, color: '#6b7280' },
}