/**
 * API client for backend communication.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  language_preference: string;
  theme: string;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ChatQueryRequest {
  query: string;
  mode?: 'global' | 'chapter';
  chapter_id?: string;
  user_difficulty?: 'beginner' | 'intermediate' | 'advanced';
  conversation_session_id?: string;
  parent_message_id?: string;
  intent?: string;
}

export interface ChatSource {
  chapter_id: string;
  chapter_title: string;
  module_slug: string;
  excerpt: string;
  relevance_score: number;
}

export interface ChatQueryResponse {
  message_id: string;
  response: string;
  sources: ChatSource[];
  conversation_context?: {
    session_id?: string;
    topics: string[];
    next_suggestions: string[];
  };
  follow_up_options: string[];
  created_at: string;
}

export interface UserCreateRequest {
  email: string;
  password: string;
  name: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface ProfileUpdateRequest {
  bio?: string;
  avatar_url?: string;
  organization?: string;
  country?: string;
  email_notifications?: boolean;
  show_progress_publicly?: boolean;
  language_preference?: string;
  theme?: string;
}

// API Client
class APIClient {
  private client: AxiosInstance;
  private baseURL: string = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  constructor() {
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Clear auth and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async signup(data: UserCreateRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/signup', data);
    return response.data;
  }

  async login(data: UserLoginRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', data);
    return response.data;
  }

  async logout(): Promise<{ message: string }> {
    const response = await this.client.post('/auth/logout');
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  async updateProfile(data: ProfileUpdateRequest): Promise<User> {
    const response = await this.client.patch<User>('/auth/profile', data);
    return response.data;
  }

  // Chat endpoints
  async askQuestion(query: ChatQueryRequest): Promise<ChatQueryResponse> {
    const response = await this.client.post<ChatQueryResponse>('/chat/query', query);
    return response.data;
  }

  async rateMessage(messageId: string, rating: number, comment?: string): Promise<any> {
    const response = await this.client.post(`/chat/messages/${messageId}/rate`, {
      rating,
      comment,
    });
    return response.data;
  }

  // Health check
  async health(): Promise<{ status: string; service: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  setAuthToken(token: string): void {
    localStorage.setItem('access_token', token);
    this.client.defaults.headers.common.Authorization = `Bearer ${token}`;
  }

  clearAuth(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    delete this.client.defaults.headers.common.Authorization;
  }
}

// Export singleton instance
export const api = new APIClient();
