// frontend/src/components/ScoreRing.jsx
import "./ScoreRing.css";

const scoreColor = (s) => s >= 80 ? "#00e5a0" : s >= 60 ? "#f59e0b" : "#ff6b6b";

export default function ScoreRing({ value }) {
  const r     = 50, cx = 60, cy = 60;
  const circ  = 2 * Math.PI * r;
  const fill  = (value / 100) * circ;
  const color = scoreColor(value);

  return (
    <div className="score-ring-wrap">
      <div className="score-ring">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle cx={cx} cy={cy} r={r} fill="none"
            stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
          <circle cx={cx} cy={cy} r={r} fill="none"
            stroke={color} strokeWidth="8"
            strokeDasharray={`${fill} ${circ}`} strokeLinecap="round"
            style={{ transform:"rotate(-90deg)", transformOrigin:"60px 60px", transition:"stroke-dasharray 1s ease" }} />
        </svg>
        <div className="score-ring-label">
          <div className="score-pct" style={{ color }}>{value}%</div>
          <div className="score-txt">MATCH</div>
        </div>
      </div>
    </div>
  );
}