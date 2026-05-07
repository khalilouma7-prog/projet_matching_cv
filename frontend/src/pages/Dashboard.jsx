import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function Dashboard() {
  const [cvFile, setCvFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const navigate = useNavigate()

  const handleUploadCV = async () => {
    if (!cvFile) return setMessage('Veuillez choisir un fichier')
    const formData = new FormData()
    formData.append('cv_file', cvFile)
    try {
      await api.post('/users/upload-cv/', formData)
      setMessage('✅ CV uploadé avec succès !')
    } catch {
      setMessage('❌ Erreur upload CV')
    }
  }

  const handleMatching = async () => {
    setLoading(true)
    setMessage('⏳ Analyse en cours...')
    try {
      const res = await api.post('/matching/lancer/')
      localStorage.setItem('resultats', JSON.stringify(res.data))
      navigate('/resultats')
    } catch {
      setMessage('❌ Erreur matching. Uploadez votre CV d\'abord.')
    }
    setLoading(false)
  }

  const handleLogout = () => {
    localStorage.clear()
    navigate('/login')
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.titre}>🎯 CV Matching Dashboard</h1>
        <button onClick={handleLogout} style={styles.btnLogout}>Déconnexion</button>
      </div>

      <div style={styles.grid}>

        {/* Card Upload CV */}
        <div style={styles.card}>
          <h3>📄 Mon CV</h3>
          <p style={{color:'#666'}}>Uploadez votre CV en PDF ou DOCX</p>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={e => setCvFile(e.target.files[0])}
            style={{margin: '1rem 0', display:'block'}}
          />
          <button onClick={handleUploadCV} style={styles.btn}>
            Uploader le CV
          </button>
        </div>

        {/* Card Lancer Matching */}
        <div style={styles.card}>
          <h3>🔍 Analyser mon profil</h3>
          <p style={{color:'#666'}}>
            Notre algorithme va comparer votre CV avec toutes les offres disponibles
          </p>
          <br/>
          <button
            onClick={handleMatching}
            style={{...styles.btn, background: loading ? '#ccc' : '#e63946'}}
            disabled={loading}
          >
            {loading ? '⏳ Analyse...' : '🚀 Lancer le Matching'}
          </button>
        </div>

      </div>

      {message && <p style={styles.message}>{message}</p>}
    </div>
  )
}

const styles = {
  container: { minHeight:'100vh', background:'#f0f2f5', padding:'2rem' },
  header: { display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'2rem' },
  titre: { color:'#1a1a2e', margin:0 },
  grid: { display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(300px, 1fr))', gap:'1.5rem' },
  card: { background:'white', padding:'1.5rem', borderRadius:'12px', boxShadow:'0 2px 10px rgba(0,0,0,0.08)' },
  btn: { padding:'0.75rem 1.5rem', background:'#4361ee', color:'white', border:'none', borderRadius:'8px', cursor:'pointer', fontSize:'1rem' },
  btnLogout: { padding:'0.5rem 1rem', background:'#e63946', color:'white', border:'none', borderRadius:'8px', cursor:'pointer' },
  message: { marginTop:'1.5rem', padding:'1rem', background:'white', borderRadius:'8px', textAlign:'center', fontSize:'1.1rem' }
}