import { Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import AIChat from "./components/AIChat";
import Landing from "./pages/Landing";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import GrowthPlan from "./pages/GrowthPlan";
import LearningJourney from "./pages/LearningJourney";
import Profile from "./pages/Profile";
import CoursesBrowse from "./pages/courses/Browse";
import CourseDetail from "./pages/courses/CourseDetail";
import OrganiserDashboard from "./pages/organiser/Dashboard";
import OrganiserSettings from "./pages/organiser/Settings";
import OrganiserProfile from "./pages/organiser/Profile";
import Onboarding from "./pages/Onboarding";

export default function App() {
  const { user } = useAuth();

  return (
    <>
      <Navbar />
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/courses" element={<CoursesBrowse />} />
        <Route path="/courses/:id" element={<CourseDetail />} />

        {/* Protected routes */}
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <Onboarding />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <RoleRoute allowedRoles={["public"]}>
              <Dashboard />
            </RoleRoute>
          }
        />
        <Route
          path="/growth-plan"
          element={
            <RoleRoute allowedRoles={["public"]}>
              <GrowthPlan />
            </RoleRoute>
          }
        />
        <Route
          path="/learning-journey"
          element={
            <RoleRoute allowedRoles={["public"]}>
              <LearningJourney />
            </RoleRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/organiser"
          element={
            <RoleRoute allowedRoles={["organiser"]}>
              <OrganiserDashboard />
            </RoleRoute>
          }
        />
        <Route
          path="/organiser/settings"
          element={
            <RoleRoute allowedRoles={["organiser"]}>
              <OrganiserSettings />
            </RoleRoute>
          }
        />
        <Route
          path="/organiser/profile"
          element={
            <RoleRoute allowedRoles={["organiser"]}>
              <OrganiserProfile />
            </RoleRoute>
          }
        />
      </Routes>
      {user && <AIChat />}
    </>
  );
}
