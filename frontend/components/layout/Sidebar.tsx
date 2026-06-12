'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/', label: 'Dashboard', icon: '🏠' },
  { href: '/upload', label: 'Upload Data', icon: '📤' },
  { href: '/planner', label: 'AI Planner', icon: '🤖' },
  { href: '/campaigns', label: 'Campaigns', icon: '🚀' },
  { href: '/analytics', label: 'Analytics', icon: '📊' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '10px',
            background: 'linear-gradient(135deg, #6366f1, #a78bfa)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '18px', flexShrink: 0,
          }}>✨</div>
          <div>
            <div style={{ fontSize: '14px', fontWeight: '700', color: '#f8fafc' }}>Xeno AI</div>
            <div style={{ fontSize: '11px', color: '#64748b', fontWeight: '500' }}>Campaign Copilot</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1 }}>
        <div style={{ fontSize: '11px', fontWeight: '600', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: '8px', paddingLeft: '14px' }}>
          Navigation
        </div>
        {navItems.map((item) => {
          const isActive = item.href === '/'
            ? pathname === '/'
            : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <span style={{ fontSize: '16px' }}>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div style={{ paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ fontSize: '11px', color: '#475569', textAlign: 'center' }}>
          v2.0 • Powered by Groq AI
        </div>
      </div>
    </aside>
  );
}
