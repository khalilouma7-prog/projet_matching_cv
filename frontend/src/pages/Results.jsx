import { useMemo, useState, useEffect } from "react";
import ScoreRing from "../components/ScoreRing";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend } from "recharts";
import GeoMap from "../components/GeoMap";
import { matchingAPI, resultsAPI } from "../services/api";
import "./Results.css";

const CONTRACTS = ["Tous", "CDI", "CDD", "Stage", "Freelance"];
const SC = (s) => (s >= 80 ? "#00e5a0" : s >= 60 ? "#f59e0b" : "#ff6b6b");

export default function Results() {
  const [offers, setOffers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("Tous");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Au chargement du composant, on essaie de récupérer l'historique récent
  useEffect(() => {
    const storedOffers = localStorage.getItem("matching_results");
    if (storedOffers) {
      const parsedOffers = JSON.parse(storedOffers);
      setOffers(parsedOffers);
      if (parsedOffers.length > 0) setSelected(parsedOffers[0]);
    } else {
      // Sinon, on va chercher sur le backend
      setLoading(true);
      resultsAPI.getDashboardStats() // On peut utiliser get() ou getDashboardStats() selon ce qui renvoie l'historique
        .then(res => {
            // Note: Adapte cette ligne si l'API renvoie les résultats sous une autre forme
            const data = res.data.results || [];
            setOffers(data);
            if(data.length > 0) setSelected(data[0]);
        })
        .catch(err => console.error("Erreur de chargement initial:", err))
        .finally(() => setLoading(false));
    }
  }, []);

  const filtered = useMemo(
    () => (filter === "Tous" ? offers : offers.filter((o) => o.contract?.includes(filter))),
    [filter, offers]
  );

  // --- DONNÉES DU RADAR CHART (Adapté pour les compétences) ---
  const radarData = useMemo(() => {
    if (!selected) return [];
    
    // Si ton backend renvoie un score par compétence (ex: {"Python": 80, "React": 50}), utilise-le ici.
    // Pour l'instant, on met des données fixes pour la démonstration comme demandé.
    return [
      { subject: "Python",        user: 85, offer: 90 },
      { subject: "Machine Learning", user: 70, offer: 80 },
      { subject: "SQL", user: 90, offer: 75 },
      { subject: "React", user: 60, offer: 50 },
      { subject: "Communication", user: 80, offer: 85 },
      { subject: "Gestion", user: 50, offer: 70 },
    ];
  }, [selected]);

 const handleUpload = async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;

  try {
    setLoading(true);
    setError("");
    const response = await matchingAPI.uploadCV(file);
    const data = response.data;
    const nextOffers = data.results || [];
    localStorage.setItem("matching_results", JSON.stringify(nextOffers));
    setOffers(nextOffers);
    setSelected(nextOffers[0] || null);

    // ✅ Sauvegarde dans l'historique
    const hist = JSON.parse(localStorage.getItem("matching_history") || "[]");
    hist.unshift({
      date: new Date().toLocaleDateString("fr-FR"),
      filename: file.name,
      topScore: nextOffers[0]?.final_score || 0,
      total: nextOffers.length,
    });
    localStorage.setItem("matching_history", JSON.stringify(hist.slice(0, 10)));

  } catch (err) {
    setError(err?.response?.data?.error || "Erreur lors du matching CV.");
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="content">
      <div className="results-upload card fade-in">
        <div className="card-header">
          <span className="card-title">Lancer le matching depuis votre CV</span>
        </div>
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={handleUpload}
          className="upload-input"
        />
        {loading && <div className="upload-status">Analyse en cours...</div>}
        {!!error && <div className="upload-error">{error}</div>}
      </div>

      {/* Filtres */}
      <div className="results-filters fade-in">
        <span className="filter-label">Contrat :</span>
        {CONTRACTS.map((c) => (
          <button
            key={c}
            className={`filter-btn${filter === c ? " active" : ""}`}
            onClick={() => setFilter(c)}
          >
            {c}
          </button>
        ))}
        <span className="filter-count">{filtered.length} offres</span>
      </div>

      <div className="results-layout fade-in fade-in-d1">
        {/* Liste */}
        <div className="results-list">
          {!filtered.length && !loading && (
            <div className="card">Aucun résultat. Uploadez un CV pour démarrer.</div>
          )}
          {filtered.map((o, index) => (
            <div
              key={o.id || index} // ✅ CORRECTION DE L'ERREUR REACT ICI
              className={`result-row${selected?.id === o.id ? " selected" : ""}`}
              onClick={() => setSelected(o)}
            >
              <div
                className="result-logo"
                style={{ background: "linear-gradient(135deg,#00e5a0,#3d7fff)" }}
              >
                {index + 1}
              </div>
              <div className="result-info">
                <div className="result-title">{o.job || o.job_title}</div>
                <div className="result-meta">
                  <span>{o.company || "N/A"}</span>
                  <span>📍 {o.location || "N/A"}</span>
                  <span className="tag">Cluster {o.cluster_id || "N/A"}</span>
                </div>
                <div className="score-bar-wrap">
                  <div
                    className="score-bar-fill"
                    style={{ width: `${o.final_score}%`, background: SC(o.final_score) }}
                  />
                </div>
              </div>
              <div className="result-score" style={{ color: SC(o.final_score) }}>
                {Math.round(o.final_score)}%
              </div>
            </div>
          ))}
        </div>

        {/* Détail */}
        {selected && (
          <div className="results-detail">
            <div className="card" style={{ marginBottom: 16 }}>
              {/* Header */}
              <div style={{ display: "flex", alignItems: "flex-start", gap: 14, marginBottom: 16 }}>
                <div
                  className="detail-logo"
                  style={{ background: "linear-gradient(135deg,#4f6ef7,#7c3aed)" }}
                >
                  📌
                </div>
                <div style={{ flex: 1 }}>
                  <div className="detail-title">{selected.job || selected.job_title}</div>
                  <div className="detail-sub">
                    🏢 {selected.company} · 📍 {selected.location}
                  </div>
                  {selected.sector && (
                    <span className="chip" style={{ marginTop: 6, display: "inline-block" }}>
                      🏷️ {selected.sector}
                    </span>
                  )}
                </div>
                {selected.url && (
                  <a
                    href={selected.url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-ghost"
                    style={{ fontSize: 11 }}
                  >
                    Voir l'offre →
                  </a>
                )}
              </div>

              {/* Score Ring */}
              <ScoreRing value={selected.final_score} />

              {/* Infos clés */}
              <div className="detail-info-grid" style={{ marginTop: 16 }}>
                <div className="detail-info-item">
                  <div className="detail-info-label">Contrat</div>
                  <div className="detail-info-val">{selected.contract || "N/A"}</div>
                </div>
                <div className="detail-info-item">
                  <div className="detail-info-label">Expérience</div>
                  <div className="detail-info-val">{selected.experience || "Non précisé"}</div>
                </div>
                <div className="detail-info-item">
                  <div className="detail-info-label">Cluster</div>
                  <div className="detail-info-val">K-Means #{selected.cluster_id || "N/A"}</div>
                </div>
                <div className="detail-info-item">
                  <div className="detail-info-label">Score final</div>
                  <div
                    className="detail-info-val"
                    style={{ color: SC(selected.final_score), fontWeight: 700 }}
                  >
                    {Math.round(selected.final_score)}%
                  </div>
                </div>
              </div>

              {/* Skills */}
              {selected.skills?.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <div className="section-label">Compétences requises</div>
                  <div className="chips">
                    {selected.skills.slice(0, 10).map((s, i) => (
                      <span key={i} className={`chip${s.startsWith('[Hard]') ? ' match' : ''}`}>
                        {s.replace('[Hard] ', '🔧 ').replace('[Soft] ', '💬 ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Formule scores */}
              <div className="formula-grid" style={{ marginTop: 16 }}>
                {[
                  { label: "Cosinus TF-IDF", val: Math.round(selected.cosine_score || 0) + "%", w: "×0.50", c: "#4f6ef7" },
                  { label: "Jaccard Skills", val: Math.round(selected.jaccard_score || 0) + "%", w: "×0.25", c: "#7c3aed" },
                  { label: "Exp. Match", val: Math.round(selected.experience_score || 0) + "%", w: "×0.15", c: "#059669" },
                  { label: "Geo Match", val: Math.round(selected.geo_score || 0) + "%", w: "×0.10", c: "#d97706" },
                ].map((m) => (
                  <div key={m.label} className="formula-item">
                    <div className="formula-label">{m.label}</div>
                    <div className="formula-value" style={{ color: m.c }}>{m.val}</div>
                    <div className="formula-weight">{m.w}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Radar - Mis à jour pour utiliser les compétences */}
            <div className="card" style={{ marginBottom: 16 }}>
              <div className="card-header">
                <span className="card-title">Profil vs Offre</span>
              </div>
              <div style={{ width: "100%", height: 300 }}>
                  <ResponsiveContainer>
                    <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                      <PolarGrid stroke="#e8e9f0" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--muted)', fontSize: 11, fontWeight: 600 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                      <Radar name="Votre CV" dataKey="user" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.4} />
                      <Radar name="Compétences Requises" dataKey="offer" stroke="#00e5a0" fill="#00e5a0" fillOpacity={0.4} />
                      <Tooltip contentStyle={{ borderRadius: 8, border: "none", boxShadow: "var(--shadow-md)" }} />
                      <Legend wrapperStyle={{ fontSize: 12, marginTop: 10 }} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
            </div>

            {/* Carte */}
            <div className="card">
              <div className="card-header">
                <span className="card-title">Localisation</span>
              </div>
              <GeoMap offers={[selected]} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}