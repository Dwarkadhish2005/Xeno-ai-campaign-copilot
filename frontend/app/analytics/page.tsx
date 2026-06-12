'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { getCampaignAnalytics, getDashboard, getTimeline, getCampaigns } from '@/lib/api';
import { formatNumber, CHANNEL_ICONS } from '@/lib/utils';
import { useToast } from '@/components/ui/Toast';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  AreaChart, Area, CartesianGrid, Legend,
} from 'recharts';

const FUNNEL_COLORS = ['#6366f1', '#10b981', '#38bdf8', '#f59e0b', '#a78bfa'];

function AnalyticsContent() {
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [campRes, dashRes] = await Promise.all([
          getCampaigns(),
          getDashboard(),
        ]);
        const allCampaigns = campRes.data.data.items || [];
        setCampaigns(allCampaigns);
        setDashboard(dashRes.data.data);

        // Check if campaign param in URL
        const paramId = searchParams.get('campaign');
        const initialId = paramId ? Number(paramId) : allCampaigns[0]?.id;
        if (initialId) {
          setSelectedId(initialId);
        }
      } catch {
        toast('Failed to load analytics', 'error');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    const loadAnalytics = async () => {
      try {
        const [analyticsRes, timelineRes] = await Promise.all([
          getCampaignAnalytics(selectedId),
          getTimeline(selectedId),
        ]);
        setAnalytics(analyticsRes.data.data);
        setTimeline(timelineRes.data.data || []);
      } catch {
        setAnalytics(null);
        setTimeline([]);
      }
    };
    loadAnalytics();
  }, [selectedId]);

  const metrics = analytics?.metrics || {};
  const funnel = analytics?.funnel || {};

  const funnelData = [
    { name: 'Sent', value: metrics.sent || 0, color: '#6366f1' },
    { name: 'Delivered', value: metrics.delivered || 0, color: '#38bdf8' },
    { name: 'Opened', value: metrics.opened || 0, color: '#10b981' },
    { name: 'Clicked', value: metrics.clicked || 0, color: '#f59e0b' },
  ].filter((d) => d.value > 0);

  const overallMetrics = dashboard?.overall_metrics || {};
  const segments = dashboard?.segment_distribution || {};

  if (loading) {
    return (
      <div>
        <div className="skeleton" style={{ height: '40px', width: '300px', marginBottom: '24px' }} />
        <div className="grid-4" style={{ marginBottom: '24px' }}>
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton" style={{ height: '100px', borderRadius: '16px' }} />)}
        </div>
        <div className="skeleton" style={{ height: '300px', borderRadius: '16px' }} />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h1 className="section-title" style={{ fontSize: '28px' }}>📊 Analytics</h1>
        <p className="section-subtitle">Track campaign performance and customer engagement</p>
      </div>

      {/* Dashboard Totals */}
      <div className="grid-4" style={{ marginBottom: '28px' }}>
        {[
          { label: 'Messages Sent', value: formatNumber(overallMetrics.total_sent || 0), icon: '📤', color: '#6366f1' },
          { label: 'Delivered', value: formatNumber(overallMetrics.total_delivered || 0), icon: '✅', color: '#10b981' },
          { label: 'Opened', value: formatNumber(overallMetrics.total_opened || 0), icon: '👁️', color: '#38bdf8' },
          { label: 'Clicked', value: formatNumber(overallMetrics.total_clicked || 0), icon: '🖱️', color: '#f59e0b' },
        ].map((m) => (
          <div key={m.label} className="metric-card">
            <div className="metric-value" style={{ color: m.color }}>{m.value}</div>
            <div className="metric-label">{m.icon} {m.label}</div>
          </div>
        ))}
      </div>

      {/* Campaign Selector */}
      {campaigns.length > 0 && (
        <div className="glass-card" style={{ padding: '20px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ fontSize: '14px', fontWeight: '600', color: '#94a3b8', flexShrink: 0 }}>Select Campaign:</div>
          <select
            className="input"
            style={{ maxWidth: '400px' }}
            value={selectedId || ''}
            onChange={(e) => setSelectedId(Number(e.target.value))}
          >
            <option value="">-- Choose a campaign --</option>
            {campaigns.map((c: any) => (
              <option key={c.id} value={c.id}>
                {CHANNEL_ICONS[c.channel]} {c.name} ({c.status})
              </option>
            ))}
          </select>
        </div>
      )}

      {analytics && (
        <>
          {/* Per-campaign header */}
          <div className="glass-card" style={{ padding: '20px', marginBottom: '24px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontWeight: '700', fontSize: '18px' }}>{analytics.name}</div>
              <div style={{ fontSize: '13px', color: '#64748b' }}>
                {CHANNEL_ICONS[analytics.channel]} {analytics.channel} • {formatNumber(analytics.audience_size)} recipients
              </div>
            </div>
            <span className={`badge badge-${analytics.status}`}>{analytics.status}</span>
          </div>

          {/* Metrics Row */}
          <div className="grid-4" style={{ marginBottom: '24px' }}>
            {funnelData.map((d) => (
              <div key={d.name} className="metric-card">
                <div className="metric-value" style={{ color: d.color }}>{formatNumber(d.value)}</div>
                <div className="metric-label">{d.name}</div>
                {analytics.audience_size > 0 && (
                  <div style={{ fontSize: '11px', color: '#475569', marginTop: '4px' }}>
                    {((d.value / analytics.audience_size) * 100).toFixed(1)}% of audience
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="grid-2" style={{ marginBottom: '24px' }}>
            {/* Funnel Chart */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h2 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '20px', color: '#94a3b8' }}>
                📉 Engagement Funnel
              </h2>
              {funnelData.length > 0 ? (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={funnelData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                    <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
                    />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                      {funnelData.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ textAlign: 'center', padding: '60px', color: '#475569' }}>
                  No engagement data yet
                </div>
              )}
            </div>

            {/* Funnel Stats */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h2 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '20px', color: '#94a3b8' }}>
                📊 Conversion Rates
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {[
                  { label: 'Sent → Delivered', value: funnel.sent_to_delivered || '0%', color: '#10b981' },
                  { label: 'Delivered → Opened', value: funnel.delivered_to_opened || '0%', color: '#38bdf8' },
                  { label: 'Opened → Clicked', value: funnel.opened_to_clicked || '0%', color: '#f59e0b' },
                  { label: 'Overall Engagement', value: funnel.overall_engagement || '0%', color: '#a78bfa' },
                ].map((item) => (
                  <div key={item.label} className="funnel-step">
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '6px' }}>{item.label}</div>
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{
                            width: item.value,
                            background: `linear-gradient(90deg, ${item.color}88, ${item.color})`,
                          }}
                        />
                      </div>
                    </div>
                    <div style={{ fontSize: '16px', fontWeight: '800', color: item.color, flexShrink: 0 }}>
                      {item.value}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Timeline Chart */}
          {timeline.length > 0 && (
            <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '20px', color: '#94a3b8' }}>
                📈 Engagement Timeline
              </h2>
              <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={timeline}>
                  <defs>
                    <linearGradient id="colorSent" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorOpened" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorClicked" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => v?.slice(11, 16)} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }} />
                  <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: '12px' }}>{v}</span>} />
                  <Area type="monotone" dataKey="sent" stroke="#6366f1" fill="url(#colorSent)" strokeWidth={2} />
                  <Area type="monotone" dataKey="opened" stroke="#10b981" fill="url(#colorOpened)" strokeWidth={2} />
                  <Area type="monotone" dataKey="clicked" stroke="#f59e0b" fill="url(#colorClicked)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}

      {/* Segment Distribution (always shown) */}
      {Object.keys(segments).length > 0 && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '16px', color: '#94a3b8' }}>
            👥 Customer Segment Distribution
          </h2>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            {Object.entries(segments).map(([seg, count]) => {
              const segColors: Record<string, string> = {
                vip: '#f59e0b', dormant: '#6366f1', frequent: '#10b981',
                new: '#38bdf8', at_risk: '#ef4444', regular: '#94a3b8',
              };
              const color = segColors[seg] || '#64748b';
              return (
                <div key={seg} style={{
                  flex: '1', minWidth: '120px', padding: '16px',
                  background: `${color}12`,
                  border: `1px solid ${color}33`,
                  borderRadius: '12px', textAlign: 'center',
                }}>
                  <div style={{ fontSize: '24px', fontWeight: '800', color }}>{count as number}</div>
                  <div style={{ fontSize: '12px', color: '#64748b', textTransform: 'capitalize', marginTop: '4px' }}>{seg}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {!loading && campaigns.length === 0 && (
        <div style={{ textAlign: 'center', padding: '80px', color: '#475569' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
          <div style={{ fontSize: '18px', fontWeight: '600', color: '#94a3b8', marginBottom: '12px' }}>No analytics yet</div>
          <div>Launch some campaigns first to see analytics here</div>
        </div>
      )}
    </div>
  );
}

export default function AnalyticsPage() {
  return (
    <Suspense fallback={<div style={{ color: '#64748b', padding: '40px' }}>Loading analytics...</div>}>
      <AnalyticsContent />
    </Suspense>
  );
}
