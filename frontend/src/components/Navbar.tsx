import type { CSSProperties } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <header style={{ borderBottom: "1px solid var(--border)", background: "var(--bg-card)", position: "sticky", top: 0, zIndex: 20 }}>
      <div className="container row-between" style={{ height: 64 }}>
        <NavLink to="/" style={{ fontWeight: 800, fontSize: "1.2rem", color: "var(--ink-900)", textDecoration: "none" }}>
          Nexa
        </NavLink>

        <nav className="row" style={{ gap: "1rem" }}>
          <NavLink to="/redesign" className="muted" style={navStyle} end>Redesign</NavLink>
          <NavLink to="/courses" className="muted" style={navStyle}>Courses</NavLink>
        </nav>

        <div className="row" style={{ gap: "0.75rem" }}>
          {user ? (
            <>
              <span className="muted" style={{ fontSize: "0.85rem" }}>{user.name || user.email}</span>
              <button className="btn btn-ghost btn-sm" onClick={handleLogout}>Log out</button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="btn btn-ghost btn-sm">Log in</NavLink>
              <NavLink to="/register" className="btn btn-primary btn-sm">Sign up</NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

const navStyle: CSSProperties = { color: "var(--ink-700)", fontWeight: 600, fontSize: "0.9rem", textDecoration: "none" };
