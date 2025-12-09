import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Centavo - Personal Expense Tracker',
  description: 'Track your expenses and income with ease',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
