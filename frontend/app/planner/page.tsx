'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { generatePlan, previewAudience, createCampaign } from '@/lib/api';
import type { Filter, CampaignPlan } from '@/lib/api';
import { useToast } from '@/components/ui/Toast';
import { CHANNEL_ICONS } from '@/lib/utils';

const EXAMPLE_GOALS = [
  'Bring back inactive customers who haven\'t purchased in 60+ days',
  'Reward our VIP customers with exclusive offers',
  'Onboard new customers with a welcome discount',
  'Re-engage frequent buyers with a loyalty reward',
  'Win back at-risk customers before they churn',
];

export default function PlannerPage() {
  const router = useRouter();
  const { toast } = useToast();

  const [goal, setGoal] = useState('');
  const [generating, setGenerating] = useState(false);
  const [plan, setPlan] = useState<CampaignPlan | null>(null);
  const [preview, setPreview] = useState<{ audience_size: number; sample: any[] } | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [creatingCampaign, setCreatingCampaign] = useState(false);
  const [campaignName, setCampaignName] = useState('');
  const [showNameInput, setShowNameInput] = useState(false);

  const handleGenerate = async () => {
    if (!goal.trim()) { toast('Please enter a business goal', 'error'); return; }
    setGenerating(true);
    setPlan(null);
    setPreview(null);
    try {
      const res = await generatePlan(goal);
      const planData = res.data.data;
      setPlan(planData);
      toast('Campaign plan generated!', 'success');
      // Auto preview
      setLoadingPreview(true);
      try {
        const prev = await previewAudience(planData.filters);
        setPreview(prev.data.data);
      } catch {
        toast('Could not load audience preview', 'error');
      } finally {
        setLoadingPreview(false);
      }
    } catch (e: any) {
      toast(e.response?.data?.detail || 'Failed to generate plan', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleCreateCampaign = async () => {
    if (!plan) return;
    if (!campaignName.trim()) { toast('Please enter a campaign name', 'error'); return; }
    setCreatingCampaign(true);
    try {
      const res = await createCampaign({
        name: campaignName,
        business_goal: goal,
        audience_name: plan.audience_name,
        filters: plan.filters,
        channel: plan.channel,
        strategy: plan.strategy,
        ai_reasoning: plan.reasoning,
      });
      toast(`Campaign "${campaignName}" created!`, 'success');
      router.push(`/campaigns/${res.data.data.id}`);
    } catch (e: any) {
      toast(e.response?.data?.detail || 'Failed to create campaign', 'error');
    } finally {
      setCreatingCampaign(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h1 className="section-title" style={{ fontSize: '28px' }}>🤖 AI Campaign Planner</h1>
        <p className="section-subtitle">Describe your business goal and let AI create the perfect campaign strategy</p>
      </div>

      {/* Goal Input */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>What's your business goal?</h2>
        <textarea
          className="input"
          style={{ resize: 'vertical', minHeight: '100px', lineHeight: '1.6' }}
          placeholder="e.g. Bring back customers who haven't purchased in 60 days with a 15% discount offer..."
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
        />
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '12px', marginBottom: '20px' }}>
          {EXAMPLE_GOALS.map((eg) => (
            <button
              key={eg}
              onClick={() => setGoal(eg)}
              style={{
                fontSize: '12px', padding: '5px 12px', borderRadius: '20px',
                background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
                color: '#a78bfa', cursor: 'pointer',
              }}
            >
              {eg.length > 45 ? eg.slice(0, 45) + '…' : eg}
            </button>
          ))}
        </div>
        <button className="btn-primary" onClick={handleGenerate} disabled={generating || !goal.trim()}>
          {generating ? '⏳ Generating plan...' : '✨ Generate AI Plan'}
        </button>
      </div>

      {/* Loading skeleton */}
      {generating && (
        <div className="glass-card" style={{ padding: '28px' }}>
          <div className="skeleton" style={{ height: '24px', width: '200px', marginBottom: '16px' }} />
          <div className="skeleton" style={{ height: '16px', width: '100%', marginBottom: '8px' }} />
          <div className="skeleton" style={{ height: '16px', width: '80%', marginBottom: '24px' }} />
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
            {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: '28px', width: '120px', borderRadius: '20px' }} />)}
          </div>
          <div className="skeleton" style={{ height: '80px' }} />
        </div>
      )}

      {/* AI Plan Card */}
      {plan && !generating && (
        <div className="glass-card" style={{ padding: '28px', marginBottom: '24px', border: '1px solid rgba(99,102,241,0.3)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>
            <div>
              <div style={{ fontSize: '12px', color: '#6366f1', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '6px' }}>
                ✨ AI Generated Plan
              </div>
              <h2 style={{ fontSize: '20px', fontWeight: '800', marginBottom: '6px' }}>{plan.audience_name}</h2>
              <span className="channel-badge">{CHANNEL_ICONS[plan.channel]} {plan.channel.toUpperCase()}</span>
            </div>
          </div>

          {/* Strategy */}
          <div style={{ padding: '14px 16px', background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.15)', borderRadius: '10px', marginBottom: '16px' }}>
            <div style={{ fontSize: '12px', color: '#6366f1', fontWeight: '700', marginBottom: '4px' }}>📋 STRATEGY</div>
            <div style={{ fontSize: '14px', color: '#c7d2fe' }}>{plan.strategy}</div>
          </div>

          {/* Filters */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              🎯 Audience Filters
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {plan.filters.map((f, i) => (
                <span key={i} className="filter-chip">
                  {f.field} {f.operator} {f.value}
                </span>
              ))}
            </div>
          </div>

          {/* Reasoning (collapsible) */}
          <details style={{ marginBottom: '16px' }}>
            <summary style={{ fontSize: '13px', color: '#64748b', cursor: 'pointer', padding: '8px 0' }}>
              🧠 AI Reasoning (click to expand)
            </summary>
            <div style={{ padding: '12px 14px', marginTop: '8px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', fontSize: '13px', color: '#94a3b8', lineHeight: '1.6' }}>
              {plan.reasoning}
            </div>
          </details>
        </div>
      )}

      {/* Audience Preview */}
      {(plan || loadingPreview) && !generating && (
        <div className="glass-card" style={{ padding: '28px', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>👥 Audience Preview</h2>
          {loadingPreview ? (
            <div className="skeleton" style={{ height: '120px' }} />
          ) : preview ? (
            <>
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: '10px',
                padding: '12px 20px', borderRadius: '12px',
                background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)',
                marginBottom: '20px',
              }}>
                <span style={{ fontSize: '24px', fontWeight: '800', color: '#10b981' }}>{preview.audience_size}</span>
                <span style={{ fontSize: '14px', color: '#6ee7b7' }}>customers match this audience</span>
              </div>
              {preview.sample.length > 0 && (
                <div style={{ overflowX: 'auto' }}>
                  <table className="data-table">
                    <thead>
                      <tr><th>Name</th><th>Email</th><th>City</th></tr>
                    </thead>
                    <tbody>
                      {preview.sample.map((c: any) => (
                        <tr key={c.id}>
                          <td style={{ fontWeight: '500' }}>{c.name}</td>
                          <td style={{ color: '#64748b' }}>{c.email}</td>
                          <td style={{ color: '#64748b' }}>{c.city || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {preview.audience_size > 10 && (
                    <div style={{ textAlign: 'center', padding: '12px', color: '#64748b', fontSize: '13px' }}>
                      ... and {preview.audience_size - 10} more customers
                    </div>
                  )}
                </div>
              )}
            </>
          ) : null}
        </div>
      )}

      {/* Create Campaign */}
      {plan && !generating && (
        <div className="glass-card" style={{ padding: '28px', border: '1px solid rgba(16,185,129,0.2)' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>🚀 Save as Campaign</h2>
          {!showNameInput ? (
            <button className="btn-success" onClick={() => setShowNameInput(true)}>
              💾 Create Campaign Draft
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: '240px' }}>
                <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '6px' }}>Campaign Name</label>
                <input
                  className="input"
                  placeholder="e.g. Dormant Revival Q1 2026"
                  value={campaignName}
                  onChange={(e) => setCampaignName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateCampaign()}
                  autoFocus
                />
              </div>
              <button className="btn-success" onClick={handleCreateCampaign} disabled={creatingCampaign || !campaignName.trim()}>
                {creatingCampaign ? '⏳ Creating...' : '✅ Create Campaign'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
