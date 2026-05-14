// frontend/src/pages/Profile.jsx
import { useEffect, useRef, useState } from "react";
import { profileAPI } from "../services/api";
import "./Profile.css";

const DEFAULT_SKILLS = ["Python","NLP","scikit-learn","Pandas","SQL","spaCy","Machine Learning"];

export default function Profile({ user }) {
  const [form, setForm] = useState({
    name: user?.name || "Ahmed Benali", email: user?.email || "ahmed@test.ma",
    phone: "+212 6XX XXX XXX", location: "Rabat, Maroc",
    formation: "Licence IASD — 2025/2026", experience: "1-2 ans (stages)",
    summary: "Étudiant en licence IASD, passionné par le Data Mining et le NLP.",
  });
  const [skills,   setSkills]   = useState(DEFAULT_SKILLS);
  const [newSkill, setNewSkill] = useState("");
  const [cvFile,   setCvFile]   = useState(null);
  const [drag,     setDrag]     = useState(false);
  const [saving,   setSaving]   = useState(false);
  const [saved,    setSaved]    = useState(false);
  const fileRef = useRef();
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
        experience: String(p.experience_years ?? prev.experience),
        formation: p.education || prev.formation,
      }));
      const skillsFromApi = (p.skills_manual || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      if (skillsFromApi.length) setSkills(skillsFromApi);
    }).catch(() => {});
  }, [userId]);

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const handleSave = async () => {
    setSaving(true);
    try {
      if (userId) {
        await profileAPI.update(userId, {
          name: form.name,
          email: form.email,
          city: form.location,
          experience_years: Number(form.experience) || 0,
          skills_manual: skills.join(", "),
          education: form.formation,
        });
      }
      if (cvFile) await profileAPI.uploadCV(cvFile);
      setSaved(true); setTimeout(() => setSaved(false), 2500);
    } finally { setSaving(false); }
  };

  const addSkill = () => {
    const s = newSkill.trim();
    if (s && !skills.includes(s)) { setSkills([...skills, s]); setNewSkill(""); }
  };

  return (
    <div className="content">
      <div className="profile-header fade-in">
        <div className="profile-avatar">{form.name.slice(0,2).toUpperCase()}</div>
        <div>
          <div className="profile-name">{form.name}</div>
          <div className="profile-sub">Data Science · {form.formation}</div>
        </div>
        <button className="btn btn-primary" style={{ marginLeft:"auto" }}
          onClick={handleSave} disabled={saving}>
          {saving ? "Sauvegarde…" : saved ? "✓ Sauvegardé !" : "Sauvegarder"}
        </button>
      </div>

      <div className="grid-2 fade-in fade-in-d1">
        <div>
          <div className="card" style={{ marginBottom:20 }}>
            <div className="card-header"><span className="card-title">Informations personnelles</span></div>
            {[["Nom complet","name","text"],["Email","email","email"],["Téléphone","phone","tel"],["Localisation","location","text"]].map(([l,k,t]) => (
              <div className="form-group" key={k}>
                <label className="form-label">{l}</label>
                <input className="form-input" type={t} value={form[k]} onChange={update(k)}/>
              </div>
            ))}
          </div>
          <div className="card">
            <div className="card-header"><span className="card-title">Formation & Expérience</span></div>
            <div className="form-group">
              <label className="form-label">Niveau d'études</label>
              <input className="form-input" value={form.formation} onChange={update("formation")}/>
            </div>
            <div className="form-group">
              <label className="form-label">Années d'expérience</label>
              <input className="form-input" value={form.experience} onChange={update("experience")}/>
            </div>
            <div className="form-group" style={{ marginBottom:0 }}>
              <label className="form-label">Résumé</label>
              <textarea className="form-input" value={form.summary} onChange={update("summary")}/>
            </div>
          </div>
        </div>

        <div>
          <div className="card" style={{ marginBottom:20 }}>
            <div className="card-header">
              <span className="card-title">Upload du CV</span>
              <span className="card-badge">PDF · DOCX</span>
            </div>
            {!cvFile ? (
              <div className={`upload-zone${drag?" drag":""}`}
                onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
                onDragLeave={() => setDrag(false)}
                onDrop={(e) => { e.preventDefault(); setDrag(false); setCvFile(e.dataTransfer.files[0]); }}
                onClick={() => fileRef.current.click()}>
                <input ref={fileRef} type="file" accept=".pdf,.docx" style={{ display:"none" }}
                  onChange={(e) => setCvFile(e.target.files[0])}/>
                <div className="upload-icon">📄</div>
                <div className="upload-title">Glissez votre CV ici</div>
                <div className="upload-sub">PDF ou DOCX · max 10 MB</div>
                <button className="btn btn-ghost" style={{ marginTop:14, fontSize:12 }}
                  onClick={(e) => { e.stopPropagation(); fileRef.current.click(); }}>
                  Parcourir
                </button>
              </div>
            ) : (
              <div className="cv-uploaded">
                <div style={{ fontSize:28 }}>✅</div>
                <div style={{ flex:1 }}>
                  <div className="cv-filename">{cvFile.name}</div>
                  <div className="cv-status">Analysé · {skills.length} compétences extraites</div>
                </div>
                <button className="btn btn-ghost" style={{ fontSize:11 }} onClick={() => setCvFile(null)}>Changer</button>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title">Compétences</span>
              <span className="card-badge">{skills.length} skills</span>
            </div>
            <div className="chips" style={{ marginBottom:16 }}>
              {skills.map((s) => (
                <span key={s} className="chip match skill-chip"
                  onClick={() => setSkills(skills.filter((x) => x !== s))} title="Cliquer pour retirer">
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
        </div>
      </div>
    </div>
  );
}