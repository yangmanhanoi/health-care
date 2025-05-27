import React, { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import type {
  AuthContextType,
  User,
  LoginRequest,
  RegisterRequest,
  RegisterDoctorRequest,
  ApiError,
} from "../types/auth";
import { apiService } from "../services/api";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load user and token from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem("auth_token");
    const savedUser = localStorage.getItem("auth_user");

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
        apiService.setAuthToken(savedToken);
      } catch (error) {
        console.error("Error parsing saved user data:", error);
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_user");
      }
    }
  }, []);

  const login = async (credentials: LoginRequest): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.login(credentials);

      // Decode the JWT token to get user info
      const tokenPayload = JSON.parse(atob(response.access.split(".")[1]));

      const userData: User = {
        username: tokenPayload.username || credentials.username,
        roles: tokenPayload.roles || ["PATIENT"],
        user_id: tokenPayload.user_id,
        id: tokenPayload.user_id, // Set both for consistency
      };

      setToken(response.access);
      setUser(userData);

      // Save to localStorage
      localStorage.setItem("auth_token", response.access);
      localStorage.setItem("auth_user", JSON.stringify(userData));
      localStorage.setItem("refresh_token", response.refresh);

      apiService.setAuthToken(response.access);
    } catch (error) {
      const apiError = error as ApiError;
      setError(apiError.message || "Login failed");
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterRequest): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await apiService.register(data);
      // After successful registration, automatically log in
      await login({ username: data.username, password: data.password });
    } catch (error) {
      const apiError = error as ApiError;
      setError(apiError.message || "Registration failed");
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const registerDoctor = async (data: RegisterDoctorRequest): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await apiService.registerDoctor(data);
      // After successful registration, automatically log in
      await login({ username: data.username, password: data.password });
    } catch (error) {
      const apiError = error as ApiError;
      setError(apiError.message || "Doctor registration failed");
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    setUser(null);
    setToken(null);
    setError(null);

    // Clear localStorage
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
    localStorage.removeItem("refresh_token");

    apiService.removeAuthToken();
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    registerDoctor,
    logout,
    isLoading,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
