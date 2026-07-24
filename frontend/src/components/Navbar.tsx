import type { CSSProperties } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header
      style={{
        borderBottom: "1px solid var(--border)",
        background: "white",
        position: "sticky",
        top: 0,
        zIndex: 10,
      }}
    >
      <div className="container row-between" style={{ height: 64 }}>
        <NavLink to="/" style={{ fontWeight: 800, fontSize: "1.15rem", color: "var(--ink-900)" }}>
          Skills<span style={{ color: "var(--purple-600)" }}>SG</span>
        </NavLink>

        <nav className="row" style={{ gap: "1.25rem" }}>
          <NavLink to="/courses" className="muted" style={navStyle}>
            Browse Courses
          </NavLink>
          {user && (
            <>
              <NavLink to="/choose-path" className="muted" style={navStyle}>
                Get Started
              </NavLink>
              <NavLink to="/dashboard" className="muted" style={navStyle}>
                Dashboard
              </NavLink>
            </>
          )}
        </nav>

        <div className="row">
          {user ? (
            <>
              <span className="muted" style={{ display: "none" }}>
                {user.email}
              </span>
              <button className="btn btn-ghost" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="btn btn-ghost">
                Log in
              </NavLink>
              <NavLink to="/register" className="btn btn-primary">
                Create account
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

const navStyle: CSSProperties = { color: "var(--ink-700)", fontWeight: 600, fontSize: "0.92rem" };
