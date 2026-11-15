import { useState, useEffect, useCallback } from 'react';
import { api } from './api.js';

export function useLoad(path) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');

  const reload = useCallback(() => {
    setLoading(true);
    api(path)
      .then(d => {
        setData(d);
        setErr('');
      })
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false));
  }, [path]);

  useEffect(reload, [reload]);
  return { data, loading, err, reload };
}

export function useAct() {
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);

  const run = async (f, okText = 'Action completed successfully') => {
    setBusy(true);
    try {
      const r = await f();
      setMsg({ ok: okText });
      return r;
    } catch (e) {
      setMsg({ err: e.message });
      throw e;
    } finally {
      setBusy(false);
    }
  };

  const clearMsg = () => setMsg(null);
  return [msg, run, busy, clearMsg];
}

export function Msg({ m, onClose }) {
  if (!m) return null;
  const isErr = Boolean(m.err);
  return (
    <div className={`alert ${isErr ? 'alert-error' : 'alert-success'}`}>
      <span>{isErr ? '⚠️ ' : '✅ '}</span>
      <span style={{ flex: 1 }}>{m.err || m.ok}</span>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer', padding: 0 }}
        >
          ✕
        </button>
      )}
    </div>
  );
}

export function Money({ amount }) {
  const n = Number(amount);
  if (isNaN(n)) return <span>-</span>;
  return <span>₹{n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>;
}

export function FormattedDate({ date }) {
  if (!date) return <span>-</span>;
  const d = new Date(date);
  return <span>{d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>;
}

export function Badge({ status, type }) {
  const s = String(status || '').toUpperCase();
  let badgeClass = 'badge-neutral';

  if (type === 'verified') {
    badgeClass = status ? 'badge-success' : 'badge-neutral';
    return <span className={`badge ${badgeClass}`}>{status ? '✓ Verified' : 'Unverified'}</span>;
  }

  if (['PAID', 'DELIVERED', 'SUCCESS', 'ACTIVE'].includes(s)) badgeClass = 'badge-success';
  else if (['SHIPPED', 'PLACED', 'PENDING'].includes(s)) badgeClass = 'badge-info';
  else if (['CANCELLED', 'FAILED', 'RETURNED'].includes(s)) badgeClass = 'badge-danger';
  else if (['REFUNDED'].includes(s)) badgeClass = 'badge-warning';

  return <span className={`badge ${badgeClass}`}>{status}</span>;
}

export function RatingStars({ rating, count }) {
  const r = Number(rating) || 0;
  const full = Math.floor(r);
  const stars = '★'.repeat(full) + '☆'.repeat(5 - full);
  return (
    <span className="rating-stars">
      <span className="stars-glow">{stars}</span>
      <span style={{ fontWeight: 700, color: 'var(--text-main)', marginLeft: 6 }}>
        {r > 0 ? r.toFixed(1) : 'New'}
      </span>
      {count != null && <span className="rating-count">({count})</span>}
    </span>
  );
}

export function StarRatingSelector({ value, onChange, max = 5 }) {
  const [hover, setHover] = useState(0);
  const labels = ['', 'Poor', 'Fair', 'Average', 'Good', 'Excellent'];
  return (
    <div className="star-rating-selector" role="radiogroup" aria-label="Rating selector">
      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
        {Array.from({ length: max }, (_, i) => i + 1).map((star) => (
          <button
            key={star}
            type="button"
            role="radio"
            aria-checked={value === star}
            aria-label={`${star} star${star > 1 ? 's' : ''}`}
            className={`star-picker-btn ${star <= (hover || value) ? 'active' : ''}`}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(0)}
            onClick={() => onChange(star)}
          >
            ★
          </button>
        ))}
        <span className="star-picker-label">
          {labels[hover || value] || `${value || 0} / ${max}`}
        </span>
      </div>
    </div>
  );
}

export function QuantityStepper({ value, min = 1, max, onChange, disabled }) {
  const val = Math.max(min, Number(value) || min);
  return (
    <div className="qty-stepper">
      <button
        type="button"
        className="qty-btn"
        disabled={disabled || val <= min}
        onClick={() => onChange(val - 1)}
        aria-label="Decrease quantity"
      >
        −
      </button>
      <span className="qty-value">{val}</span>
      <button
        type="button"
        className="qty-btn"
        disabled={disabled || (max != null && val >= max)}
        onClick={() => onChange(val + 1)}
        aria-label="Increase quantity"
      >
        +
      </button>
    </div>
  );
}

export function Modal({ isOpen, title, onClose, children, footer }) {
  useEffect(() => {
    if (!isOpen) return;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;
  return (
    <div className="modal-backdrop" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3 id="modal-title">{title}</h3>
          <button className="modal-close" onClick={onClose} aria-label="Close modal">✕</button>
        </div>
        <div className="modal-body">
          {children}
        </div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}

export function Table({ rows, render, emptyText = 'No records found' }) {
  if (!rows || rows.length === 0) {
    return (
      <div className="empty-state">
        <p>{emptyText}</p>
      </div>
    );
  }

  const keys = Object.keys(rows[0]);

  return (
    <div className="table-responsive">
      <table>
        <thead>
          <tr>
            {keys.map(k => (
              <th key={k}>{k.replace(/_/g, ' ')}</th>
            ))}
            {render && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {keys.map(k => (
                <td key={k}>
                  {k.includes('price') || k.includes('revenue') || k.includes('gross') || k.includes('payable') || k === 'amount'
                    ? <Money amount={r[k]} />
                    : k.includes('_at') || k === 'joined_on'
                    ? <FormattedDate date={r[k]} />
                    : typeof r[k] === 'boolean'
                    ? <Badge status={r[k]} type={k === 'is_verified' ? 'verified' : undefined} />
                    : k.includes('status')
                    ? <Badge status={r[k]} />
                    : String(r[k] ?? '-')}
                </td>
              ))}
              {render && <td>{render(r)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function OrderProgressStepper({ status, items }) {
  const isCancelled = status === 'CANCELLED';
  const steps = [
    { key: 'PLACED', label: 'Order Placed', desc: 'Received & verified' },
    { key: 'SHIPPED', label: 'Dispatched', desc: 'With logistics courier' },
    { key: 'DELIVERED', label: 'Delivered', desc: 'Handed over to buyer' }
  ];

  let currentIdx = 0;
  if (status === 'PAID' || status === 'PLACED') currentIdx = 0;
  else if (status === 'SHIPPED') currentIdx = 1;
  else if (status === 'DELIVERED') currentIdx = 2;

  // If any item is shipped or delivered, reflect progressive status
  if (items && items.length > 0 && !isCancelled) {
    const allDelivered = items.every(it => it.item_status === 'DELIVERED');
    const anyShipped = items.some(it => it.item_status === 'SHIPPED' || it.item_status === 'DELIVERED');
    if (allDelivered) currentIdx = 2;
    else if (anyShipped) currentIdx = 1;
  }

  if (isCancelled) {
    return (
      <div className="order-stepper-box cancelled">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: '1.4rem' }}>🛑</span>
          <div>
            <div style={{ fontWeight: 700, color: 'var(--danger)' }}>Order Cancelled</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              All order items have been cancelled and inventory quantities restored to sellers.
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="order-stepper-box">
      <div className="stepper-track">
        {steps.map((st, i) => {
          const isDone = i < currentIdx;
          const isCurrent = i === currentIdx;
          return (
            <div key={st.key} className={`stepper-step ${isDone ? 'done' : isCurrent ? 'current' : 'pending'}`}>
              <div className="stepper-circle">
                {isDone ? '✓' : i + 1}
              </div>
              <div className="stepper-text">
                <div className="stepper-title">{st.label}</div>
                <div className="stepper-desc">{st.desc}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function SimulatedPaymentModal({ isOpen, orderId, amount, method, onSuccess, onFailure, onClose }) {
  const [chosenMethod, setChosenMethod] = useState(method || 'UPI');
  const [busy, setBusy] = useState(false);
  const [simState, setSimState] = useState(null); // 'PROCESSING' | 'SUCCESS' | 'FAILED'

  useEffect(() => {
    if (isOpen) {
      setChosenMethod(method || 'UPI');
      setSimState(null);
      setBusy(false);
    }
  }, [isOpen, method]);

  if (!isOpen) return null;

  const handleSimulate = async (simulateSuccess) => {
    setBusy(true);
    setSimState('PROCESSING');
    try {
      await new Promise(r => setTimeout(r, 600));
      const res = await api(`/orders/${orderId}/pay`, {
        method: 'POST',
        body: {
          method: chosenMethod,
          simulate_status: simulateSuccess ? 'SUCCESS' : 'FAILED'
        }
      });
      if (simulateSuccess) {
        setSimState('SUCCESS');
        setTimeout(() => {
          if (onSuccess) onSuccess(res);
        }, 1200);
      } else {
        setSimState('FAILED');
        if (onFailure) onFailure(res);
      }
    } catch (err) {
      setSimState('FAILED');
      alert(err.message || 'Payment simulation failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal isOpen={isOpen} title="KartHub Simulated Payment Gateway" onClose={busy ? () => {} : onClose}>
      <div style={{ padding: '4px 0' }}>
        <div style={{
          background: 'var(--info-bg)',
          border: '1px solid var(--info-border)',
          borderRadius: 'var(--radius-sm)',
          padding: '10px 14px',
          marginBottom: 16,
          display: 'flex',
          gap: 10,
          alignItems: 'center'
        }}>
          <span style={{ fontSize: '1.3rem' }}>🧪</span>
          <div style={{ fontSize: '0.84rem', color: 'var(--info)', lineHeight: 1.4 }}>
            <strong>Sandbox Simulation Environment:</strong> No real bank account, UPI PIN, or credit card is charged. Choose an outcome below to test order lifecycle states.
          </div>
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'var(--bg-muted)',
          padding: '12px 16px',
          borderRadius: 'var(--radius-sm)',
          marginBottom: 18
        }}>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
              Order Reference
            </div>
            <div style={{ fontWeight: 800, fontSize: '1.05rem', color: 'var(--text-main)' }}>
              #{orderId}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
              Payable Amount
            </div>
            <div style={{ fontWeight: 800, fontSize: '1.25rem', color: 'var(--primary)' }}>
              <Money amount={amount} />
            </div>
          </div>
        </div>

        {simState !== 'SUCCESS' && (
          <div style={{ marginBottom: 18 }}>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8 }}>
              PAYMENT METHOD SIMULATED
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
              {[
                { id: 'UPI', label: 'UPI / VPA', icon: '📱' },
                { id: 'CARD', label: 'Credit / Debit', icon: '💳' },
                { id: 'NETBANKING', label: 'Net Banking', icon: '🏦' }
              ].map(m => (
                <button
                  key={m.id}
                  type="button"
                  className={`btn-secondary btn-sm ${chosenMethod === m.id ? 'active' : ''}`}
                  style={{
                    padding: '8px 10px',
                    borderColor: chosenMethod === m.id ? 'var(--accent)' : 'var(--border-color)',
                    background: chosenMethod === m.id ? 'var(--primary-light)' : '#fff',
                    fontWeight: 600
                  }}
                  onClick={() => setChosenMethod(m.id)}
                  disabled={busy}
                >
                  {m.icon} {m.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {simState === null && (
          <div style={{
            border: '1px dashed var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            padding: '14px',
            marginBottom: 20,
            background: '#ffffff'
          }}>
            {chosenMethod === 'UPI' && (
              <div>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4 }}>
                  Virtual Payment Address (VPA) / UPI ID
                </div>
                <input
                  type="text"
                  readOnly
                  value="karthub.customer@okaxis"
                  style={{ background: '#f8fafc', color: 'var(--text-muted)', fontFamily: 'monospace' }}
                />
                <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: 4 }}>
                  ⚡ Mock instant UPI verification enabled.
                </div>
              </div>
            )}

            {chosenMethod === 'CARD' && (
              <div>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4 }}>
                  Mock Test Card Number
                </div>
                <input
                  type="text"
                  readOnly
                  value="4111 •••• •••• 1111 (Visa Sandbox)"
                  style={{ background: '#f8fafc', color: 'var(--text-muted)', fontFamily: 'monospace', marginBottom: 8 }}
                />
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  <input type="text" readOnly value="12/28" style={{ background: '#f8fafc', color: 'var(--text-muted)' }} />
                  <input type="password" readOnly value="•••" style={{ background: '#f8fafc', color: 'var(--text-muted)' }} />
                </div>
              </div>
            )}

            {chosenMethod === 'NETBANKING' && (
              <div>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4 }}>
                  Select Simulated Bank Portal
                </div>
                <select style={{ margin: 0 }}>
                  <option>HDFC Bank (Sandbox Gateway)</option>
                  <option>State Bank of India (Sandbox Gateway)</option>
                  <option>ICICI Bank (Sandbox Gateway)</option>
                  <option>Axis Bank (Sandbox Gateway)</option>
                </select>
              </div>
            )}
          </div>
        )}

        {simState === 'PROCESSING' && (
          <div style={{ textAlign: 'center', padding: '24px 0' }}>
            <div style={{ fontSize: '2rem', marginBottom: 8 }}>⏳</div>
            <div style={{ fontWeight: 700 }}>Processing simulated payment transaction...</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Contacting mock payment gateway host...
            </div>
          </div>
        )}

        {simState === 'SUCCESS' && (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <div style={{ fontSize: '2.4rem', color: 'var(--success)', marginBottom: 6 }}>✓</div>
            <h4 style={{ color: 'var(--success)', margin: '0 0 6px' }}>Simulated Payment Successful!</h4>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: 0 }}>
              Order status updated to PAID. Redirecting to your order confirmation...
            </p>
          </div>
        )}

        {simState === 'FAILED' && (
          <div style={{
            background: 'var(--danger-bg)',
            border: '1px solid var(--danger-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '12px 14px',
            marginBottom: 16
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--danger)', fontWeight: 700 }}>
              <span>✕</span> Simulated Payment Failed / Declined
            </div>
            <div style={{ fontSize: '0.84rem', color: 'var(--danger)', marginTop: 4 }}>
              The simulated gateway declined the transaction. The order remains recorded with payment status <strong>FAILED</strong>. You can retry with a different method or retry now.
            </div>
          </div>
        )}

        {simState !== 'SUCCESS' && (
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 14 }}>
            <button
              type="button"
              className="btn-secondary"
              disabled={busy}
              onClick={onClose}
            >
              {simState === 'FAILED' ? 'Close & View Order' : 'Cancel'}
            </button>
            <button
              type="button"
              className="btn-outline-danger"
              disabled={busy}
              onClick={() => handleSimulate(false)}
            >
              Simulate Failure ✕
            </button>
            <button
              type="button"
              className="btn-primary"
              disabled={busy}
              onClick={() => handleSimulate(true)}
            >
              {busy ? 'Simulating...' : 'Simulate Success ✓'}
            </button>
          </div>
        )}
      </div>
    </Modal>
  );
}
