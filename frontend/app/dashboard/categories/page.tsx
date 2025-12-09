'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import type { Category } from '@/lib/types';

export default function CategoriesPage() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddModal, setShowAddModal] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        icon: '📦',
        color: '#6366f1',
        type: 'expense' as 'expense' | 'income',
    });

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const cats = await apiClient.get<Category[]>('/api/v1/categories');
            setCategories(cats);
        } catch (error) {
            console.error('Failed to fetch categories:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            await apiClient.post('/api/v1/categories', formData);
            setShowAddModal(false);
            setFormData({
                name: '',
                icon: '📦',
                color: '#6366f1',
                type: 'expense',
            });
            fetchCategories();
        } catch (error: any) {
            alert(error.message || 'Failed to create category');
        }
    };

    const handleDelete = async (id: string, isSystem: boolean) => {
        if (isSystem) {
            alert('Cannot delete system categories');
            return;
        }

        if (!confirm('Are you sure you want to delete this category?')) return;

        try {
            await apiClient.delete(`/api/v1/categories/${id}`);
            fetchCategories();
        } catch (error) {
            console.error('Failed to delete category:', error);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    const expenseCategories = categories.filter((c) => c.type === 'expense');
    const incomeCategories = categories.filter((c) => c.type === 'income');

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Categories</h1>
                    <p className="text-gray-600 mt-1">Manage your transaction categories</p>
                </div>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all"
                >
                    + Add Category
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Expense Categories */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Expense Categories</h2>
                    <div className="space-y-2">
                        {expenseCategories.map((category) => (
                            <div
                                key={category.id}
                                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50"
                            >
                                <div className="flex items-center space-x-3">
                                    <span className="text-2xl">{category.icon}</span>
                                    <div>
                                        <p className="font-medium text-gray-900">{category.name}</p>
                                        {category.is_system && (
                                            <p className="text-xs text-gray-500">System</p>
                                        )}
                                    </div>
                                </div>
                                {!category.is_system && (
                                    <button
                                        onClick={() => handleDelete(category.id, category.is_system)}
                                        className="text-red-600 hover:text-red-700 p-2"
                                    >
                                        🗑️
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Income Categories */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Income Categories</h2>
                    <div className="space-y-2">
                        {incomeCategories.map((category) => (
                            <div
                                key={category.id}
                                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50"
                            >
                                <div className="flex items-center space-x-3">
                                    <span className="text-2xl">{category.icon}</span>
                                    <div>
                                        <p className="font-medium text-gray-900">{category.name}</p>
                                        {category.is_system && (
                                            <p className="text-xs text-gray-500">System</p>
                                        )}
                                    </div>
                                </div>
                                {!category.is_system && (
                                    <button
                                        onClick={() => handleDelete(category.id, category.is_system)}
                                        className="text-red-600 hover:text-red-700 p-2"
                                    >
                                        🗑️
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Add Category Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl p-8 max-w-md w-full">
                        <h2 className="text-2xl font-bold text-gray-900 mb-6">Add Category</h2>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                    placeholder="Groceries"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Icon (Emoji)</label>
                                <input
                                    type="text"
                                    value={formData.icon}
                                    onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900 placeholder-gray-500"
                                    placeholder="🛒"
                                />
                            </div>

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
                                    Add Category
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
