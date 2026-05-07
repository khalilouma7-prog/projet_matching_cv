import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts'

export default function Resultats() {
  const [data, setData] = useState(null)
  const [selectionne, setSelectionne] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const stored = localStorage.getItem('resultats')
    if (stored) setData(JSON.parse(stored))
    else navigate('/dashboard')
  }, [])

  if (!data) return <p>Chargement...</p>

  const radarData = selectionne ? [
    { critere: 'Texte', score: selectionne.score_cosinus },
    { critere: 'Compétences', score: selectionne.score_jaccard },
    { critere: 'Expérience', score: selectionne.score_experience },
    { critere: 'Localisation', score: selectionne.score_geo },
  ] : []

  const getColor = (score) => {
    if (score >= 60) return '#2dc653'
    if (score >= 30) return '#f4a261'
    return '#e63946'
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>🎯 Résultats du Matching</h2>
        <button onClick={() => navigate('/dashboard')} style={styles.btnBack}>
          ← Retour
        </button>
      </div>

      <p style={{color:'#666'}}>
        ✅ <strong>{data.competences_cv?.length}</strong> compétences détectées dans votre CV :
        {' '}{data.competences_cv?.join(', ')}
      </p>

      <div style={styles.grid}>

        {/* Liste des offres */}
        <div style={styles.liste}>
          <h3>📋 {data.total_offres} offres analysées</h3>
          {data.resultats?.map((offre, i) => (
            <div
              key={i}
              style={{
                ...styles.offreCard,
                border: selectionne?.offre_id === offre.offre_id
                  ? '2px solid #4361ee' : '2px solid transparent'
              }}
              onClick={() => setSelectionne(offre)}
            >
              <div style={{display:'flex', justifyContent:'space-between'}}>
                <div>
                  <strong>{offre.titre}</strong>
                  <p style={{margin:'4px 0', color:'#666', fontSize:'0.9rem'}}>
                    🏢 {offre.entreprise} | 📍 {offre.localisation}
                  </p>
                  <span style={styles.badge}>{offre.type_contrat}</span>
                </div>
                <div style={{
                  ...styles.score,
                  color: getColor(offre.score_total)
                }}>
                  {offre.score_total}%
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Graphique Radar */}
        {selectionne && (
          <div style={styles.detail}>
            <h3>📊 Analyse : {selectionne.titre}</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="critere" />
                <Radar
                  dataKey="score"
                  stroke="#4361ee"
                  fill="#4361ee"
                  fillOpacity={0.4}
                />
              </RadarChart>
            </ResponsiveContainer>

            <div style={styles.scores}>
              <div style={styles.scoreItem}>
                <span>📝 Similarité texte</span>
                <strong>{selectionne.score_cosinus}%</strong>
              </div>
              <div style={styles.scoreItem}>
                <span>🛠️ Compétences</span>
                <strong>{selectionne.score_jaccard}%</strong>
              </div>
              <div style={styles.scoreItem}>
                <span>📅 Expérience</span>
                <strong>{selectionne.score_experience}%</strong>
              </div>
              <div style={styles.scoreItem}>
                <span>📍 Localisation</span>
                <strong>{selectionne.score_geo}%</strong>
              </div>
            </div>

            <a href={selectionne.url} target="_blank" rel="noreferrer"
               style={styles.btnOffre}>
              Voir l'offre complète →
            </a>
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  container: { minHeight:'100vh', background:'#f0f2f5', padding:'2rem' },
  header: { display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1rem' },
  grid: { display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1.5rem', marginTop:'1rem' },
  liste: { background:'white', borderRadius:'12px', padding:'1.5rem', maxHeight:'80vh', overflowY:'auto' },
  offreCard: { padding:'1rem', marginBottom:'0.75rem', borderRadius:'8px', background:'#f8f9fa', cursor:'pointer' },
  score: { fontSize:'1.5rem', fontWeight:'bold' },
  badge: { background:'#e8f4fd', color:'#4361ee', padding:'2px 8px', borderRadius:'4px', fontSize:'0.8rem' },
  detail: { background:'white', borderRadius:'12px', padding:'1.5rem' },
  scores: { marginTop:'1rem' },
  scoreItem: { display:'flex', justifyContent:'space-between', padding:'0.5rem 0', borderBottom:'1px solid #eee' },
  btnBack: { padding:'0.5rem 1rem', background:'#4361ee', color:'white', border:'none', borderRadius:'8px', cursor:'pointer' },
  btnOffre: { display:'block', marginTop:'1rem', padding:'0.75rem', background:'#4361ee', color:'white', textAlign:'center', borderRadius:'8px', textDecoration:'none' }
}