import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import { ToastProvider } from '@/components/ui/Toast';

export const metadata: Metadata = {
  title: 'Xeno AI Campaign Copilot',
  description: 'AI-Native Customer Engagement Platform — Build, Launch & Analyze Campaigns',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ToastProvider>
          <Sidebar />
          <main className="main-content">
            {children}
          </main>
        </ToastProvider>
      </body>
    </html>
  );
}
