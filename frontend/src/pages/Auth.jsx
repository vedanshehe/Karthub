import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, auth } from '../api.js';
import { Msg, useAct } from '../ui.jsx';

export function Login({ onAuth }) {
  const nav = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [msg, run, busy] = useAct();

  const handleLogin = (e) => {
    e.preventDefault();
    run(async () => {
      const r = await api('/auth/login', {
        method: 'POST',
        body: { email: email.trim(), password }
      });
      auth.set(r.user, r.token);
      onAuth(r.user);
      if (r.user.role === 'seller') nav('/seller');
      else if (r.user.role === 'admin') nav('/admin');
      else nav('/');
    }, 'Login successful!');
  };

  const quickFill = (roleEmail, rolePwd = 'secret1') => {
    setEmail(roleEmail);
    setPassword(rolePwd);
  };

  return (
    <div style={{ maxWidth: 440, margin: '40px auto' }}>
      <div className="card">
        <h2>Welcome to KartHub</h2>
        <p style={{ color: 'var(--text-muted)', marginTop: -8, marginBottom: 20 }}>
          Sign in to your account
        </p>

        <Msg m={msg} />

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 4 }}>
              Email address
            </label>
            <input
              type="email"
              required
              placeholder="e.g. cust1@karthub.dev"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 4 }}>
              Password
            </label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <button type="submit" disabled={busy} style={{ width: '100%', padding: '10px' }}>
            {busy ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--border-color)' }}>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>
            Quick fill demo accounts (password: <code>secret1</code>):
          </p>
          <div className="row" style={{ gap: 6 }}>
            <button type="button" className="btn-secondary btn-sm" onClick={() => quickFill('cust1@karthub.dev')}>
              Customer
            </button>
            <button type="button" className="btn-secondary btn-sm" onClick={() => quickFill('seller1@karthub.dev')}>
              Seller
            </button>
            <button type="button" className="btn-secondary btn-sm" onClick={() => quickFill('admin@karthub.dev')}>
              Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export function Register({ onAuth }) {
  const nav = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [isSeller, setIsSeller] = useState(false);
  const [storeName, setStoreName] = useState('');
  const [gstNo, setGstNo] = useState('');
  const [msg, run, busy] = useAct();

  const handleRegister = (e) => {
    e.preventDefault();

    // CH-06: General email syntax validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    if (!emailRegex.test(email.trim())) {
      alert('Please enter a valid email address (e.g. user@domain.com or user@dept.univ.edu).');
      return;
    }

    if (phone.trim() && !/^[0-9]{10}$/.test(phone.trim())) {
      alert('Phone number must be exactly 10 digits.');
      return;
    }

    if (isSeller) {
      const cleanGst = gstNo.trim().toUpperCase();
      if (cleanGst.length !== 15 || !/^[0-9A-Z]{15}$/.test(cleanGst)) {
        alert('GST number must be exactly 15 alphanumeric characters.');
        return;
      }
    }

    run(async () => {
      const body = {
        full_name: fullName.trim(),
        email: email.trim(),
        phone: phone.trim() || undefined,
        password,
        ...(isSeller ? { store_name: storeName.trim(), gst_no: gstNo.trim().toUpperCase() } : {})
      };

      const r = await api('/auth/register', { method: 'POST', body });
      auth.set(r.user, r.token);
      onAuth(r.user);
      if (r.user.role === 'seller') nav('/seller');
      else nav('/');
    }, 'Registration successful! Welcome to KartHub.');
  };

  return (
    <div style={{ maxWidth: 480, margin: '40px auto' }}>
      <div className="card">
        <h2>Create an Account</h2>
        <p style={{ color: 'var(--text-muted)', marginTop: -8, marginBottom: 20 }}>
          Join KartHub marketplace as a customer or seller
        </p>

        <Msg m={msg} />

        <form onSubmit={handleRegister}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 4 }}>
              Full name *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Aditi Sharma"
              value={fullName}
              onChange={e => setFullName(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 4 }}>
              Email address *
            </label>
            <input
              type="email"
              required
              placeholder="e.g. aditi@example.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 4 }}>
              Phone number (10 digits, optional)
            </label>
            <input
              type="text"
              placeholder="9876543210"
              maxLength={10}
              value={phone}
              onChange={e => setPhone(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: 18 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: 4 }}>
              Password (6+ characters) *
            </label>
            <input
              type="password"
              required
              minLength={6}
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <div style={{
            background: 'var(--bg-muted)',
            padding: '12px 14px',
            borderRadius: 'var(--radius-sm)',
            marginBottom: 18
          }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontWeight: 600 }}>
              <input
                type="checkbox"
                checked={isSeller}
                onChange={e => setIsSeller(e.target.checked)}
                style={{ width: 'auto', margin: 0 }}
              />
              Register as a multi-vendor Seller
            </label>

            {isSeller && (
              <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--border-color)' }}>
                <div style={{ marginBottom: 12 }}>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: 4 }}>
                    Store name *
                  </label>
                  <input
                    type="text"
                    required={isSeller}
                    placeholder="e.g. Apex Electronics"
                    value={storeName}
                    onChange={e => setStoreName(e.target.value)}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: 4 }}>
                    GST Number (15 alphanumeric characters) *
                  </label>
                  <input
                    type="text"
                    required={isSeller}
                    maxLength={15}
                    placeholder="29ABCDE1234F1Z5"
                    value={gstNo}
                    onChange={e => setGstNo(e.target.value.toUpperCase())}
                    style={{ textTransform: 'uppercase', fontFamily: 'monospace', letterSpacing: '0.05em' }}
                  />
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4, lineHeight: 1.4 }}>
                    Format: 15 alphanumeric characters (e.g. 29AAAAA0000A1Z5). For academic demonstration, any 15-character ID is accepted.
                  </div>
                </div>
              </div>
            )}
          </div>

          <button type="submit" disabled={busy} style={{ width: '100%', padding: '10px' }}>
            {busy ? 'Creating Account...' : isSeller ? 'Register as Seller' : 'Register as Customer'}
          </button>
        </form>
      </div>
    </div>
  );
}
