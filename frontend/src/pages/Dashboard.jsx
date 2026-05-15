import { useState, useEffect } from "react";
import { resultsAPI, matchingAPI } from "../services/api";
import WordCloud from "../components/WordCloud";
import GeoMap from "../components/GeoMap";
import "./Dashboard.css";

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [mapPoints, setMapPoints] = useState([]);
  
  const [kpis, setKpis] = useState({ total_offres: 0, domaines_count: 0, cv_analyses: 0, avg_score: 0 });
  const [historyData, setHistoryData] = useState([]);
  const [clustersGlobal, setClustersGlobal] = useState([]);
  const [globalWords, setGlobalWords] = useState([]);

  useEffect(() => {
    resultsAPI.getDashboardStats()
      .then((res) => {
        // LIGNE DE DEBUG : Regarde dans ta console ce qui s'affiche !
        console.log("RÉPONSE DU BACKEND :", res); 
        
        // Sécurité : on s'assure que la donnée existe avant de l'injecter
        const data = res.data || res; // Gère la différence entre Axios et Fetch
        
        if (data.kpis) setKpis(data.kpis);
        if (data.historyData) setHistoryData(data.historyData);
        if (data.clustersGlobal) setClustersGlobal(data.clustersGlobal);
        if (data.globalWords) setGlobalWords(data.globalWords);
      })
      .catch((err) => console.error("Erreur chargement des statistiques:", err));

    matchingAPI.mapOffers()
      .then((res) => setMapPoints(res.data?.points || res.points || []))
      .catch((err) => console.error("Erreur chargement de la carte:", err))
      .finally(() => setLoading(false));
  }, []);

  // Utilisation du "Optional Chaining" (?.) pour éviter les crashs
  const STATS = [
    { label: "Total Offres Scrapées", value: kpis?.total_offres || 0, sub: "Dans la base", icon: "📋", color: "var(--accent)" },
    { label: "Domaines Identifiés", value: kpis?.domaines_count || 0, sub: "K-Means backend", icon: "🗂️", color: "#f59e0b" },
    { label: "Analyses de CV", value: kpis?.cv_analyses || 0, sub: "Historique utilisateur", icon: "📄", color: "#a855f7" },
    { label: "Taux de Match Moyen", value: `${kpis?.avg_score || 0}%`, sub: "Sur vos recherches", icon: "🎯", color: "#3d7fff" },
  ];

  return (
    <div className="content">
      <div style={{ marginBottom: 30 }}>
        <h1>Dashboard Global</h1>
        <p style={{ color: "var(--muted)", margin: "8px 0 0 0" }}>Aperçu du marché de l'emploi et de vos analyses</p>
      </div>

      {loading && <div className="card" style={{ marginBottom: 20 }}>Chargement des données du marché...</div>}

      <div className="grid-4 fade-in">
        {STATS.map((s, i) => (
          <div key={s.label} className={`card fade-in fade-in-d${i + 1}`} style={{ borderBottom: `3px solid ${s.color}` }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <div className="section-label" style={{ margin: 0 }}>{s.label}</div>
              <div style={{ fontSize: 20 }}>{s.icon}</div>
            </div>
            <div style={{ fontSize: 28, fontWeight: 800, color: "var(--text-h)", marginBottom: 4 }}>
              {s.value}
            </div>
            <div style={{ fontSize: 12, color: s.color, fontWeight: 600 }}>{s.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid-3 fade-in fade-in-d2">
        <div className="card" style={{ overflowX: "auto" }}>
          <div className="card-header">
            <span className="card-title">Historique de vos analyses</span>
          </div>
          
          {historyData.length === 0 && !loading ? (
            <div style={{ padding: "20px 0", color: "var(--muted)", fontSize: 14 }}>Aucune analyse trouvée.</div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  <th style={{ padding: "12px 8px", fontSize: 12, color: "var(--muted)", fontWeight: 600 }}>Date</th>
                  <th style={{ padding: "12px 8px", fontSize: 12, color: "var(--muted)", fontWeight: 600 }}>Fichier CV</th>
                  <th style={{ padding: "12px 8px", fontSize: 12, color: "var(--muted)", fontWeight: 600 }}>Top Match</th>
                  <th style={{ padding: "12px 8px", fontSize: 12, color: "var(--muted)", fontWeight: 600 }}>Domaine</th>
                  <th style={{ padding: "12px 8px", fontSize: 12, textAlign: "right" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {historyData.map((row) => (
                  <tr key={row.id} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "16px 8px", fontSize: 13, color: "var(--text)" }}>{row.date}</td>
                    <td style={{ padding: "16px 8px", fontSize: 13, fontWeight: 600, color: "var(--text-h)" }}>{row.cv}</td>
                    <td style={{ padding: "16px 8px" }}>
                      <span className="chip match" style={{ padding: "4px 8px", fontSize: 11 }}>{row.topMatch}</span>
                    </td>
                    <td style={{ padding: "16px 8px", fontSize: 13, color: "var(--text)" }}>{row.domaine}</td>
                    <td style={{ padding: "16px 8px", textAlign: "right" }}>
                      <button className="btn btn-ghost" style={{ padding: "6px 12px", fontSize: 12 }} onClick={() => window.location.href="/results"}>
                        Revoir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Répartition du marché</span>
            <span className="card-badge">K-Means</span>
          </div>
          
          {clustersGlobal.length === 0 && !loading ? (
            <div style={{ padding: "20px 0", color: "var(--muted)", fontSize: 14 }}>Aucun cluster calculé.</div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 10 }}>
              {clustersGlobal.map((cluster, i) => {
                const maxCount = clustersGlobal[0]?.count || 1;
                const width = `${(cluster.count / maxCount) * 100}%`;
                
                return (
                  <div key={i}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 6 }}>
                      <span style={{ fontWeight: 600, color: "var(--text-h)" }}>{cluster.label}</span>
                      <span style={{ color: "var(--muted)" }}>{cluster.count} offres</span>
                    </div>
                    <div style={{ width: "100%", height: 6, background: "var(--surface2)", borderRadius: 10, overflow: "hidden" }}>
                      <div style={{ width: width, height: "100%", background: cluster.color, borderRadius: 10, transition: "width 1s ease-out" }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      <div className="grid-2 fade-in fade-in-d3">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Top Compétences globales</span>
            <span className="card-badge">Tout le marché</span>
          </div>
          {globalWords.length > 0 ? (
            <WordCloud words={globalWords} />
          ) : (
            <div style={{ height: 200, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--muted)" }}>
              {loading ? "Chargement..." : "Pas de données pour le nuage de mots."}
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Carte géographique</span>
            <span className="card-badge">{mapPoints.length} points</span>
          </div>
          <GeoMap offers={mapPoints} />
        </div>
      </div>
    </div>
  );
}