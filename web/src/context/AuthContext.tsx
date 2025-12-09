/**
 * Authentication context for managing user state.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api, User, UserCreateRequest, UserLoginRequest } from '../services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signup: (data: UserCreateRequest) => Promise<void>;
  login: (data: UserLoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (updates: any) => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const currentUser = await api.getCurrentUser();
          setUser(currentUser);
          localStorage.setItem('user', JSON.stringify(currentUser));
        } catch (err) {
          // Token invalid or expired
          api.clearAuth();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const signup = async (data: UserCreateRequest) => {
    try {
      setError(null);
      const response = await api.signup(data);
      api.setAuthToken(response.access_token);
      setUser(response.user);
      localStorage.setItem('user', JSON.stringify(response.user));
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Signup failed';
      setError(message);
      throw err;
    }
  };

  const login = async (data: UserLoginRequest) => {
    try {
      setError(null);
      const response = await api.login(data);
      api.setAuthToken(response.access_token);
      setUser(response.user);
      localStorage.setItem('user', JSON.stringify(response.user));
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      throw err;
    }
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      api.clearAuth();
      setUser(null);
    }
  };

  const updateProfile = async (updates: any) => {
    try {
      setError(null);
      const updated = await api.updateProfile(updates);
      setUser(updated);
      localStorage.setItem('user', JSON.stringify(updated));
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Profile update failed';
      setError(message);
      throw err;
    }
  };

  const clearError = () => setError(null);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    signup,
    login,
    logout,
    updateProfile,
    error,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
