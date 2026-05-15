import { useEffect, useState } from "react";
import { profileAPI } from "../services/api";
import "./Profile.css";

const DEFAULT_SKILLS = ["Python","NLP","scikit-learn","Pandas","SQL","spaCy","Machine Learning"];

export default function Profile({ user }) {
  const [form, setForm] = useState({
    name: user?.name || "",
    email: user?.email || "",
    phone: "+212 6XX XXX XXX",
    location: "",
    formation: "Licence IASD — 2025/2026",
    experience: "0",
    summary: "",
  });
  const [skills, setSkills] = useState(DEFAULT_SKILLS);
  const [newSkill, setNewSkill] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const [historique, setHistorique] = useState([]);
  const userId = user?.id;

  useEffect(() => {
    if (!userId) return;
    profileAPI.get(userId).then((res) => {
      const p = res.data.profile;
      setForm((prev) => ({
        ...prev,
        name: p.name || prev.name,
        email: p.email || prev.email,
        location: p.city || prev.location,
        experience: String(p.experience_years ?? "0"),
          phone: p.phone || prev.phone, 
        formation: p.education || prev.formation,
      }));
      const skillsFromApi = (p.skills_manual || "")
        .split(",").map((s) => s.trim()).filter(Boolean);
      if (skillsFromApi.length) setSkills(skillsFromApi);
    }).catch(() => {});

    // Charger historique depuis localStorage
    const hist = JSON.parse(localStorage.getItem("matching_history") || "[]");
    setHistorique(hist);
  }, [userId]);

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      if (!userId) {
        setError("Utilisateur non connecté !");
        return;
      }
      await profileAPI.update(userId, {
        name: form.name,
        email: form.email,
        city: form.location,
          phone: form.phone, 
        experience_years: Number(form.experience) || 0,
        skills_manual: skills.join(", "),
        education: form.formation,
      });
      // Met à jour localStorage
      const currentUser = JSON.parse(localStorage.getItem("user") || "{}");
      localStorage.setItem("user", JSON.stringify({
        ...currentUser,
        name: form.name,
        email: form.email,
      }));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch(e) {
      console.error(e);
      setError("Erreur lors de la sauvegarde : " + (e.response?.data?.error || e.message));
    } finally {
      setSaving(false);
    }
  };

  const addSkill = () => {
    const s = newSkill.trim();
    if (s && !skills.includes(s)) { setSkills([...skills, s]); setNewSkill(""); }
  };

  return (
    <div className="content">
      {/* Header */}
      <div className="profile-header fade-in">
        <div className="profile-avatar">{(form.name||"?").slice(0,2).toUpperCase()}</div>
        <div>
          <div className="profile-name">{form.name || "Mon Profil"}</div>
          <div className="profile-sub">Data Science · {form.formation}</div>
        </div>
        <div style={{ marginLeft:"auto", display:"flex", flexDirection:"column", alignItems:"flex-end", gap:6 }}>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? "Sauvegarde…" : saved ? "✓ Sauvegardé !" : "Sauvegarder"}
          </button>
          {error && <div style={{ fontSize:12, color:"#dc2626" }}>{error}</div>}
          {saved && <div style={{ fontSize:12, color:"#059669" }}>✓ Profil mis à jour !</div>}
        </div>
      </div>

      <div className="grid-2 fade-in fade-in-d1">
        {/* Gauche */}
        <div>
          <div className="card" style={{ marginBottom:20 }}>
            <div className="card-header">
              <span className="card-title">Informations personnelles</span>
            </div>
            {[
              ["Nom complet","name","text"],
              ["Email","email","email"],
              ["Téléphone","phone","tel"],
              ["Localisation","location","text"],
            ].map(([l,k,t]) => (
              <div className="form-group" key={k}>
                <label className="form-label">{l}</label>
                <input className="form-input" type={t} value={form[k]} onChange={update(k)}/>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title">Formation & Expérience</span>
            </div>
            <div className="form-group">
              <label className="form-label">Niveau d'études</label>
              <input className="form-input" value={form.formation} onChange={update("formation")}/>
            </div>
            <div className="form-group">
              <label className="form-label">Années d'expérience</label>
              <input className="form-input" type="number" value={form.experience} onChange={update("experience")}/>
            </div>
            <div className="form-group" style={{ marginBottom:0 }}>
              <label className="form-label">Résumé</label>
              <textarea className="form-input" value={form.summary} onChange={update("summary")}/>
            </div>
          </div>
        </div>

        {/* Droite */}
        <div>
          <div className="card" style={{ marginBottom:20 }}>
            <div className="card-header">
              <span className="card-title">Compétences</span>
              <span className="card-badge">{skills.length} skills</span>
            </div>
            <div className="chips" style={{ marginBottom:16 }}>
              {skills.map((s) => (
                <span key={s} className="chip match skill-chip"
                  onClick={() => setSkills(skills.filter((x) => x !== s))}
                  title="Cliquer pour retirer">
                  ✓ {s} ×
                </span>
              ))}
            </div>
            <div style={{ display:"flex", gap:8 }}>
              <input className="form-input" placeholder="Ajouter une compétence…"
                value={newSkill} onChange={(e) => setNewSkill(e.target.value)}
                onKeyDown={(e) => e.key==="Enter" && addSkill()} style={{ flex:1 }}/>
              <button className="btn btn-primary" style={{ fontSize:12 }} onClick={addSkill}>+</button>
            </div>
          </div>

          {/* ✅ Historique des matchings */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Historique des matchings</span>
              <span className="card-badge">{historique.length} analyses</span>
            </div>
            {historique.length === 0 ? (
              <div className="db-empty">
                <div className="db-empty-icon">📂</div>
                <div className="db-empty-text">Aucun matching effectué</div>
                <div style={{ fontSize:12, color:"var(--muted)", marginTop:4 }}>
                  Uploadez un CV dans "Mes résultats"
                </div>
              </div>
            ) : (
              <div className="historique-table">
                <div className="hist-header">
                  <span>Date</span>
                  <span>Fichier CV</span>
                  <span>Top Match</span>
                  <span>Offres</span>
                </div>
                {historique.map((h, i) => (
                  <div key={i} className="hist-row">
                    <span className="hist-date">{h.date}</span>
                    <span className="hist-file">📄 {h.filename}</span>
                    <span className="hist-score" style={{
                      color: h.topScore >= 60 ? "#059669" : h.topScore >= 40 ? "#d97706" : "#dc2626"
                    }}>{h.topScore}%</span>
                    <span className="hist-count">{h.total} offres</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}