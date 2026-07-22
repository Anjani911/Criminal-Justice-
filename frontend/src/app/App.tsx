import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import MainLayout from '@/layouts/MainLayout';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import CasesPage from '@/pages/CasesPage';
import AnalyticsPage from '@/pages/AnalyticsPage';
import PredictionsPage from '@/pages/PredictionsPage';
import NetworkPage from '@/pages/NetworkPage';
import ChatPage from '@/pages/ChatPage';
import ReportsPage from '@/pages/ReportsPage';
import AuditPage from '@/pages/AuditPage';
import ProfilePage from '@/pages/ProfilePage';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="cases" element={<CasesPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="predictions" element={<PredictionsPage />} />
        <Route path="network" element={<NetworkPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="audit" element={<AuditPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>
    </Routes>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
};

export default App;
