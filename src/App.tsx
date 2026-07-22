import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ResumeUploadPage from './pages/ResumeUploadPage';
import PathSelectionPage from './pages/PathSelectionPage';
import JobRecommendationsPage from './pages/JobRecommendationsPage';
import UpskillingPage from './pages/UpskillingPage';
import GrantSelectionPage from './pages/GrantSelectionPage';
import MassApplyReviewPage from './pages/MassApplyReviewPage';
import ExitPage from './pages/ExitPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/resume" element={<ProtectedRoute><ResumeUploadPage /></ProtectedRoute>} />
          <Route path="/choose-path" element={<ProtectedRoute><PathSelectionPage /></ProtectedRoute>} />
          <Route path="/jobs" element={<ProtectedRoute><JobRecommendationsPage /></ProtectedRoute>} />
          <Route path="/upskilling" element={<ProtectedRoute><UpskillingPage /></ProtectedRoute>} />
          <Route path="/grants" element={<ProtectedRoute><GrantSelectionPage /></ProtectedRoute>} />
          <Route path="/review" element={<ProtectedRoute><MassApplyReviewPage /></ProtectedRoute>} />
          <Route path="/exit" element={<ProtectedRoute><ExitPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
