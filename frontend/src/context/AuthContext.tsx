import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { Employee } from '@/types';
import { authService } from '@/services/auth.service';

interface AuthContextValue {
  employee: Employee | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [employee, setEmployee] = useState<Employee | null>(null);
  const isAuthenticated = Boolean(employee);

  useEffect(() => {
    const stored = localStorage.getItem('employee');
    if (stored) {
      setEmployee(JSON.parse(stored));
    }
  }, []);

  const login = async (username: string, password: string) => {
    const result = await authService.login(username, password);
    setEmployee(result.employee);
  };

  const logout = () => {
    authService.logout();
    setEmployee(null);
  };

  const value = useMemo(() => ({ employee, isAuthenticated, login, logout }), [employee, isAuthenticated]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
