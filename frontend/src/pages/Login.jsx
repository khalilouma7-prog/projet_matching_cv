import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from "../services/api"

const FEATURES = [
  
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
      const res = await api.post('/users/auth/login/', { email: form.email, password: form.password })
      localStorage.setItem('user', JSON.stringify(res.data.user))
      navigate('/dashboard')
    } catch { setErreur('Identifiants incorrects') }
    finally { setLoading(false) }
  }

  return (
    <div style={S.page}>
      {/* Gauche */}
      <div style={S.left}>
        <div style={S.brand}></div>
        <h1 style={S.heroTitle}>
         <br/>
          <span style={{ color: '#4f6ef7' }}></span><br/>
        </h1>
        <p style={S.heroSub}></p>
        <div style={S.features}>
          {FEATURES.map(f => (
            <div key={f.text} style={S.feature}>
              <span style={S.fIcon}>{f.icon}</span>
              <span style={S.fText}>{f.text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Droite */}
      <div style={S.right}>
        <div style={S.card}>
          <h2 style={S.cardTitle}>Connexion</h2>
          <p style={S.cardSub}>Accédez à votre tableau de bord</p>
          {erreur && <div style={S.error}>{erreur}</div>}
          <form onSubmit={handleSubmit}>
            <div style={S.group}>
              <label style={S.label}>EMAIL</label>
              <input style={S.input} type="email" placeholder="vous@email.com"
                value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
            </div>
            <div style={S.group}>
              <label style={S.label}>MOT DE PASSE</label>
              <input style={S.input} type="password" placeholder="••••••••"
                value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
            </div>
            <button style={S.btn} type="submit" disabled={loading}>
              {loading ? 'Connexion…' : 'Se connecter →'}
            </button>
          </form>
          <p style={S.linkRow}>
            Pas encore de compte ?{' '}
            <Link to="/register" style={{ color: '#4f6ef7', fontWeight: 600 }}>S'inscrire</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

const S = {
  page:      { display:'flex', minHeight:'100vh', background:'#f5f6fa', fontFamily:'Inter,sans-serif' },
  left: { 
  flex:1, 
  padding:'60px 70px', 
  display:'flex', 
  flexDirection:'column', 
  justifyContent:'center',
  backgroundImage: 'url(/bg-login.jpg)',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  position: 'relative',
},
  brand:     { fontSize:12, fontWeight:700, color:'#4f6ef7', letterSpacing:2, marginBottom:48 },
  heroTitle: { fontSize:46, fontWeight:900, color:'#1a1d2e', lineHeight:1.15, margin:'0 0 20px', fontFamily:'Manrope,sans-serif' },
  heroSub:   { fontSize:15, color:'#6b7280', lineHeight:1.7, marginBottom:40, maxWidth:460 },
  features:  { display:'flex', flexDirection:'column', gap:14, maxWidth:460 },
  feature:   { display:'flex', alignItems:'center', gap:14 },
  fIcon:     { width:38, height:38, borderRadius:10, background:'#fff', display:'flex', alignItems:'center', justifyContent:'center', fontSize:17, flexShrink:0, boxShadow:'0 2px 8px rgba(0,0,0,0.08)' },
  fText:     { fontSize:14, color:'#4a4d6a' },
  right:     { width:480, background:'#fff', display:'flex', alignItems:'center', justifyContent:'center', padding:'40px', boxShadow:'-4px 0 24px rgba(0,0,0,0.06)' },
  card:      { width:'100%', maxWidth:380 },
  cardTitle: { fontSize:28, fontWeight:900, color:'#1a1d2e', marginBottom:6, fontFamily:'Manrope,sans-serif' },
  cardSub:   { fontSize:14, color:'#9095b0', marginBottom:32 },
  error:     { background:'#fff0f0', border:'1px solid #fecaca', color:'#dc2626', padding:'10px 14px', borderRadius:8, marginBottom:16, fontSize:13 },
  group:     { marginBottom:20 },
  label:     { display:'block', fontSize:11, fontWeight:700, color:'#9095b0', letterSpacing:1.2, marginBottom:8 },
  input:     { width:'100%', padding:'12px 14px', background:'#f5f6fa', border:'1.5px solid #e8e9f0', borderRadius:9, fontSize:14, color:'#1a1d2e', outline:'none', boxSizing:'border-box' },
  btn:       { width:'100%', padding:'13px', background:'#4f6ef7', color:'#fff', border:'none', borderRadius:9, fontSize:14, fontWeight:700, cursor:'pointer', marginTop:8 },
  linkRow:   { textAlign:'center', marginTop:24, fontSize:14, color:'#9095b0' },
}