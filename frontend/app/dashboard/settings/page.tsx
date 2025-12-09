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
        <div className="max-w-4xl mx-auto space-y-6">
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>

            {/* Telegram Integration Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
                <div className="flex items-start justify-between">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900 flex items-center">
                            <span className="text-2xl mr-2">🤖</span>
                            Connect Telegram Bot
                        </h2>
                        <p className="text-gray-600 mt-2 max-w-xl">
                            Link your Telegram account to log expenses on the go.
                            Just verify your code here and send it to the bot.
                        </p>
                    </div>
                </div>

                <div className="mt-8 bg-gray-50 rounded-xl p-6 border border-gray-200">
                    {!linkCode ? (
                        <div className="text-center py-4">
                            <button
                                onClick={generateLinkCode}
                                disabled={loading}
                                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
                            >
                                {loading ? 'Generating...' : 'Generate Link Code'}
                            </button>
                        </div>
                    ) : (
                        <div className="text-center">
                            <p className="text-gray-600 mb-2">Send this command to the bot:</p>
                            <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-4 inline-block mb-4">
                                <code className="text-2xl font-mono font-bold text-indigo-600">
                                    /link {linkCode}
                                </code>
                            </div>
                            <p className="text-sm text-gray-500">
                                This code expires in 5 minutes.
                            </p>
                            <button
                                onClick={() => setLinkCode(null)}
                                className="mt-4 text-sm text-gray-500 hover:text-gray-700 underline"
                            >
                                Generate new code
                            </button>
                        </div>
                    )}
                </div>

                <div className="mt-8 border-t border-gray-100 pt-6">
                    <h3 className="font-semibold text-gray-900 mb-4">How it works:</h3>
                    <ol className="list-decimal list-inside space-y-2 text-gray-600">
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
