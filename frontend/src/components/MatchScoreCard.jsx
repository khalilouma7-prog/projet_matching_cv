// frontend/src/components/MatchScoreCard.jsx
import "./MatchScoreCard.css";

const scoreColor = (s) => s >= 80 ? "#00e5a0" : s >= 60 ? "#f59e0b" : "#ff6b6b";

export default function MatchScoreCard({ offer, selected, onClick }) {
  return (
    <div className={`offer-item${selected ? " selected" : ""}`} onClick={onClick}>
      <div className="offer-logo"
        style={{ background:`linear-gradient(135deg, ${offer.color1}, ${offer.color2})` }}>
        {offer.icon}
      </div>
      <div className="offer-info">
        <div className="offer-title">{offer.title}</div>
        <div className="offer-meta">
          <span>{offer.company}</span>
          <span>📍 {offer.location}</span>
          <span>{offer.contract}</span>
        </div>
      </div>
      <div className="offer-score" style={{ color: scoreColor(offer.score) }}>
        {offer.score}%
      </div>
    </div>
  );
}