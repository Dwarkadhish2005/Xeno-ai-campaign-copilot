'use client';

import { useState, useRef } from 'react';
import { uploadCustomers, uploadOrders, generateProfiles } from '@/lib/api';
import { useToast } from '@/components/ui/Toast';

interface UploadResult {
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  inserted_count: number;
  errors?: Array<{ row: number; field: string; message: string }>;
}

function DropZone({
  label,
  icon,
  onUpload,
  accept,
  uploading,
  result,
}: {
  label: string;
  icon: string;
  onUpload: (file: File) => void;
  accept: string;
  uploading: boolean;
  result: UploadResult | null;
}) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) onUpload(file);
  };

  return (
    <div>
      <div
        className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          style={{ display: 'none' }}
          onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])}
        />
        <div style={{ fontSize: '40px', marginBottom: '12px' }}>{icon}</div>
        <div style={{ fontWeight: '600', marginBottom: '6px' }}>{label}</div>
        <div style={{ fontSize: '13px', color: '#64748b' }}>
          {uploading ? 'Uploading...' : 'Drag & drop or click to browse'}
        </div>
        {uploading && (
          <div style={{ marginTop: '16px' }}>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '70%', animation: 'none', background: 'linear-gradient(90deg, #6366f1, #a78bfa)' }} />
            </div>
          </div>
        )}
      </div>

      {result && (
        <div style={{ marginTop: '16px' }}>
          <div style={{
            background: result.invalid_rows === 0 ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)',
            border: `1px solid ${result.invalid_rows === 0 ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)'}`,
            borderRadius: '12px', padding: '16px',
          }}>
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: result.errors?.length ? '12px' : 0 }}>
              <div><span style={{ color: '#64748b', fontSize: '12px' }}>Total Rows</span><br /><strong style={{ color: '#38bdf8' }}>{result.total_rows}</strong></div>
              <div><span style={{ color: '#64748b', fontSize: '12px' }}>Inserted</span><br /><strong style={{ color: '#10b981' }}>{result.inserted_count}</strong></div>
              <div><span style={{ color: '#64748b', fontSize: '12px' }}>Errors</span><br /><strong style={{ color: result.invalid_rows > 0 ? '#f59e0b' : '#10b981' }}>{result.invalid_rows}</strong></div>
            </div>
            {result.errors && result.errors.length > 0 && (
              <div style={{ maxHeight: '160px', overflowY: 'auto' }}>
                <table className="data-table" style={{ fontSize: '12px' }}>
                  <thead>
                    <tr>
                      <th>Row</th><th>Field</th><th>Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.errors.slice(0, 10).map((err, i) => (
                      <tr key={i}>
                        <td style={{ color: '#f59e0b' }}>#{err.row}</td>
                        <td style={{ color: '#94a3b8' }}>{err.field}</td>
                        <td style={{ color: '#fca5a5' }}>{err.message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function UploadPage() {
  const { toast } = useToast();
  const [uploadingCustomers, setUploadingCustomers] = useState(false);
  const [uploadingOrders, setUploadingOrders] = useState(false);
  const [customersResult, setCustomersResult] = useState<UploadResult | null>(null);
  const [ordersResult, setOrdersResult] = useState<UploadResult | null>(null);
  const [generatingProfs, setGeneratingProfs] = useState(false);

  const handleCustomerUpload = async (file: File) => {
    setUploadingCustomers(true);
    try {
      const res = await uploadCustomers(file);
      setCustomersResult(res.data.data);
      toast(`Customers uploaded: ${res.data.data.inserted_count} inserted`, 'success');
    } catch (e: any) {
      toast(e.response?.data?.message || 'Customer upload failed', 'error');
    } finally {
      setUploadingCustomers(false);
    }
  };

  const handleOrderUpload = async (file: File) => {
    setUploadingOrders(true);
    try {
      const res = await uploadOrders(file);
      setOrdersResult(res.data.data);
      toast(`Orders uploaded: ${res.data.data.inserted_count} inserted`, 'success');
    } catch (e: any) {
      toast(e.response?.data?.message || 'Order upload failed', 'error');
    } finally {
      setUploadingOrders(false);
    }
  };

  const handleGenerateProfiles = async () => {
    setGeneratingProfs(true);
    try {
      await generateProfiles();
      toast('Customer profiles generated successfully!', 'success');
    } catch {
      toast('Profile generation failed', 'error');
    } finally {
      setGeneratingProfs(false);
    }
  };

  const bothUploaded = customersResult && ordersResult;

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h1 className="section-title" style={{ fontSize: '28px' }}>📤 Upload Data</h1>
        <p className="section-subtitle">Upload your CSV files to populate the platform with customer and order data</p>
      </div>

      <div className="grid-2" style={{ marginBottom: '24px' }}>
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '6px', color: '#38bdf8' }}>👥 Customers CSV</h2>
          <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '20px' }}>
            Required columns: customer_id, name, email, phone, city, signup_date
          </p>
          <DropZone
            label="Drop customers.csv here"
            icon="👥"
            onUpload={handleCustomerUpload}
            accept=".csv"
            uploading={uploadingCustomers}
            result={customersResult}
          />
        </div>

        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '6px', color: '#10b981' }}>🛒 Orders CSV</h2>
          <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '20px' }}>
            Required columns: order_id, customer_id, amount, order_date, category
          </p>
          <DropZone
            label="Drop orders.csv here"
            icon="🛒"
            onUpload={handleOrderUpload}
            accept=".csv"
            uploading={uploadingOrders}
            result={ordersResult}
          />
        </div>
      </div>

      {/* Generate Profiles */}
      <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
        <div style={{ fontSize: '36px', marginBottom: '12px' }}>🧠</div>
        <h2 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>Generate Customer Intelligence</h2>
        <p style={{ color: '#64748b', fontSize: '14px', marginBottom: '24px', maxWidth: '480px', margin: '0 auto 24px' }}>
          After uploading both files, generate customer profiles to compute segments, spending metrics, and purchase patterns.
        </p>
        <button
          className={bothUploaded ? 'btn-success' : 'btn-secondary'}
          onClick={handleGenerateProfiles}
          disabled={generatingProfs}
        >
          {generatingProfs ? '⏳ Generating profiles...' : '🔄 Generate Customer Profiles'}
        </button>
        {!bothUploaded && (
          <p style={{ fontSize: '12px', color: '#475569', marginTop: '12px' }}>
            Upload both CSV files first to enable this step
          </p>
        )}
      </div>

      {/* Instructions */}
      <div className="glass-card" style={{ padding: '24px', marginTop: '24px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '700', marginBottom: '12px', color: '#94a3b8' }}>📋 Upload Steps</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {[
            { step: '1', text: 'Upload customers.csv (1,000 customers with business segments)', done: !!customersResult },
            { step: '2', text: 'Upload orders.csv (9,000–12,000 orders)', done: !!ordersResult },
            { step: '3', text: 'Click "Generate Customer Profiles" to compute segments', done: false },
            { step: '4', text: 'Navigate to AI Planner to start building campaigns', done: false },
          ].map((item) => (
            <div key={item.step} style={{
              display: 'flex', alignItems: 'center', gap: '12px',
              padding: '10px 14px', borderRadius: '8px',
              background: item.done ? 'rgba(16,185,129,0.08)' : 'rgba(255,255,255,0.02)',
              border: `1px solid ${item.done ? 'rgba(16,185,129,0.2)' : 'rgba(255,255,255,0.04)'}`,
            }}>
              <span style={{
                width: '24px', height: '24px', borderRadius: '50%',
                background: item.done ? '#10b981' : 'rgba(255,255,255,0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '12px', fontWeight: '700', flexShrink: 0,
                color: item.done ? 'white' : '#64748b',
              }}>
                {item.done ? '✓' : item.step}
              </span>
              <span style={{ fontSize: '13px', color: item.done ? '#6ee7b7' : '#94a3b8' }}>{item.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
