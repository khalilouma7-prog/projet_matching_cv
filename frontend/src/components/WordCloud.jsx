import "./WordCloud.css";

// words = [{ text, size, color, opacity }, ...]
export default function WordCloud({ words = [] }) {
  return (
    <div className="word-cloud">
      {words.map((w) => (
        <span key={w.text} className="wc-item"
          style={{ fontSize: w.size, color: w.color, opacity: w.opacity ?? 0.85,
            fontWeight: w.size > 24 ? 800 : 600 }}>
          {w.text}
        </span>
      ))}
    </div>
  );
}
