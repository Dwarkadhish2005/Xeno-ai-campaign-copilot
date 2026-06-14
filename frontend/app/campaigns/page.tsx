'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getCampaigns, deleteCampaign } from '@/lib/api';
import { CHANNEL_ICONS, formatNumber, timeAgo } from '@/lib/utils';
import { useToast } from '@/components/ui/Toast';

const STATUS_TABS = ['all', 'draft', 'ready', 'approved', 'running', 'completed', 'failed'];

export default function CampaignsPage() {
  const { toast } = useToast();
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  const load = async (status?: string) => {
    setLoading(true);
    try {
      const res = await getCampaigns(status === 'all' ? undefined : status);
      setCampaigns(res.data.data.items || []);
    } catch {
      toast('Failed to load campaigns', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(activeTab); }, [activeTab]);

  const handleDelete = async (id: number, name: string) => {
    if (!window.confirm(`Permanently delete "${name}" and all its data? This cannot be undone.`)) return;
    try {
      await deleteCampaign(id);
      toast(`Campaign "${name}" deleted.`, 'success');
      setCampaigns(prev => prev.filter(c => c.id !== id));
    } catch (e: any) {
      toast(e.response?.data?.detail || 'Delete failed', 'error');
    }
  };

  const statusColors: Record<string, string> = {
    all: '#6366f1', draft: '#94a3b8', ready: '#60a5fa', approved: '#c4b5fd',
    running: '#fcd34d', completed: '#6ee7b7', failed: '#fca5a5',
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 className="section-title" style={{ fontSize: '28px' }}>🚀 Campaigns</h1>
          <p className="section-subtitle">Manage your AI-powered marketing campaigns</p>
        </div>
        <Link href="/planner">
          <button className="btn-primary">✨ New Campaign</button>
        </Link>
      </div>

      {/* Status Tabs */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '24px' }}>
        {STATUS_TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '7px 16px', borderRadius: '8px', fontSize: '13px', fontWeight: '600',
              cursor: 'pointer', border: '1px solid',
              background: activeTab === tab ? `${statusColors[tab]}22` : 'rgba(255,255,255,0.03)',
              color: activeTab === tab ? statusColors[tab] : '#64748b',
              borderColor: activeTab === tab ? `${statusColors[tab]}44` : 'rgba(255,255,255,0.08)',
              transition: 'all 0.15s ease',
              textTransform: 'capitalize',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[...Array(5)].map((_, i) => (
              <div key={i} className="skeleton" style={{ height: '56px' }} />
            ))}
          </div>
        ) : campaigns.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 24px', color: '#475569' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🚀</div>
            <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: '#94a3b8' }}>No campaigns yet</div>
            <div style={{ fontSize: '14px', marginBottom: '24px' }}>
              {activeTab !== 'all' ? `No ${activeTab} campaigns` : 'Get started by creating your first AI campaign'}
            </div>
            <Link href="/planner">
              <button className="btn-primary">✨ Create your first campaign</button>
            </Link>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Campaign Name</th>
                <th>Channel</th>
                <th>Audience</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((c: any) => (
                <tr key={c.id}>
                  <td>
                    <div style={{ fontWeight: '600', marginBottom: '2px' }}>{c.name}</div>
                    {c.audience_name && (
                      <div style={{ fontSize: '12px', color: '#64748b' }}>{c.audience_name}</div>
                    )}
                  </td>
                  <td>
                    <span className="channel-badge">
                      {CHANNEL_ICONS[c.channel]} {c.channel}
                    </span>
                  </td>
                  <td style={{ color: '#38bdf8', fontWeight: '600' }}>
                    {formatNumber(c.audience_size)}
                  </td>
                  <td>
                    <span className={`badge badge-${c.status}`}>
                      {c.status === 'running' && '● '}{c.status}
                    </span>
                  </td>
                  <td style={{ color: '#64748b', fontSize: '12px' }}>
                    {timeAgo(c.created_at)}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <Link href={`/campaigns/${c.id}`}>
                          <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                            View
                          </button>
                        </Link>
                        {c.status === 'completed' && (
                          <Link href={`/analytics?campaign=${c.id}`}>
                            <button className="btn-primary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                              📊 Analytics
                            </button>
                          </Link>
                        )}
                        <button
                          onClick={() => handleDelete(c.id, c.name)}
                          style={{
                            padding: '6px 12px', fontSize: '12px', borderRadius: '8px',
                            border: '1px solid rgba(239,68,68,0.35)',
                            background: 'rgba(239,68,68,0.08)',
                            color: '#f87171', cursor: 'pointer', fontWeight: '600',
                            transition: 'all 0.15s',
                          }}
                          onMouseEnter={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.18)')}
                          onMouseLeave={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.08)')}
                        >
                          🗑️
                        </button>
                      </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
