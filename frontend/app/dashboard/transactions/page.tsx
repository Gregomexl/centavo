'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
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
        } catch (error) {
            console.error('Failed to create transaction:', error);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this transaction?')) return;

        try {
            await apiClient.delete(`/api/v1/transactions/${id}`);
            fetchTransactions();
        } catch (error) {
            console.error('Failed to delete transaction:', error);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Transactions</h1>
                    <p className="text-gray-600 mt-1">View and manage all your transactions</p>
                </div>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all"
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
                            <div key={transaction.id} className="p-6 hover:bg-gray-50 flex items-center justify-between">
                                <div className="flex items-center space-x-4">
                                    <div className={`p-3 rounded-full ${transaction.type === 'expense' ? 'bg-red-100' : 'bg-green-100'
                                        }`}>
                                        <span className="text-2xl">{transaction.type === 'expense' ? '💸' : '💰'}</span>
                                    </div>
                                    <div>
                                        <p className="font-semibold text-gray-900">{transaction.description}</p>
                                        <div className="text-sm text-gray-500">
                                            <p className="text-sm text-gray-600">
                                                {new Date(transaction.transaction_date).toLocaleDateString()} •{' '}
                                                {transaction.type}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-4">
                                    <div className={`text-lg font-semibold ${transaction.type === 'expense' ? 'text-red-600' : 'text-green-600'
                                        }`}>
                                        {transaction.type === 'expense' ? '-' : '+'}${Number(transaction.amount).toFixed(2)}
                                    </div>
                                    <button
                                        onClick={() => handleDelete(transaction.id)}
                                        className="text-red-600 hover:text-red-700 p-2"
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Add Transaction Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl p-8 max-w-md w-full">
                        <h2 className="text-2xl font-bold text-gray-900 mb-6">Add Transaction</h2>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                                <select
                                    value={formData.type}
                                    onChange={(e) => setFormData({ ...formData, type: e.target.value as 'expense' | 'income' })}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                >
                                    <option value="expense">Expense</option>
                                    <option value="income">Income</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Amount</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.amount}
                                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                                    required
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                    placeholder="0.00"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                                <input
                                    type="text"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    required
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                    placeholder="Lunch at restaurant"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Category (Optional)</label>
                                <select
                                    value={formData.category_id}
                                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
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
                                <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                                <input
                                    type="date"
                                    value={formData.transaction_date}
                                    onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                                    required
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                />
                            </div>

                            <div className="flex space-x-4 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowAddModal(false)}
                                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50 text-gray-700"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700"
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
