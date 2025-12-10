'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { Skeleton } from '@/components/ui/skeleton';
import type { Transaction, PaginatedResponse, Category } from '@/lib/types';

export default function TransactionsPage() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddModal, setShowAddModal] = useState(false);
    const [formData, setFormData] = useState({
        type: 'expense' as 'expense' | 'income',
        amount: '',
        description: '',
        category_id: '',
        transaction_date: new Date().toISOString().split('T')[0],
    });

    useEffect(() => {
        fetchTransactions();
        fetchCategories();
    }, []);

    const fetchTransactions = async () => {
        try {
            const response = await apiClient.get<PaginatedResponse<Transaction>>(
                '/api/v1/transactions?page=1&page_size=50'
            );
            setTransactions(response.items);
        } catch (error) {
            console.error('Failed to fetch transactions:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const cats = await apiClient.get<Category[]>('/api/v1/categories');
            setCategories(cats);
        } catch (error) {
            console.error('Failed to fetch categories:', error);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            await apiClient.post('/api/v1/transactions', {
                ...formData,
                amount: parseFloat(formData.amount),
                category_id: formData.category_id || null,
            });

            setShowAddModal(false);
            setFormData({
                type: 'expense',
                amount: '',
                description: '',
                category_id: '',
                transaction_date: new Date().toISOString().split('T')[0],
            });
            fetchTransactions();
            toast.success('Transaction created successfully');
        } catch (error) {
            console.error('Failed to create transaction:', error);
            toast.error('Failed to create transaction');
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this transaction?')) return;

        try {
            await apiClient.delete(`/api/v1/transactions/${id}`);
            fetchTransactions();
            toast.success('Transaction deleted');
        } catch (error) {
            console.error('Failed to delete transaction:', error);
            toast.error('Failed to delete transaction');
        }
    };

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="flex justify-between items-center">
                    <div>
                        <Skeleton className="h-10 w-48 mb-2" />
                        <Skeleton className="h-5 w-64" />
                    </div>
                    <Skeleton className="h-12 w-40 rounded-lg" />
                </div>
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
                    {[1, 2, 3, 4, 5].map((i) => (
                        <Skeleton key={i} className="h-20 w-full rounded-lg" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Transactions</h1>
                    <p className="text-sm md:text-base text-gray-600 mt-1">View and manage all your transactions</p>
                </div>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 active:from-indigo-800 active:to-purple-800 transition-all"
                >
                    + Add Transaction
                </button>
            </div>

            {/* Transactions List */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                <div className="divide-y divide-gray-200">
                    {transactions.length === 0 ? (
                        <div className="p-12 text-center">
                            <span className="text-6xl mb-4 block">📊</span>
                            <p className="text-gray-600 text-lg">No transactions yet</p>
                            <button
                                onClick={() => setShowAddModal(true)}
                                className="mt-4 text-indigo-600 hover:text-indigo-700 font-semibold"
                            >
                                Create your first transaction
                            </button>
                        </div>
                    ) : (
                        transactions.map((transaction) => (
                            <div key={transaction.id} className="p-4 md:p-6 hover:bg-gray-50 active:bg-gray-100">
                                <div className="flex items-center justify-between gap-3">
                                    <div className="flex items-center space-x-3 md:space-x-4 min-w-0 flex-1">
                                        <div className={`p-2 md:p-3 rounded-full flex-shrink-0 ${transaction.type === 'expense' ? 'bg-red-100' : 'bg-green-100'
                                            }`}>
                                            <span className="text-lg md:text-2xl">{transaction.type === 'expense' ? '💸' : '💰'}</span>
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <p className="font-semibold text-gray-900 text-sm md:text-base truncate">{transaction.description}</p>
                                            <p className="text-xs md:text-sm text-gray-600">
                                                {(() => {
                                                    const [year, month, day] = transaction.transaction_date.split('T')[0].split('-').map(Number);
                                                    return new Date(year, month - 1, day).toLocaleDateString();
                                                })()} • {transaction.type}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2 md:space-x-4 flex-shrink-0">
                                        <div className={`text-base md:text-lg font-semibold ${transaction.type === 'expense' ? 'text-red-600' : 'text-green-600'
                                            }`}>
                                            {transaction.type === 'expense' ? '-' : '+'}${Number(transaction.amount).toFixed(2)}
                                        </div>
                                        <button
                                            onClick={() => handleDelete(transaction.id)}
                                            className="text-red-600 hover:text-red-700 active:text-red-800 p-2 min-w-[44px] min-h-[44px] flex items-center justify-center"
                                            aria-label="Delete transaction"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Add Transaction Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={() => setShowAddModal(false)}>
                    <div className="bg-white rounded-2xl p-4 sm:p-6 md:p-8 max-w-sm sm:max-w-md w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                        <h2 className="text-xl md:text-2xl font-bold text-gray-900 mb-4 md:mb-6">Add Transaction</h2>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm md:text-base font-medium text-gray-700 mb-2">Type</label>
                                <select
                                    value={formData.type}
                                    onChange={(e) => setFormData({ ...formData, type: e.target.value as 'expense' | 'income' })}
                                    className="w-full px-3 py-2 md:px-4 md:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                >
                                    <option value="expense">Expense</option>
                                    <option value="income">Income</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm md:text-base font-medium text-gray-700 mb-2">Amount</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.amount}
                                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                                    required
                                    className="w-full px-3 py-2 md:px-4 md:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                    placeholder="0.00"
                                />
                            </div>

                            <div>
                                <label className="block text-sm md:text-base font-medium text-gray-700 mb-2">Description</label>
                                <input
                                    type="text"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    required
                                    className="w-full px-3 py-2 md:px-4 md:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                    placeholder="Lunch at restaurant"
                                />
                            </div>

                            <div>
                                <label className="block text-sm md:text-base font-medium text-gray-700 mb-2">Category (Optional)</label>
                                <select
                                    value={formData.category_id}
                                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                                    className="w-full px-3 py-2 md:px-4 md:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                >
                                    <option value="">No category</option>
                                    {categories
                                        .filter((c) => c.type === formData.type)
                                        .map((cat) => (
                                            <option key={cat.id} value={cat.id}>
                                                {cat.icon} {cat.name}
                                            </option>
                                        ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm md:text-base font-medium text-gray-700 mb-2">Date</label>
                                <input
                                    type="date"
                                    value={formData.transaction_date}
                                    onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                                    required
                                    className="w-full px-3 py-2 md:px-4 md:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                />
                            </div>

                            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowAddModal(false)}
                                    className="w-full sm:flex-1 px-4 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50 active:bg-gray-100 text-gray-700"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="w-full sm:flex-1 px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 active:from-indigo-800 active:to-purple-800"
                                >
                                    Add Transaction
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
