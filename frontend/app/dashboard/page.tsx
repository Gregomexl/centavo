'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import type { Transaction } from '@/lib/types';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from 'recharts';

interface SummaryData {
    total_expenses: number;
    total_income: number;
    balance: number;
    transaction_count: number;
}

export default function DashboardPage() {
    const [summary, setSummary] = useState<SummaryData>({
        total_expenses: 0,
        total_income: 0,
        balance: 0,
        transaction_count: 0,
    });
    const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
    const [chartData, setChartData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const response = await apiClient.get<any>('/api/v1/transactions?page=1&page_size=100');
                const transactions = response.items || [];

                // Calculate summary
                const totalExpenses = transactions
                    .filter((t: Transaction) => t.type === 'expense')
                    .reduce((sum: number, t: Transaction) => sum + Number(t.amount), 0);

                const totalIncome = transactions
                    .filter((t: Transaction) => t.type === 'income')
                    .reduce((sum: number, t: Transaction) => sum + Number(t.amount), 0);

                setSummary({
                    total_expenses: totalExpenses,
                    total_income: totalIncome,
                    balance: totalIncome - totalExpenses,
                    transaction_count: transactions.length,
                });

                // Get recent 5 transactions
                setRecentTransactions(transactions.slice(0, 5));

                // Prepare mini chart data (last 7 days or simply last few transactions for sparkline effect)
                // Group by day
                const dailyData: Record<string, number> = {};
                transactions.forEach((t: Transaction) => {
                    const date = new Date(t.transaction_date).toLocaleDateString();
                    // Net amount
                    const amount = t.type === 'income' ? Number(t.amount) : -Number(t.amount);
                    dailyData[date] = (dailyData[date] || 0) + amount;
                });

                const chart = Object.entries(dailyData)
                    .map(([date, amount]) => ({ date: date.split('/')[0] + '/' + date.split('/')[1], amount })) // MM/DD
                    .slice(-7) // Last 7 days with activity
                    .reverse(); // Standard chron order might need sorting if keys not sorted.

                setChartData(chart);

            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6 md:space-y-8">
            <div>
                <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-sm md:text-base text-gray-600 mt-1">Welcome back! Here's your financial overview.</p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs md:text-sm font-medium text-gray-600">Total Expenses</p>
                            <p className="text-xl md:text-2xl font-bold text-red-600 mt-1 md:mt-2">
                                ${summary.total_expenses.toFixed(2)}
                            </p>
                        </div>
                        <div className="bg-red-100 rounded-full p-2 md:p-3">
                            <span className="text-xl md:text-2xl">💸</span>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs md:text-sm font-medium text-gray-600">Total Income</p>
                            <p className="text-xl md:text-2xl font-bold text-green-600 mt-1 md:mt-2">
                                ${summary.total_income.toFixed(2)}
                            </p>
                        </div>
                        <div className="bg-green-100 rounded-full p-2 md:p-3">
                            <span className="text-xl md:text-2xl">💰</span>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs md:text-sm font-medium text-gray-600">Balance</p>
                            <p className={`text-xl md:text-2xl font-bold mt-1 md:mt-2 ${summary.balance >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                                ${summary.balance.toFixed(2)}
                            </p>
                        </div>
                        <div className="bg-blue-100 rounded-full p-2 md:p-3">
                            <span className="text-xl md:text-2xl">📊</span>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs md:text-sm font-medium text-gray-600">Transactions</p>
                            <p className="text-xl md:text-2xl font-bold text-purple-600 mt-1 md:mt-2">
                                {summary.transaction_count}
                            </p>
                        </div>
                        <div className="bg-purple-100 rounded-full p-2 md:p-3">
                            <span className="text-xl md:text-2xl">📝</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
                {/* Recent Transactions */}
                <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200">
                    <div className="p-4 md:p-6 border-b border-gray-200 flex justify-between items-center">
                        <h2 className="text-lg md:text-xl font-semibold text-gray-900">Recent Transactions</h2>
                        <a href="/dashboard/transactions" className="text-indigo-600 text-sm hover:underline active:underline">View All</a>
                    </div>
                    <div className="divide-y divide-gray-200">
                        {recentTransactions.length === 0 ? (
                            <div className="p-6 md:p-8 text-center text-sm md:text-base text-gray-500">
                                No transactions yet. Start tracking your expenses!
                            </div>
                        ) : (
                            recentTransactions.map((transaction) => (
                                <div key={transaction.id} className="p-4 md:p-6 hover:bg-gray-50 active:bg-gray-100">
                                    <div className="flex items-center justify-between gap-3">
                                        <div className="flex items-center space-x-3 md:space-x-4 min-w-0 flex-1">
                                            <div className={`p-2 rounded-full flex-shrink-0 ${transaction.type === 'expense' ? 'bg-red-100' : 'bg-green-100'
                                                }`}>
                                                <span className="text-lg md:text-xl">{transaction.type === 'expense' ? '💸' : '💰'}</span>
                                            </div>
                                            <div className="min-w-0 flex-1">
                                                <p className="font-medium text-gray-900 text-sm md:text-base truncate">{transaction.description}</p>
                                                <p className="text-xs md:text-sm text-gray-500">{new Date(transaction.transaction_date).toLocaleDateString()}</p>
                                            </div>
                                        </div>
                                        <div className={`text-base md:text-lg font-semibold flex-shrink-0 ${transaction.type === 'expense' ? 'text-red-600' : 'text-green-600'
                                            }`}>
                                            {transaction.type === 'expense' ? '-' : '+'}${Number(transaction.amount).toFixed(2)}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Mini Chart / Quick Stats */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6">
                    <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-4">Activity</h2>
                    <div className="h-56 md:h-64 lg:h-72">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                                <Tooltip />
                                <Line type="monotone" dataKey="amount" stroke="#6366f1" strokeWidth={2} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                        <p className="text-center text-xs md:text-sm text-gray-500 mt-2">Daily Net Activity</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
