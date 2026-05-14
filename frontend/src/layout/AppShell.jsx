import { useEffect, useMemo, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { clearStoredUser, loadStoredUser } from "../session";
import "./AppShell.css";

function pathToPage(pathname) {
  if (pathname.startsWith("/dashboard")) return "dashboard";
  if (pathname.startsWith("/results")) return "results";
  if (pathname.startsWith("/profile")) return "profile";
  return "dashboard";
}

export default function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const [user, setUser] = useState(loadStoredUser);

  const page = useMemo(() => pathToPage(location.pathname), [location.pathname]);

  useEffect(() => {
    setUser(loadStoredUser());
  }, [location.pathname]);

  const setPage = (id) => {
    const paths = { dashboard: "/dashboard", results: "/results", profile: "/profile" };
    navigate(paths[id] || "/dashboard");
  };

  const onLogout = () => {
    clearStoredUser();
    setUser(null);
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={setPage} user={user} />
      <div className="app-shell-main">
        <Topbar page={page} setPage={setPage} onLogout={onLogout} />
        <main className="app-shell-outlet">
          <Outlet context={{ user }} />
        </main>
      </div>
    </div>
  );
}
