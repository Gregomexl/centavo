// TypeScript types for API data models

export type TransactionType = 'expense' | 'income';

export interface User {
    id: string;
    email: string | null;
    telegram_id: number | null;
    display_name: string;
    default_currency: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface Category {
    id: string;
    user_id: string | null;
    name: string;
    icon: string;
    color: string;
    type: TransactionType;
    is_system: boolean;
    monthly_limit: number | null;
    created_at: string;
    updated_at: string;
}

export interface Transaction {
    id: string;
    user_id: string;
    category_id: string | null;
    type: TransactionType;
    amount: number;
    currency: string;
    description: string;
    raw_message: string | null;
    transaction_date: string;
    created_at: string;
    updated_at: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    display_name: string;
    default_currency?: string;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface TransactionCreate {
    type: TransactionType;
    amount: number;
    currency?: string;
    description: string;
    category_id?: string | null;
    transaction_date?: string;
}

export interface TransactionUpdate {
    type?: TransactionType;
    amount?: number;
    currency?: string;
    description?: string;
    category_id?: string | null;
    transaction_date?: string;
}

export interface CategoryCreate {
    name: string;
    icon?: string;
    color?: string;
    type: TransactionType;
    monthly_limit?: number | null;
}

export interface CategoryUpdate {
    name?: string;
    icon?: string;
    color?: string;
    monthly_limit?: number | null;
}
