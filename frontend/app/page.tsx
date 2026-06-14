'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import Link from 'next/link';
import { getDashboard, generateProfiles, clearDatabase } from '@/lib/api';
import { formatCurrency, formatNumber, STATUS_COLORS, CHANNEL_ICONS, timeAgo } from '@/lib/utils';
import { useToast } from '@/components/ui/Toast';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const SEGMENT_COLORS: Record<string, string> = {
  vip: '#f59e0b',
  dormant: '#6366f1',
  frequent: '#10b981',
  new: '#38bdf8',
  at_risk: '#ef4444',
  regular: '#94a3b8',
  unknown: '#475569',
};

type ClearMode = 'campaigns_only' | 'all';

export default function DashboardPage() {
  const { toast } = useToast();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generatingProfiles, setGeneratingProfiles] = useState(false);
  const [clearModalOpen, setClearModalOpen] = useState(false);
  const [clearMode, setClearMode] = useState<ClearMode>('campaigns_only');
  const [clearing, setClearing] = useState(false);
  const isMounted = useRef(true);

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const res = await getDashboard();
      if (isMounted.current) {
        setData(res.data.data);
      }
    } catch {
      if (isMounted.current) {
        toast('Failed to load dashboard data', 'error');
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, []);

  // Initial load
  useEffect(() => {
    isMounted.current = true;
    load();

    // Re-fetch when user returns to this tab (fixes stale data after navigating away)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        load(true); // silent refresh — keeps existing data visible while refreshing
      }
    };

    // Re-fetch when window regains focus (e.g., Alt+Tab back)
    const handleFocus = () => {
      load(true);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);

    return () => {
      isMounted.current = false;
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, [load]);

  const handleGenerateProfiles = async () => {
    setGeneratingProfiles(true);
    try {
      await generateProfiles();
      toast('Customer profiles generated!', 'success');
      await load(); // full refresh with loading state
    } catch {
      toast('Failed to generate profiles', 'error');
    } finally {
      setGeneratingProfiles(false);
    }
  };

  const handleClearDatabase = async () => {
    setClearing(true);
    try {
      const res = await clearDatabase(clearMode);
      const msg = res.data.message || 'Database cleared.';
      toast(msg, 'success');
      setClearModalOpen(false);
      setData(null);
      await load(); // full refresh
    } catch (e: any) {
      toast(e.response?.data?.detail || 'Failed to clear database', 'error');
    } finally {
      setClearing(false);
    }
  };

  const segmentData = data?.segment_distribution
    ? Object.entries(data.segment_distribution).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value: value as number,
        key: name,
      }))
    : [];

  const metrics = data?.overall_metrics || {};

  return (
    <div>
      {/* Clear Database Confirmation Modal */}
      {clearModalOpen && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 1000,
          background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          padding: '24px',
        }}>
          <div style={{
            background: '#0f172a', border: '1px solid rgba(239,68,68,0.4)',
            borderRadius: '16px', padding: '32px', maxWidth: '480px', width: '100%',
            boxShadow: '0 25px 60px rgba(0,0,0,0.6)',
          }}>
            <div style={{ fontSize: '40px', marginBottom: '16px', textAlign: 'center' }}>⚠️</div>
            <h2 style={{ fontSize: '20px', fontWeight: '800', color: '#ef4444', marginBottom: '8px', textAlign: 'center' }}>
              Clear Database
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '14px', textAlign: 'center', marginBottom: '24px', lineHeight: '1.6' }}>
              This action is <strong style={{ color: '#f87171' }}>irreversible</strong>. Choose what to clear:
            </p>

            {/* Mode selector */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
              {([
                {
                  value: 'campaigns_only' as ClearMode,
                  label: '🚀 Campaigns Only',
                  desc: 'Deletes all campaigns, logs & audience data. Keeps customers & orders.',
                },
                {
                  value: 'all' as ClearMode,
                  label: '🗑️ Full Wipe (Everything)',
                  desc: 'Deletes ALL data including customers, orders, and campaigns.',
                },
              ] as const).map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setClearMode(opt.value)}
                  style={{
                    padding: '14px 16px', borderRadius: '10px', textAlign: 'left',
                    border: `1px solid ${clearMode === opt.value ? 'rgba(239,68,68,0.6)' : 'rgba(255,255,255,0.08)'}`,
                    background: clearMode === opt.value ? 'rgba(239,68,68,0.12)' : 'rgba(255,255,255,0.03)',
                    cursor: 'pointer', transition: 'all 0.15s',
                  }}
                >
                  <div style={{ fontWeight: '700', fontSize: '14px', color: clearMode === opt.value ? '#f87171' : '#94a3b8', marginBottom: '4px' }}>
                    {opt.label}
                  </div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>{opt.desc}</div>
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setClearModalOpen(false)}
                disabled={clearing}
                style={{
                  flex: 1, padding: '10px 0', borderRadius: '8px', fontWeight: '600',
                  border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.05)',
                  color: '#94a3b8', cursor: 'pointer', fontSize: '14px',
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleClearDatabase}
                disabled={clearing}
                style={{
                  flex: 1, padding: '10px 0', borderRadius: '8px', fontWeight: '700',
                  border: '1px solid rgba(239,68,68,0.5)', background: 'rgba(239,68,68,0.2)',
                  color: '#f87171', cursor: clearing ? 'not-allowed' : 'pointer', fontSize: '14px',
                  opacity: clearing ? 0.6 : 1,
                }}
              >
                {clearing ? '⏳ Clearing...' : '🗑️ Confirm Clear'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 className="section-title" style={{ fontSize: '28px', marginBottom: '8px' }}>
            Welcome to{' '}
            <span className="gradient-text">Xeno AI Campaign Copilot</span>
          </h1>
          <p className="section-subtitle">AI-native customer engagement platform</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button
            onClick={() => load()}
            disabled={loading}
            style={{
              padding: '8px 16px', borderRadius: '8px', fontSize: '13px', fontWeight: '600',
              border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.05)',
              color: '#94a3b8', cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s', opacity: loading ? 0.6 : 1,
            }}
            onMouseEnter={e => !loading && (e.currentTarget.style.background = 'rgba(255,255,255,0.09)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.05)')}
          >
            {loading ? '⏳ Loading...' : '↺ Refresh'}
          </button>
          <button
            className="btn-secondary"
            onClick={handleGenerateProfiles}
            disabled={generatingProfiles}
          >
            {generatingProfiles ? '⏳ Generating...' : '🔄 Refresh Profiles'}
          </button>
          <button
            onClick={() => setClearModalOpen(true)}
            style={{
              padding: '8px 16px', borderRadius: '8px', fontSize: '13px', fontWeight: '600',
              border: '1px solid rgba(239,68,68,0.3)', background: 'rgba(239,68,68,0.08)',
              color: '#f87171', cursor: 'pointer', transition: 'all 0.15s',
            }}
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.16)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.08)')}
          >
            🗑️ Clear Database
          </button>
          <Link href="/planner">
            <button className="btn-primary">✨ New Campaign</button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid-4" style={{ marginBottom: '24px' }}>
        {[
          { label: 'Total Customers', value: loading ? '...' : formatNumber(data?.total_customers || 0), icon: '👥', color: '#38bdf8' },
          { label: 'Total Orders', value: loading ? '...' : formatNumber(data?.total_orders || 0), icon: '🛒', color: '#10b981' },
          { label: 'Total Revenue', value: loading ? '...' : formatCurrency(data?.total_revenue || 0), icon: '💰', color: '#f59e0b' },
          { label: 'Total Campaigns', value: loading ? '...' : formatNumber(data?.total_campaigns || 0), icon: '🚀', color: '#a78bfa' },
        ].map((stat) => (
          <div key={stat.label} className="stat-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
              <span style={{ fontSize: '28px' }}>{stat.icon}</span>
              <div style={{
                width: '8px', height: '8px', borderRadius: '50%',
                background: stat.color, boxShadow: `0 0 8px ${stat.color}`,
              }} />
            </div>
            <div style={{ fontSize: '26px', fontWeight: '800', color: stat.color, letterSpacing: '-0.5px', marginBottom: '4px' }}>
              {loading ? <div className="skeleton" style={{ height: '32px', width: '80px' }} /> : stat.value}
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', fontWeight: '500' }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Communication Metrics Row */}
      {!loading && metrics.total_sent > 0 && (
        <div className="grid-4" style={{ marginBottom: '24px' }}>
          {[
            { label: 'Messages Sent', value: formatNumber(metrics.total_sent), icon: '📤', color: '#6366f1' },
            { label: 'Delivered', value: formatNumber(metrics.total_delivered), icon: '✅', color: '#10b981' },
            { label: 'Opened', value: formatNumber(metrics.total_opened), icon: '👁️', color: '#38bdf8' },
            { label: 'Clicked', value: formatNumber(metrics.total_clicked), icon: '🖱️', color: '#f59e0b' },
          ].map((m) => (
            <div key={m.label} className="metric-card">
              <div className="metric-value" style={{ color: m.color }}>{m.value}</div>
              <div className="metric-label">{m.icon} {m.label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="grid-2">
        {/* Segment Distribution */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 className="section-title" style={{ fontSize: '16px', marginBottom: '20px' }}>
            Customer Segments
          </h2>
          {loading ? (
            <div className="skeleton" style={{ height: '260px' }} />
          ) : segmentData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={segmentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={110}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {segmentData.map((entry) => (
                    <Cell key={entry.key} fill={SEGMENT_COLORS[entry.key] || '#6366f1'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
                />
                <Legend
                  formatter={(value) => <span style={{ color: '#94a3b8', fontSize: '12px' }}>{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ textAlign: 'center', padding: '60px 0', color: '#475569' }}>
              <div style={{ fontSize: '36px', marginBottom: '12px' }}>📊</div>
              <div>No segment data yet.</div>
              <div style={{ fontSize: '12px', marginTop: '4px' }}>Upload data and generate profiles first.</div>
            </div>
          )}
        </div>

        {/* Recent Campaigns */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 className="section-title" style={{ fontSize: '16px', marginBottom: 0 }}>
              Recent Campaigns
            </h2>
            <Link href="/campaigns" style={{ fontSize: '13px', color: '#6366f1', textDecoration: 'none' }}>
              View all →
            </Link>
          </div>
          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[...Array(4)].map((_, i) => (
                <div key={i} className="skeleton" style={{ height: '48px' }} />
              ))}
            </div>
          ) : data?.recent_campaigns?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {data.recent_campaigns.map((c: any) => (
                <Link key={c.id} href={`/campaigns/${c.id}`} style={{ textDecoration: 'none' }}>
                  <div style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '12px 14px',
                    background: 'rgba(255,255,255,0.03)',
                    borderRadius: '10px',
                    border: '1px solid rgba(255,255,255,0.05)',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.03)')}
                  >
                    <div>
                      <div style={{ fontWeight: '600', fontSize: '13px', marginBottom: '2px' }}>{c.name}</div>
                      <div style={{ fontSize: '11px', color: '#64748b' }}>
                        {CHANNEL_ICONS[c.channel]} {c.channel} • {c.audience_size} recipients • {timeAgo(c.created_at)}
                      </div>
                    </div>
                    <span className={`badge badge-${c.status}`}>{c.status}</span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '60px 0', color: '#475569' }}>
              <div style={{ fontSize: '36px', marginBottom: '12px' }}>🚀</div>
              <div>No campaigns yet.</div>
              <Link href="/planner">
                <button className="btn-primary" style={{ marginTop: '12px' }}>Create your first campaign</button>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="glass-card" style={{ padding: '24px', marginTop: '24px' }}>
        <h2 className="section-title" style={{ fontSize: '16px', marginBottom: '16px' }}>Quick Actions</h2>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <Link href="/upload">
            <button className="btn-secondary">📤 Upload Customer Data</button>
          </Link>
          <Link href="/planner">
            <button className="btn-primary">🤖 Generate AI Campaign</button>
          </Link>
          <Link href="/analytics">
            <button className="btn-secondary">📊 View Analytics</button>
          </Link>
        </div>
      </div>
    </div>
  );
}
