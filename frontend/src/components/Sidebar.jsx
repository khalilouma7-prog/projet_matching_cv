// frontend/src/components/Sidebar.jsx
import { useNavigate } from "react-router-dom";
import "./Sidebar.css";

const NAV = [
  { id:"dashboard", path:"/dashboard", icon:"▦",  label:"Dashboard"    },
  { id:"results",   path:"/results",   icon:"🎯", label:"Mes résultats" },
  { id:"profile",   path:"/profile",   icon:"👤", label:"Mon profil"   },
];

export default function Sidebar({ page, setPage, user }) {
  const navigate = useNavigate();

  const go = (item) => {
    setPage(item.id);
    navigate(item.path);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">◆ <span>CV&Match</span></div>
      <div className="nav-section">Navigation</div>
      {NAV.map((n) => (
        <div key={n.id} className={`nav-item${page===n.id?" active":""}`} onClick={() => go(n)}>
          <span className="nav-icon">{n.icon}</span>{n.label}
        </div>
      ))}
      <div className="sidebar-bottom">
        <div className="user-card">
          <div className="avatar">{(user?.name||"AB").slice(0,2).toUpperCase()}</div>
          <div className="user-info">
            <div className="u-name">{user?.name || "Ahmed Benali"}</div>
            <div className="u-role">IASD · L3</div>
          </div>
        </div>
      </div>
    </aside>
  );
}