// frontend/src/components/Topbar.jsx
import { useNavigate } from "react-router-dom";
import "./Topbar.css";

const TITLES = {
  dashboard: "Dashboard",
  results:   "Résultats de matching",
  profile:   "Mon profil",
};

export default function Topbar({ page, setPage, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate("/login");
  };

  return (
    <div className="topbar">
      <div className="page-title">{TITLES[page] || "Dashboard"}</div>
      <div className="topbar-actions">
        <button className="btn btn-ghost" style={{ fontSize: 12 }}>
          🔔 Alertes
        </button>
        <button
          className="btn btn-primary"
          style={{ fontSize: 12 }}
          onClick={() => { setPage("results"); navigate("/results"); }}
        >
          🎯 Lancer matching
        </button>
        <button className="btn btn-ghost" style={{ fontSize: 12 }} onClick={handleLogout}>
          Déconnexion
        </button>
      </div>
    </div>
  );
}
