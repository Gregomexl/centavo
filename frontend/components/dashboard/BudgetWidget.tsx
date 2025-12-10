'use client';

import type { Category, Transaction } from '@/lib/types';

interface BudgetWidgetProps {
    categories: Category[];
    transactions: Transaction[];
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
                const txDate = new Date(t.transaction_date);
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

export default function BudgetWidget({ categories, transactions }: BudgetWidgetProps) {
    const categorySpending = calculateCategorySpending(categories, transactions);

    if (categorySpending.length === 0) {
        return (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6">
                <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-4">Budget Overview</h2>
                <p className="text-sm md:text-base text-gray-500 text-center py-4">
                    No budgets set. Add monthly limits to your categories to track spending!
                </p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-4">Budget Overview</h2>
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
        </div>
    );
}
