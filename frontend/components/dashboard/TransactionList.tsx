'use client';

import type { Transaction } from '@/lib/types';

interface TransactionListProps {
    transactions: Transaction[];
}

interface GroupedTransactions {
    [date: string]: Transaction[];
}

function groupTransactionsByDate(transactions: Transaction[]): GroupedTransactions {
    const sorted = [...transactions].sort((a, b) =>
        new Date(b.transaction_date).getTime() - new Date(a.transaction_date).getTime()
    );

    const grouped: GroupedTransactions = {};
    sorted.forEach((transaction) => {
        const dateKey = transaction.transaction_date.split('T')[0]; // Get YYYY-MM-DD
        if (!grouped[dateKey]) {
            grouped[dateKey] = [];
        }
        grouped[dateKey].push(transaction);
    });

    return grouped;
}

function getDateLabel(dateStr: string): string {
    // Parse the date string as YYYY-MM-DD in local timezone
    // Splitting and using Date constructor prevents UTC interpretation
    const [year, month, day] = dateStr.split('T')[0].split('-').map(Number);
    const date = new Date(year, month - 1, day); // month is 0-indexed

    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    // Reset time for comparison
    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const todayOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const yesterdayOnly = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate());

    if (dateOnly.getTime() === todayOnly.getTime()) {
        return 'Today';
    } else if (dateOnly.getTime() === yesterdayOnly.getTime()) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        });
    }
}

export default function TransactionList({ transactions }: TransactionListProps) {
    if (transactions.length === 0) {
        return (
            <div className="p-6 md:p-8 text-center text-sm md:text-base text-gray-500">
                No transactions yet. Start tracking your expenses!
            </div>
        );
    }

    const groupedTransactions = groupTransactionsByDate(transactions);

    return (
        <div>
            {Object.entries(groupedTransactions).map(([date, txs]) => (
                <div key={date}>
                    <div className="px-4 md:px-6 py-2 bg-gray-50 border-b border-gray-200">
                        <h3 className="text-xs md:text-sm font-semibold text-gray-700">
                            {getDateLabel(date)}
                        </h3>
                    </div>
                    <div className="divide-y divide-gray-200">
                        {txs.map((transaction) => (
                            <div key={transaction.id} className="p-4 md:p-6 hover:bg-gray-50 active:bg-gray-100">
                                <div className="flex items-center justify-between gap-3">
                                    <div className="flex items-center space-x-3 md:space-x-4 min-w-0 flex-1">
                                        <div className={`p-2 rounded-full flex-shrink-0 ${transaction.type === 'expense' ? 'bg-red-100' : 'bg-green-100'
                                            }`}>
                                            <span className="text-lg md:text-xl">
                                                {transaction.type === 'expense' ? '💸' : '💰'}
                                            </span>
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <p className="font-medium text-gray-900 text-sm md:text-base truncate">
                                                {transaction.description}
                                            </p>
                                            <p className="text-xs md:text-sm text-gray-500">
                                                {(() => {
                                                    const [year, month, day] = transaction.transaction_date.split('T')[0].split('-').map(Number);
                                                    return new Date(year, month - 1, day).toLocaleDateString();
                                                })()}
                                            </p>
                                        </div>
                                    </div>
                                    <div className={`text-base md:text-lg font-semibold flex-shrink-0 ${transaction.type === 'expense' ? 'text-red-600' : 'text-green-600'
                                        }`}>
                                        {transaction.type === 'expense' ? '-' : '+'}${Number(transaction.amount).toFixed(2)}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}
