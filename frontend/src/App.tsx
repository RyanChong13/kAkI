import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import Landing from "./pages/Landing";
import Register from "./pages/Register";
import Login from "./pages/Login";
import ResumeUpload from "./pages/ResumeUpload";
import ChoosePath from "./pages/ChoosePath";
import Dashboard from "./pages/Dashboard";
import RecommendedJobs from "./pages/jobRedeployment/RecommendedJobs";
import MassApply from "./pages/jobRedeployment/MassApply";
import GoalPrompt from "./pages/upskilling/GoalPrompt";
import RecommendedCourses from "./pages/upskilling/RecommendedCourses";
import RecommendedGrants from "./pages/upskilling/RecommendedGrants";
import Browse from "./pages/courses/Browse";
import CourseDetail from "./pages/courses/CourseDetail";

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/courses" element={<Browse />} />
        <Route path="/courses/:id" element={<CourseDetail />} />

        <Route
          path="/resume-upload"
          element={
            <ProtectedRoute>
              <ResumeUpload />
            </ProtectedRoute>
          }
        />
        <Route
          path="/choose-path"
          element={
            <ProtectedRoute>
              <ChoosePath />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/jobs/recommended"
          element={
            <ProtectedRoute>
              <RecommendedJobs />
            </ProtectedRoute>
          }
        />
        <Route
          path="/jobs/apply"
          element={
            <ProtectedRoute>
              <MassApply />
            </ProtectedRoute>
          }
        />

        <Route
          path="/upskilling/goal"
          element={
            <ProtectedRoute>
              <GoalPrompt />
            </ProtectedRoute>
          }
        />
        <Route
          path="/upskilling/courses"
          element={
            <ProtectedRoute>
              <RecommendedCourses />
            </ProtectedRoute>
          }
        />
        <Route
          path="/upskilling/grants"
          element={
            <ProtectedRoute>
              <RecommendedGrants />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}
