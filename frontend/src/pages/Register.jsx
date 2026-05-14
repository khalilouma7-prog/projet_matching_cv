import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from "../services/api"

export default function Register() {
  const [form, setForm] = useState({
    username: '', email: '', password: '',
    localisation: '', experience_annees: 0
  })
  const [erreur, setErreur] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await api.post('/users/auth/register/', {
        name: form.username,
        email: form.email,
        password: form.password,
        city: form.localisation,
        experience_years: form.experience_annees,
      })
      localStorage.setItem('user', JSON.stringify(res.data.user))
      navigate('/dashboard')
    } catch (err) {
      console.error('ERREUR:', err.response?.data || err.message)  // ← ajouté
      setErreur('Erreur lors de l\'inscription')
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.titre}>📝 Inscription</h2>

        {erreur && <p style={styles.erreur}>{erreur}</p>}

        <form onSubmit={handleSubmit}>
          <input style={styles.input} placeholder="Nom d'utilisateur"
            onChange={e => setForm({...form, username: e.target.value})} />
          <input style={styles.input} placeholder="Email" type="email"
            onChange={e => setForm({...form, email: e.target.value})} />
          <input style={styles.input} placeholder="Mot de passe" type="password"
            onChange={e => setForm({...form, password: e.target.value})} />
          <input style={styles.input} placeholder="Ville (ex: Casablanca)"
            onChange={e => setForm({...form, localisation: e.target.value})} />
          <input style={styles.input} placeholder="Années d'expérience" type="number"
            onChange={e => setForm({...form, experience_annees: parseInt(e.target.value)})} />
          <button style={styles.btn} type="submit">S'inscrire</button>
        </form>

        <p style={{textAlign:'center', marginTop:'1rem'}}>
          Déjà un compte ? <Link to="/login">Se connecter</Link>
        </p>
      </div>
    </div>
  )
}

const styles = {
  container: { minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center', background:'#f0f2f5' },
  card: { background:'white', padding:'2rem', borderRadius:'12px', boxShadow:'0 4px 20px rgba(0,0,0,0.1)', width:'100%', maxWidth:'400px' },
  titre: { textAlign:'center', marginBottom:'1.5rem', color:'#1a1a2e' },
  input: { width:'100%', padding:'0.75rem', marginBottom:'1rem', borderRadius:'8px', border:'1px solid #ddd', fontSize:'1rem', boxSizing:'border-box' },
  btn: { width:'100%', padding:'0.75rem', background:'#4361ee', color:'white', border:'none', borderRadius:'8px', fontSize:'1rem', cursor:'pointer' },
  erreur: { color:'red', textAlign:'center' }
}