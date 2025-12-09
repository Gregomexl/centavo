'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService } from '@/lib/auth-service';
import type { User } from '@/lib/types';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initAuth = async () => {
            authService.initializeToken();
            const token = authService.getAccessToken();

            if (!token) {
                router.push('/login');
                return;
            }

            try {
                const currentUser = await authService.getCurrentUser();
                setUser(currentUser);
            } catch (error) {
                authService.logout();
                router.push('/login');
            } finally {
                setLoading(false);
            }
        };

        initAuth();
    }, [router]);

    const handleLogout = () => {
        authService.logout();
        router.push('/login');
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navigation */}
            <nav className="bg-white shadow-sm border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center space-x-8">
                            <Link href="/dashboard" className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                                Centavo
                            </Link>

                            <div className="hidden md:flex space-x-4">
                                <Link href="/dashboard" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-indigo-600 hover:bg-gray-50">
                                    Dashboard
                                </Link>
                                <Link href="/dashboard/transactions" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-indigo-600 hover:bg-gray-50">
                                    Transactions
                                </Link>
                                <Link href="/dashboard/analytics" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-indigo-600 hover:bg-gray-50">
                                    Analytics
                                </Link>
                                <Link href="/dashboard/categories" className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-indigo-600 hover:bg-gray-50">
                                    Categories
                                </Link>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4">
                            <span className="text-sm text-gray-600">
                                {user?.display_name}
                            </span>
                            <button
                                onClick={handleLogout}
                                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-indigo-600"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {children}
            </main>
        </div>
    );
}
