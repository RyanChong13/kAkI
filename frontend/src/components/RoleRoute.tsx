import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

interface Props {
  children: ReactNode;
  allowedRoles?: Array<"public" | "organiser">;
}

/**
 * Wraps a protected route with role-based access control.
 * - If allowedRoles includes "organiser" only, public users are redirected to /dashboard.
 * - If allowedRoles includes "public" only, organisers are redirected to /organiser.
 * - If allowedRoles is omitted, all authenticated users can access.
 */
export default function RoleRoute({ children, allowedRoles }: Props) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="page container" style={{ display: "flex", justifyContent: "center" }}>
        <div className="spinner" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to the appropriate dashboard
    const redirect = user.role === "organiser" ? "/organiser" : "/dashboard";
    return <Navigate to={redirect} replace />;
  }

  return <>{children}</>;
}
