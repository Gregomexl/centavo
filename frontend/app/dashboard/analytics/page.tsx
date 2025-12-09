'use client';

import { useEffect, useState } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart,
    Line,
} from 'recharts';
import { apiClient } from '@/lib/api-client';
import type { Transaction, Category } from '@/lib/types';

const COLORS = ['#6366f1', '#ec4899', '#8b5cf6', '#14b8a6', '#f59e0b', '#ef4444', '#10b981', '#3b82f6'];

export default function AnalyticsPage() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [transRes, catsRes] = await Promise.all([
                    apiClient.get<any>('/api/v1/transactions?page=1&page_size=100'),
                    apiClient.get<Category[]>('/api/v1/categories')
                ]);
                setTransactions(transRes.items || []);
                setCategories(catsRes);
            } catch (error) {
                console.error('Failed to fetch analytics data:', error);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    // Process Monthly Data
    const getMonthlyData = () => {
        const monthlyData: Record<string, { name: string; income: number; expense: number }> = {};

        transactions.forEach(t => {
            const date = new Date(t.transaction_date);
            const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            const monthName = date.toLocaleString('default', { month: 'short', year: '2-digit' });

            if (!monthlyData[monthKey]) {
                monthlyData[monthKey] = { name: monthName, income: 0, expense: 0 };
            }

            if (t.type === 'income') {
                monthlyData[monthKey].income += t.amount;
            } else {
                monthlyData[monthKey].expense += t.amount;
            }
        });

        return Object.keys(monthlyData).sort().map(key => monthlyData[key]);
    };

    // Process Category Breakdown
    const getCategoryData = () => {
        const expenses = transactions.filter(t => t.type === 'expense');
        const categoryTotals: Record<string, number> = {};

        expenses.forEach(t => {
            const cat = categories.find(c => c.id === t.category_id);
            const name = cat ? cat.name : 'Uncategorized';
            categoryTotals[name] = (categoryTotals[name] || 0) + t.amount;
        });

        return Object.entries(categoryTotals)
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    const monthlyData = getMonthlyData();
    const categoryData = getCategoryData();

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
                <p className="text-gray-600 mt-1">Visualize your financial trends</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Income vs Expenses */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-semibold mb-6">Income vs Expenses</h2>
                    <div className="h-80 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={monthlyData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                                <YAxis axisLine={false} tickLine={false} tickFormatter={(value) => `$${value}`} />
                                <Tooltip
                                    formatter={(value: number) => [`$${value.toFixed(2)}`, '']}
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Legend />
                                <Bar dataKey="income" fill="#10b981" name="Income" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="expense" fill="#ef4444" name="Expenses" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Category Breakdown */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-semibold mb-6">Expense Breakdown</h2>
                    <div className="h-80 w-full flex justify-center">
                        {categoryData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={categoryData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={100}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {categoryData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center text-gray-400">
                                No expense data available
                            </div>
                        )}
                    </div>
                </div>

                {/* Balance Trend */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 lg:col-span-2">
                    <h2 className="text-xl font-semibold mb-6">Balance Trend</h2>
                    <div className="h-80 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={monthlyData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                                <YAxis axisLine={false} tickLine={false} tickFormatter={(value) => `$${value}`} />
                                <Tooltip
                                    formatter={(value: number) => [`$${value.toFixed(2)}`, '']}
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="income"
                                    stroke="#10b981"
                                    strokeWidth={2}
                                    dot={{ r: 4 }}
                                    activeDot={{ r: 8 }}
                                    name="Income Trend"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="expense"
                                    stroke="#ef4444"
                                    strokeWidth={2}
                                    dot={{ r: 4 }}
                                    name="Expense Trend"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}
