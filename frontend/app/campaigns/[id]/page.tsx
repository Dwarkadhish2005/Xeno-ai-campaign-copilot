'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  getCampaign, generateMessage, approveCampaign, launchCampaign,
  resetCampaign, deleteCampaign, getCampaignAudience,
} from '@/lib/api';
import { CHANNEL_ICONS, formatNumber, formatDate } from '@/lib/utils';
import { useToast } from '@/components/ui/Toast';

function MessagePreview({ template }: { template: string }) {
  const highlighted = template
    .replace(/\{name\}/g, '<span style="background:rgba(99,102,241,0.3);color:#a78bfa;padding:1px 5px;border-radius:4px;font-weight:600">{name}</span>')
    .replace(/\{days_since_last_purchase\}/g, '<span style="background:rgba(245,158,11,0.3);color:#fcd34d;padding:1px 5px;border-radius:4px;font-weight:600">{days}</span>')
    .replace(/\{city\}/g, '<span style="background:rgba(16,185,129,0.3);color:#6ee7b7;padding:1px 5px;border-radius:4px;font-weight:600">{city}</span>');
  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: '12px', padding: '20px', lineHeight: '1.7', fontSize: '14px',
    }}
    dangerouslySetInnerHTML={{ __html: highlighted }}
    />
  );
}

export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const id = Number(params.id);

  const [campaign, setCampaign] = useState<any>(null);
  const [audience, setAudience] = useState<any[]>([]);
  const [audienceTotal, setAudienceTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState('');
  const isMounted = useRef(true);

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const [campRes, audRes] = await Promise.all([
        getCampaign(id),
        getCampaignAudience(id),
      ]);
      if (isMounted.current) {
        setCampaign(campRes.data.data);
        setAudience(audRes.data.data.items || []);
        setAudienceTotal(audRes.data.data.total || 0);
      }
    } catch {
      if (isMounted.current) {
        toast('Failed to load campaign', 'error');
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, [id]);

  useEffect(() => {
    isMounted.current = true;
    load();

    // Re-fetch when user returns to this tab (fixes stale status/metrics)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') load(true);
    };
    const handleFocus = () => load(true);

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);
    return () => {
      isMounted.current = false;
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, [id, load]);

  const handleGenerateMessage = async () => {
    setActionLoading('message');
    try {
      await generateMessage(id);
      toast('Message generated!', 'success');
      await load();
    } catch (e: any) {
      toast(e.response?.data?.detail || 'Message generation failed', 'error');
    } finally {
      setActionLoading('');
    }
  };

  const handleApprove = async () => {
    setActionLoading('approve');
    try {
      await approveCampaign(id);
      toast('Campaign approved!', 'success');
      await load();
    } catch (e: any) {
      toast(e.response?.data?.detail || 'Approval failed', 'error');
    } finally {
      setActionLoading('');
    }
  };

  const handleLaunch = async () => {
    if (!window.confirm('Launch this campaign? This will start sending messages to all audience members.')) return;
    setActionLoading('launch');
    try {
      await launchCampaign(id);
      toast('Campaign launched! Execution running in background.', 'success');
      await load();
    } catch (e: any) {
      toast(e.response?.data?.detail || 'Launch failed', 'error');
    } finally {
      setActionLoading('');
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Reset this campaign back to draft? This will clear all communication logs and audience data.')) return;
    setActionLoading('reset');
    try {
      await resetCampaign(id);
      toast('Campaign reset to draft!', 'success');
      await load();
    } catch (e: any) {
      toast(e.response?.data?.detail || 'Reset failed', 'error');
    } finally {
      setActionLoading('');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Permanently delete "${campaign?.name}" and ALL its data? This cannot be undone.`)) return;
    setActionLoading('delete');
    try {
      await deleteCampaign(id);
      toast('Campaign permanently deleted.', 'success');
      router.push('/campaigns');
    } catch (e: any) {
      toast(e.response?.data?.detail || 'Delete failed', 'error');
      setActionLoading('');
    }
  };

  if (loading) {
    return (
      <div>
        <div className="skeleton" style={{ height: '40px', width: '300px', marginBottom: '24px' }} />
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          <div className="skeleton" style={{ height: '200px', flex: 1, minWidth: '300px', borderRadius: '16px' }} />
          <div className="skeleton" style={{ height: '200px', flex: 1, minWidth: '300px', borderRadius: '16px' }} />
        </div>
      </div>
    );
  }

  if (!campaign) {
    return <div style={{ textAlign: 'center', padding: '80px', color: '#475569' }}>Campaign not found</div>;
  }

  const metrics = campaign.metrics || {};

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <Link href="/campaigns" style={{ fontSize: '13px', color: '#6366f1', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px', marginBottom: '12px' }}>
          ← Back to campaigns
        </Link>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap', marginBottom: '8px' }}>
              <h1 style={{ fontSize: '24px', fontWeight: '800', margin: 0 }}>{campaign.name}</h1>
              <span className={`badge badge-${campaign.status}`}>{campaign.status}</span>
              <span className="channel-badge">{CHANNEL_ICONS[campaign.channel]} {campaign.channel}</span>
            </div>
            {campaign.audience_name && (
              <div style={{ fontSize: '14px', color: '#64748b' }}>
                🎯 {campaign.audience_name} • {formatNumber(campaign.audience_size)} recipients
              </div>
            )}
          </div>
          {/* Actions */}
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {campaign.status === 'draft' && (
              <button
                className="btn-primary"
                onClick={handleGenerateMessage}
                disabled={actionLoading === 'message'}
              >
                {actionLoading === 'message' ? '⏳ Generating...' : '🤖 Generate Message'}
              </button>
            )}
            {campaign.status === 'ready' && (
              <button
                className="btn-success"
                onClick={handleApprove}
                disabled={actionLoading === 'approve'}
              >
                {actionLoading === 'approve' ? '⏳ Approving...' : '✅ Approve Campaign'}
              </button>
            )}
            {campaign.status === 'approved' && (
              <button
                className="btn-primary"
                onClick={handleLaunch}
                disabled={actionLoading === 'launch'}
                style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}
              >
                {actionLoading === 'launch' ? '⏳ Launching...' : '🚀 Launch Campaign'}
              </button>
            )}
            {campaign.status === 'completed' && (
              <Link href={`/analytics?campaign=${id}`}>
                <button className="btn-primary">📊 View Analytics</button>
              </Link>
            )}
            {campaign.status !== 'draft' && (
              <button
                onClick={handleReset}
                disabled={actionLoading === 'reset'}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: '1px solid rgba(239,68,68,0.4)',
                  background: 'rgba(239,68,68,0.1)',
                  color: '#f87171',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: '600',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.2)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.1)')}
              >
                {actionLoading === 'reset' ? '⏳ Resetting...' : '🔄 Reset to Draft'}
              </button>
            )}
            <button
              onClick={handleDelete}
              disabled={actionLoading === 'delete'}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid rgba(239,68,68,0.6)',
                background: 'rgba(239,68,68,0.15)',
                color: '#ef4444',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '700',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.28)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'rgba(239,68,68,0.15)')}
            >
              {actionLoading === 'delete' ? '⏳ Deleting...' : '🗑️ Delete Campaign'}
            </button>
          </div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: '24px' }}>
        {/* Campaign Info */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '16px', color: '#94a3b8' }}>Campaign Details</h2>
          <dl style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            {[
              { label: 'Status', value: <span className={`badge badge-${campaign.status}`}>{campaign.status}</span> },
              { label: 'Channel', value: <span className="channel-badge">{CHANNEL_ICONS[campaign.channel]} {campaign.channel}</span> },
              { label: 'Audience Size', value: <span style={{ color: '#38bdf8', fontWeight: '700' }}>{formatNumber(campaign.audience_size)}</span> },
              { label: 'Created', value: <span style={{ color: '#64748b', fontSize: '13px' }}>{formatDate(campaign.created_at)}</span> },
            ].map(({ label, value }) => (
              <div key={label}>
                <dt style={{ fontSize: '11px', color: '#475569', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>{label}</dt>
                <dd style={{ margin: 0 }}>{value}</dd>
              </div>
            ))}
          </dl>

          {campaign.strategy && (
            <div style={{ marginTop: '16px', padding: '12px 14px', background: 'rgba(99,102,241,0.08)', borderRadius: '8px', border: '1px solid rgba(99,102,241,0.15)' }}>
              <div style={{ fontSize: '11px', color: '#6366f1', fontWeight: '700', marginBottom: '4px' }}>STRATEGY</div>
              <div style={{ fontSize: '13px', color: '#c7d2fe' }}>{campaign.strategy}</div>
            </div>
          )}

          {campaign.business_goal && (
            <div style={{ marginTop: '12px', padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ fontSize: '11px', color: '#64748b', fontWeight: '700', marginBottom: '4px' }}>BUSINESS GOAL</div>
              <div style={{ fontSize: '13px', color: '#94a3b8' }}>{campaign.business_goal}</div>
            </div>
          )}

          {/* Filters */}
          {campaign.filters?.length > 0 && (
            <div style={{ marginTop: '12px' }}>
              <div style={{ fontSize: '11px', color: '#475569', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>Audience Filters</div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {campaign.filters.map((f: any, i: number) => (
                  <span key={i} className="filter-chip">{f.field} {f.operator} {f.value}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Metrics (if campaign ran) */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '16px', color: '#94a3b8' }}>
            {Object.keys(metrics).length > 0 ? 'Communication Metrics' : 'Message Preview'}
          </h2>
          {Object.keys(metrics).length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              {[
                { label: 'Sent', value: metrics.sent || 0, color: '#6366f1', icon: '📤' },
                { label: 'Delivered', value: metrics.delivered || 0, color: '#10b981', icon: '✅' },
                { label: 'Opened', value: metrics.opened || 0, color: '#38bdf8', icon: '👁️' },
                { label: 'Clicked', value: metrics.clicked || 0, color: '#f59e0b', icon: '🖱️' },
                { label: 'Failed', value: metrics.failed || 0, color: '#ef4444', icon: '❌' },
              ].map((m) => (
                <div key={m.label} className="metric-card">
                  <div className="metric-value" style={{ color: m.color }}>{formatNumber(m.value)}</div>
                  <div className="metric-label">{m.icon} {m.label}</div>
                </div>
              ))}
            </div>
          ) : campaign.message_template ? (
            <>
              <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '8px' }}>
                Highlighted tokens: <span style={{ color: '#a78bfa' }}>{'{name}'}</span> <span style={{ color: '#fcd34d' }}>{'{days}'}</span> <span style={{ color: '#6ee7b7' }}>{'{city}'}</span>
              </div>
              {campaign.subject_line && (
                <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.04)', borderRadius: '8px', fontSize: '13px', marginBottom: '12px', color: '#94a3b8' }}>
                  <span style={{ color: '#64748b', fontSize: '11px' }}>SUBJECT: </span>{campaign.subject_line}
                </div>
              )}
              <MessagePreview template={campaign.message_template} />
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#475569' }}>
              <div style={{ fontSize: '40px', marginBottom: '12px' }}>💬</div>
              <div style={{ marginBottom: '16px' }}>No message generated yet</div>
              {campaign.status === 'draft' && (
                <button className="btn-primary" onClick={handleGenerateMessage} disabled={actionLoading === 'message'}>
                  {actionLoading === 'message' ? '⏳ Generating...' : '🤖 Generate Message'}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* AI Reasoning */}
      {campaign.ai_reasoning && (
        <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
          <details>
            <summary style={{ fontSize: '14px', fontWeight: '600', cursor: 'pointer', color: '#94a3b8' }}>
              🧠 AI Reasoning
            </summary>
            <div style={{ marginTop: '12px', fontSize: '14px', color: '#64748b', lineHeight: '1.7' }}>
              {campaign.ai_reasoning}
            </div>
          </details>
        </div>
      )}

      {/* Audience Table */}
      {audience.length > 0 && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: '700', color: '#94a3b8', margin: 0 }}>
              👥 Audience ({formatNumber(audienceTotal)} customers)
            </h2>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>City</th>
                  <th>Segment</th>
                  <th>Total Spend</th>
                  <th>Days Inactive</th>
                </tr>
              </thead>
              <tbody>
                {audience.map((c: any, i: number) => (
                  <tr key={c.id}>
                    <td style={{ color: '#475569' }}>{i + 1}</td>
                    <td style={{ fontWeight: '600' }}>{c.name}</td>
                    <td style={{ color: '#64748b', fontSize: '12px' }}>{c.email}</td>
                    <td style={{ color: '#64748b' }}>{c.city || '—'}</td>
                    <td>
                      {c.segment && (
                        <span className={`badge badge-${c.segment === 'vip' ? 'approved' : c.segment === 'dormant' ? 'failed' : c.segment === 'frequent' ? 'completed' : c.segment === 'at_risk' ? 'running' : 'draft'}`} style={{ fontSize: '11px' }}>
                          {c.segment}
                        </span>
                      )}
                    </td>
                    <td style={{ color: '#10b981', fontWeight: '600' }}>
                      {c.total_spend ? `₹${Math.round(c.total_spend).toLocaleString()}` : '—'}
                    </td>
                    <td style={{ color: c.days_since_last_purchase > 60 ? '#ef4444' : '#94a3b8' }}>
                      {c.days_since_last_purchase != null ? `${c.days_since_last_purchase}d` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {audienceTotal > 50 && (
              <div style={{ textAlign: 'center', padding: '16px', color: '#475569', fontSize: '13px' }}>
                Showing first 50 of {formatNumber(audienceTotal)} audience members
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
