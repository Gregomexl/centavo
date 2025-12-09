// Authentication service using API client

import { apiClient } from './api-client';
import type {
    LoginCredentials,
    RegisterData,
    TokenResponse,
    User,
} from './types';

const TOKEN_KEY = 'centavo_access_token';
const REFRESH_TOKEN_KEY = 'centavo_refresh_token';

export const authService = {
    async login(credentials: LoginCredentials): Promise<TokenResponse> {
        const response = await apiClient.post<TokenResponse>(
            '/api/v1/auth/login',
            credentials
        );

        this.setTokens(response.access_token, response.refresh_token);
        apiClient.setToken(response.access_token);

        return response;
    },

    async register(data: RegisterData): Promise<User> {
        const user = await apiClient.post<User>('/api/v1/auth/register', data);
        return user;
    },

    async getCurrentUser(): Promise<User> {
        return apiClient.get<User>('/api/v1/auth/me');
    },

    logout() {
        if (typeof window !== 'undefined') {
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(REFRESH_TOKEN_KEY);
        }
        apiClient.setToken(null);
    },

    getAccessToken(): string | null {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(TOKEN_KEY);
    },

    getRefreshToken(): string | null {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(REFRESH_TOKEN_KEY);
    },

    setTokens(accessToken: string, refreshToken: string) {
        if (typeof window !== 'undefined') {
            localStorage.setItem(TOKEN_KEY, accessToken);
            localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
        }
    },

    initializeToken() {
        const token = this.getAccessToken();
        if (token) {
            apiClient.setToken(token);
        }
    },
};
