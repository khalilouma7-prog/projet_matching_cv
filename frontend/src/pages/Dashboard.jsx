// frontend/src/pages/Dashboard.jsx
import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { matchingAPI } from "../services/api";
import RadarChart    from "../components/RadarChart";
import WordCloud     from "../components/WordCloud";
import MatchScoreCard from "../components/MatchScoreCard";
import ClusterMap    from "../components/ClusterMap";
import ScoreRing     from "../components/ScoreRing";
import GeoMap        from "../components/GeoMap";
import "./Dashboard.css";

const CLUSTER_COLORS = ["#00e5a0", "#3d7fff", "#a855f7", "#f59e0b", "#ef4444", "#06b6d4"];

export default function Dashboard() {
  const [offers, setOffers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [mapPoints, setMapPoints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("matching_results") || "[]");
    const normalized = stored.map((o, i) => ({
      id: o.job_id ?? i + 1,
      title: o.job || "Offre",
      company: o.company || "N/A",
      location: o.location || "N/A",
      contract: o.contract_type || "N/A",
      score: Math.round(o.final_score || 0),
      color1: "#00e5a0",
      color2: "#3d7fff",
      cluster_id: o.cluster_id ?? 0,
      cosine_score: o.cosine_score || 0,
      jaccard_score: o.jaccard_score || 0,
      experience_score: o.experience_score || 0,
      geo_score: o.geo_score || 0,
      final_score: o.final_score || 0,
      lat: o.lat,
      lng: o.lng,
    }));
    setOffers(normalized);
    setSelected(normalized[0] || null);

    matchingAPI
      .mapOffers()
      .then((response) => setMapPoints(response.data.points || []))
      .finally(() => setLoading(false));
  }, []);

  const radar = selected
    ? [
        { subject: "Cosinus", user: selected.cosine_score, offer: 100 },
        { subject: "Jaccard", user: selected.jaccard_score, offer: 100 },
        { subject: "Experience", user: selected.experience_score, offer: 100 },
        { subject: "Geo", user: selected.geo_score, offer: 100 },
        { subject: "Final", user: selected.final_score, offer: 100 },
      ]
    : [];

  const words = offers
    .slice(0, 8)
    .map((o, i) => ({ text: o.title, size: 16 + Math.round(o.score / 8), color: CLUSTER_COLORS[i % CLUSTER_COLORS.length], opacity: 0.9 }));

  const dist = [
    { range: "0-20", count: offers.filter((o) => o.score < 20).length },
    { range: "20-40", count: offers.filter((o) => o.score >= 20 && o.score < 40).length },
    { range: "40-60", count: offers.filter((o) => o.score >= 40 && o.score < 60).length },
    { range: "60-80", count: offers.filter((o) => o.score >= 60 && o.score < 80).length },
    { range: "80-100", count: offers.filter((o) => o.score >= 80).length },
  ];

  const clusterMap = {};
  offers.forEach((o) => {
    const k = `Cluster ${o.cluster_id ?? 0}`;
    clusterMap[k] = (clusterMap[k] || 0) + 1;
  });
  const clusters = Object.entries(clusterMap).map(([label, count], i) => ({
    label,
    count,
    color: CLUSTER_COLORS[i % CLUSTER_COLORS.length],
  }));

  const STATS = [
    { label:"Offres matchees",      value:`${offers.length}`, sub:"Issues du dernier upload CV", icon:"📋", color:"var(--accent)" },
    { label:"Score moyen",          value:`${offers.length ? Math.round(offers.reduce((a,b)=>a+b.score,0)/offers.length) : 0}%`, sub:`Top match : ${offers[0]?.score ?? 0}%`, icon:"🎯", color:"#3d7fff" },
    { label:"Points geo",           value:`${mapPoints.length}`, sub:"Offres geolocalisees", icon:"📍", color:"#a855f7" },
    { label:"Clusters identifies",  value:`${clusters.length}`, sub:"K-Means backend", icon:"🗂️", color:"#f59e0b" },
  ];

  return (
    <div className="content">
      {loading && <div className="card" style={{ marginBottom: 12 }}>Chargement des donnees...</div>}
      {!offers.length && !loading && (
        <div className="card" style={{ marginBottom: 12 }}>
          Aucun matching disponible. Uploadez d'abord un CV dans la page Results.
        </div>
      )}

      {/* Stats */}
      <div className="grid-4 fade-in">
        {STATS.map((s, i) => (
          <div key={s.label} className={`stat-card fade-in fade-in-d${i+1}`}
            style={{ "--card-color": s.color }}>
            <div className="stat-icon">{s.icon}</div>
            <div className="stat-label">{s.label}</div>
            <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
            <div className="stat-sub">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Offres + Détail */}
      <div className="grid-3 fade-in fade-in-d2">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Offres recommandées</span>
            <span className="card-badge">{offers.length} affichées</span>
          </div>
          <div className="offer-list">
            {offers.map((o) => (
              <MatchScoreCard key={o.id} offer={o}
                selected={selected?.id === o.id}
                onClick={() => setSelected(o)} />
            ))}
          </div>
        </div>

        <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
          <div className="card">
            <div className="card-header">
              <span className="card-title">{selected?.title}</span>
              <span style={{ fontSize:12, color:"var(--muted)" }}>{selected?.company}</span>
            </div>
            <ScoreRing value={selected?.score ?? 0} />
            <div style={{ marginTop:18 }}>
              <div className="section-label">Sous-scores</div>
              <div className="chips">
                <span className="chip match">Cosine {Math.round(selected?.cosine_score || 0)}%</span>
                <span className="chip">Jaccard {Math.round(selected?.jaccard_score || 0)}%</span>
                <span className="chip">Exp {Math.round(selected?.experience_score || 0)}%</span>
                <span className="chip">Geo {Math.round(selected?.geo_score || 0)}%</span>
              </div>
            </div>
            <button className="btn btn-primary" style={{ width:"100%", marginTop:16, fontSize:13 }} onClick={() => window.location.href="/results"}>
              Aller aux resultats →
            </button>
          </div>

          <div className="card">
            <div className="card-header"><span className="card-title">Profil vs Offre</span></div>
            <RadarChart data={radar} />
          </div>
        </div>
      </div>

      {/* WordCloud + Distribution */}
      <div className="grid-2 fade-in fade-in-d3">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Compétences les + demandées</span>
            <span className="card-badge">807 offres</span>
          </div>
          <WordCloud words={words} />
        </div>

        <div className="card">
          <div className="card-header"><span className="card-title">Distribution des scores</span></div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={dist} barSize={28}>
              <XAxis dataKey="range" tick={{ fill:"#6b7280", fontSize:11 }} axisLine={false} tickLine={false}/>
              <YAxis tick={{ fill:"#6b7280", fontSize:11 }} axisLine={false} tickLine={false}/>
              <Tooltip contentStyle={{ background:"var(--surface2)", border:"1px solid var(--border)", borderRadius:8, fontSize:12 }} cursor={false}/>
              <Bar dataKey="count" radius={[4,4,0,0]}>
                {dist.map((_,i) => <Cell key={i} fill={i >= 3 ? "#00e5a0" : "#1e2430"}/>)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Clusters */}
      <div className="card fade-in fade-in-d4">
        <div className="card-header">
          <span className="card-title">Clustering K-Means des offres</span>
          <span className="card-badge">{clusters.length} clusters</span>
        </div>
        <ClusterMap clusters={clusters} />
      </div>

      <div className="card fade-in fade-in-d4" style={{ marginTop: 16 }}>
        <div className="card-header">
          <span className="card-title">Carte geographique</span>
          <span className="card-badge">{mapPoints.length} points</span>
        </div>
        <GeoMap offers={mapPoints} />
      </div>
    </div>
  );
}