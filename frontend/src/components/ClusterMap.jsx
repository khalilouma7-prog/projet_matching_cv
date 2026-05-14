// frontend/src/components/ClusterMap.jsx
import "./ClusterMap.css";

// clusters = [{ label, color, count }, ...]
export default function ClusterMap({ clusters = [] }) {
  return (
    <div className="cluster-grid">
      {clusters.map((c) => (
        <div key={c.label} className="cluster-card">
          <div className="cluster-icon" style={{ background:`${c.color}22` }}>
            <div className="cluster-dot" style={{ background: c.color }} />
          </div>
          <div className="cluster-label">{c.label}</div>
          <div className="cluster-count" style={{ color: c.color }}>{c.count}</div>
          <div className="cluster-sub">offres</div>
        </div>
      ))}
    </div>
  );
}