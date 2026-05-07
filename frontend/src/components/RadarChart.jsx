import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart as ReRadarChart,
  ResponsiveContainer,
} from "recharts";

export default function RadarChart({ data = [] }) {
  if (!data.length) return <div style={{ fontSize: 12, color: "var(--muted)" }}>Pas de donnees radar.</div>;

  return (
    <ResponsiveContainer width="100%" height={230}>
      <ReRadarChart data={data}>
        <PolarGrid stroke="#293042" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: "#9ca3af", fontSize: 11 }} />
        <PolarRadiusAxis tick={false} axisLine={false} />
        <Radar name="Profil" dataKey="user" stroke="#00e5a0" fill="#00e5a0" fillOpacity={0.25} />
        <Radar name="Offre" dataKey="offer" stroke="#3d7fff" fill="#3d7fff" fillOpacity={0.12} />
      </ReRadarChart>
    </ResponsiveContainer>
  );
}
