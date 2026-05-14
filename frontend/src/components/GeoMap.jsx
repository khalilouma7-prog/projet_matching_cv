// frontend/src/components/GeoMap.jsx
import "./GeoMap.css";

// offers = [{ title, company, location, lat, lng }, ...]
export default function GeoMap({ offers = [] }) {
  const points = offers.filter((o) => Number.isFinite(o.lat) && Number.isFinite(o.lng));

  if (!points.length) {
    return (
      <div className="geomap geomap-empty">
        <div className="geomap-title">Carte géographique des offres</div>
        <div className="geomap-sub">Aucune coordonnee disponible pour les offres.</div>
      </div>
    );
  }

  const center = points[0];
  const mapUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${center.lng - 1.2}%2C${center.lat - 1.0}%2C${center.lng + 1.2}%2C${center.lat + 1.0}&layer=mapnik&marker=${center.lat}%2C${center.lng}`;

  return (
    <div className="geomap">
      <iframe
        title="offers-map"
        className="geomap-frame"
        src={mapUrl}
        loading="lazy"
      />
      <div className="geomap-points">
        {points.map((o) => (
          <a
            key={`${o.job_id}-${o.lat}-${o.lng}`}
            href={`https://www.openstreetmap.org/?mlat=${o.lat}&mlon=${o.lng}#map=11/${o.lat}/${o.lng}`}
            target="_blank"
            rel="noreferrer"
            className="geomap-point"
          >
            {o.title} - {o.location}
          </a>
        ))}
      </div>
      <div className="geomap-sub">{points.length} offre(s) geolocalisee(s)</div>
    </div>
  );
}