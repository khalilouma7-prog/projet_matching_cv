// frontend/src/pages/Results.jsx
import { useMemo, useState } from "react";
import ScoreRing  from "../components/ScoreRing";
import RadarChart from "../components/RadarChart";
import GeoMap     from "../components/GeoMap";
import { matchingAPI } from "../services/api";
import "./Results.css";

const CONTRACTS = ["Tous", "CDI", "CDD", "Stage", "Freelance"];
const SC = (s) => s>=80?"#00e5a0":s>=60?"#f59e0b":"#ff6b6b";

export default function Results() {
  const [offers, setOffers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("Tous");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const filtered = useMemo(
() => (filter === "Tous" ? offers : offers.filter((o) => o.contract?.includes(filter))),    [filter, offers]
  );

  const radarData = useMemo(() => {
    if (!selected) return [];
    return [
      { subject: "Cosinus", user: selected.cosine_score, offer: 100 },
      { subject: "Jaccard", user: selected.jaccard_score, offer: 100 },
      { subject: "Experience", user: selected.experience_score, offer: 100 },
      { subject: "Geo", user: selected.geo_score, offer: 100 },
      { subject: "Final", user: selected.final_score, offer: 100 },
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
          <button key={c} className={`filter-btn${filter===c?" active":""}`}
            onClick={() => setFilter(c)}>{c}</button>
        ))}
        <span className="filter-count">{filtered.length} offres</span>
      </div>

      <div className="results-layout fade-in fade-in-d1">
        {/* Liste */}
        <div className="results-list">
          {!filtered.length && !loading && (
            <div className="card">Aucun resultat. Uploadez un CV pour demarrer.</div>
          )}
          {filtered.map((o, index) => (
            <div key={o.id} className={`result-row${selected?.id===o.id?" selected":""}`}
              onClick={() => setSelected(o)}>
              <div className="result-logo"
                style={{ background:"linear-gradient(135deg,#00e5a0,#3d7fff)" }}>{index + 1}</div>
              <div className="result-info">
                <div className="result-title">{o.job}</div>
                <div className="result-meta">
                  <span>{o.company || "N/A"}</span><span>📍 {o.location || "N/A"}</span>
                  <span className="tag">Cluster {o.cluster_id}</span>
                </div>
                <div className="score-bar-wrap">
                  <div className="score-bar-fill" style={{ width:`${o.final_score}%`, background:SC(o.final_score) }}/>
                </div>
              </div>
              <div className="result-score" style={{ color:SC(o.final_score) }}>{o.final_score}%</div>
            </div>
          ))}
        </div>

        {/* Détail */}
        {selected && (
          <div className="results-detail">
            <div className="card" style={{ marginBottom:16 }}>
              <div style={{ display:"flex", alignItems:"center", gap:14, marginBottom:16 }}>
                <div className="detail-logo"
                  style={{ background:"linear-gradient(135deg,#00e5a0,#3d7fff)" }}>
                  📌
                </div>
                <div>
                  <div className="detail-title">{selected.job}</div>
                  <div className="detail-sub">{selected.company} · 📍 {selected.location}</div>
                </div>
              </div>
              <ScoreRing value={selected.final_score} />
              {/* Formule */}
              <div className="formula-grid" style={{ marginTop:18 }}>
                {[
                  { label:"Cosinus TF-IDF", val:Math.round(selected.cosine_score)+"%",  w:"×0.50", c:"var(--accent)" },
                  { label:"Jaccard Skills", val:Math.round(selected.jaccard_score)+"%", w:"×0.25", c:"#3d7fff" },
                  { label:"Exp. Match",     val:Math.round(selected.experience_score)+"%",w:"×0.15", c:"#a855f7" },
                  { label:"Geo Match",      val:Math.round(selected.geo_score)+"%",w:"×0.10", c:"#f59e0b" },
                ].map((m) => (
                  <div key={m.label} className="formula-item">
                    <div className="formula-label">{m.label}</div>
                    <div className="formula-value" style={{ color:m.c }}>{m.val}</div>
                    <div className="formula-weight">{m.w}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card" style={{ marginBottom:16 }}>
              <div className="card-header"><span className="card-title">Profil vs Offre</span></div>
              <RadarChart data={radarData} />
            </div>

            <div className="card" style={{ marginBottom:16 }}>
              <div className="card-header"><span className="card-title">Analyse du clustering</span></div>
              <div className="chips" style={{ marginBottom:12 }}>
                <span className="chip match">Cluster K-Means: {selected.cluster_id}</span>
                <span className="chip">Job ID: {selected.job_id}</span>
              </div>
            </div>

            <div className="card">
              <div className="card-header"><span className="card-title">Localisation</span></div>
              <GeoMap offers={[selected]} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}