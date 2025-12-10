'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import type { Category, Transaction } from '@/lib/types';

interface BudgetWidgetProps {
    categories: Category[];
    transactions: Transaction[];
    onBudgetUpdate?: () => void;
}

interface CategorySpending {
    category: Category;
    spent: number;
    limit: number;
    percentage: number;
}

function calculateCategorySpending(
    categories: Category[],
    transactions: Transaction[]
): CategorySpending[] {
    // Filter categories with budget limits
    const budgetedCategories = categories.filter(
        (cat) => cat.monthly_limit !== null && cat.monthly_limit > 0
    );

    if (budgetedCategories.length === 0) {
        return [];
    }

    // Get current month's date range
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    // Calculate spending for each category
    return budgetedCategories.map((category) => {
        const spent = transactions
            .filter((t) => {
                const [year, month, day] = t.transaction_date.split('T')[0].split('-').map(Number);
                const txDate = new Date(year, month - 1, day);
                return (
                    t.category_id === category.id &&
                    t.type === 'expense' &&
                    txDate.getMonth() === currentMonth &&
                    txDate.getFullYear() === currentYear
                );
            })
            .reduce((sum, t) => sum + Number(t.amount), 0);

        const limit = category.monthly_limit!;
        const percentage = (spent / limit) * 100;

        return { category, spent, limit, percentage };
    });
}

function getProgressColor(percentage: number): string {
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 80) return 'bg-yellow-500';
    return 'bg-green-500';
}

export default function BudgetWidget({ categories, transactions, onBudgetUpdate }: BudgetWidgetProps) {
    const [showModal, setShowModal] = useState(false);
    const [budgetLimits, setBudgetLimits] = useState<Record<string, string>>({});
    const [saving, setSaving] = useState(false);

    const categorySpending = calculateCategorySpending(categories, transactions);
    const expenseCategories = categories.filter(cat => cat.type === 'expense');

    const handleOpenModal = () => {
        // Initialize budget limits from existing categories
        const limits: Record<string, string> = {};
        categories.forEach(cat => {
            if (cat.monthly_limit) {
                limits[cat.id] = cat.monthly_limit.toString();
            }
        });
        setBudgetLimits(limits);
        setShowModal(true);
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            // Update each category with new budget limit
            const updates = Object.entries(budgetLimits).map(([categoryId, limit]) => {
                const limitValue = limit ? parseFloat(limit) : null;
                return apiClient.put(`/api/v1/categories/${categoryId}`, {
                    monthly_limit: limitValue
                });
            });

            await Promise.all(updates);

            toast.success('Budget limits updated successfully');
            setShowModal(false);
            onBudgetUpdate?.();
        } catch (error) {
            console.error('Failed to update budgets:', error);
            toast.error('Failed to update budget limits');
        } finally {
            setSaving(false);
        }
    };

    return (
        <>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg md:text-xl font-semibold text-gray-900">Budget Overview</h2>
                    <button
                        onClick={handleOpenModal}
                        className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
                    >
                        Set Budgets
                    </button>
                </div>

                {categorySpending.length === 0 ? (
                    <p className="text-sm md:text-base text-gray-500 text-center py-4">
                        No budgets set. Click "Set Budgets" to add monthly limits!
                    </p>
                ) : (
                    <div className="space-y-4">
                        {categorySpending.map(({ category, spent, limit, percentage }) => (
                            <div key={category.id} className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className="text-lg md:text-xl">{category.icon}</span>
                                        <span className="text-sm md:text-base font-medium text-gray-900">
                                            {category.name}
                                        </span>
                                    </div>
                                    <span className="text-xs md:text-sm text-gray-600">
                                        ${spent.toFixed(2)} / ${limit.toFixed(2)}
                                    </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2.5">
                                    <div
                                        className={`h-2.5 rounded-full transition-all ${getProgressColor(percentage)}`}
                                        style={{ width: `${Math.min(percentage, 100)}%` }}
                                    />
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-gray-500">
                                        {percentage.toFixed(0)}% used
                                    </span>
                                    {percentage >= 100 && (
                                        <span className="text-xs font-semibold text-red-600">
                                            Over budget by ${(spent - limit).toFixed(2)}
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Budget Settings Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={() => setShowModal(false)}>
                    <div className="bg-white rounded-2xl p-6 max-w-md w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">Set Monthly Budgets</h2>
                        <p className="text-sm text-gray-600 mb-6">
                            Set monthly spending limits for your expense categories. Leave blank to remove budget.
                        </p>

                        <div className="space-y-4 mb-6">
                            {expenseCategories.map((category) => (
                                <div key={category.id}>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        <span className="mr-2">{category.icon}</span>
                                        {category.name}
                                    </label>
                                    <div className="relative">
                                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                                        <input
                                            type="number"
                                            step="0.01"
                                            min="0"
                                            value={budgetLimits[category.id] || ''}
                                            onChange={(e) => setBudgetLimits({
                                                ...budgetLimits,
                                                [category.id]: e.target.value
                                            })}
                                            className="w-full pl-7 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900"
                                            placeholder="No limit"
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={() => setShowModal(false)}
                                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50"
                                disabled={saving}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSave}
                                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
                                disabled={saving}
                            >
                                {saving ? 'Saving...' : 'Save Budgets'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
