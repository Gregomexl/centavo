'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';

export default function SettingsPage() {
    const [linkCode, setLinkCode] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const generateLinkCode = async () => {
        setLoading(true);
        try {
            const response = await apiClient.post<{ code: string }>('/api/v1/users/link/code', {});
            setLinkCode(response.code);
        } catch (error) {
            console.error('Failed to generate link code:', error);
            alert('Failed to generate code. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6 md:space-y-8">
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Settings</h1>

            {/* Telegram Integration Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6 lg:p-8">
                <div className="flex items-start justify-between">
                    <div>
                        <h2 className="text-lg md:text-xl font-bold text-gray-900 flex items-center">
                            <span className="text-xl md:text-2xl mr-2">🤖</span>
                            Connect Telegram Bot
                        </h2>
                        <p className="text-sm md:text-base text-gray-600 mt-2 max-w-xl">
                            Link your Telegram account to log expenses on the go.
                            Just verify your code here and send it to the bot.
                        </p>
                    </div>
                </div>

                <div className="mt-6 md:mt-8 bg-gray-50 rounded-xl p-4 md:p-6 border border-gray-200">
                    {!linkCode ? (
                        <div className="text-center py-4">
                            <button
                                onClick={generateLinkCode}
                                disabled={loading}
                                className="w-full sm:w-auto px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors disabled:opacity-50"
                            >
                                {loading ? 'Generating...' : 'Generate Link Code'}
                            </button>
                        </div>
                    ) : (
                        <div className="text-center">
                            <p className="text-sm md:text-base text-gray-600 mb-2">Send this command to the bot:</p>
                            <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-3 md:p-4 inline-block mb-4 max-w-full overflow-x-auto">
                                <code className="text-lg md:text-2xl font-mono font-bold text-indigo-600 break-all">
                                    /link {linkCode}
                                </code>
                            </div>
                            <p className="text-xs md:text-sm text-gray-500">
                                This code expires in 5 minutes.
                            </p>
                            <button
                                onClick={() => setLinkCode(null)}
                                className="mt-4 text-xs md:text-sm text-gray-500 hover:text-gray-700 active:text-gray-800 underline min-h-[44px] px-3 py-2"
                            >
                                Generate new code
                            </button>
                        </div>
                    )}
                </div>

                <div className="mt-6 md:mt-8 border-t border-gray-100 pt-6">
                    <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-4">How it works:</h3>
                    <ol className="list-decimal list-inside space-y-2 text-sm md:text-base text-gray-600">
                        <li>Open the <strong>Centavo Bot</strong> on Telegram</li>
                        <li>Type the command shown above</li>
                        <li>You'll receive a confirmation message</li>
                        <li>Start logging expenses directly from Telegram!</li>
                    </ol>
                </div>
            </div>
        </div>
    );
}
