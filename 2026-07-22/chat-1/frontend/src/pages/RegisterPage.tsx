import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { register } from '../api/client';

const RegisterPage: React.FC = () => {
  const [form, setForm] = useState({
    email: '', password: '', name: '', age: '', sector: '', income_band: '',
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await register({
        email: form.email,
        password: form.password,
        name: form.name,
        age: form.age ? parseInt(form.age) : undefined,
        sector: form.sector || undefined,
        income_band: form.income_band || undefined,
      });
      navigate('/login');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Registration failed';
      setError(msg);
    }
  };

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm({ ...form, [field]: e.target.value });

  return (
    <div style={{ maxWidth: 480, margin: '60px auto', padding: 24 }}>
      <h1>Create Account</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 12 }}>
          <label>Name *</label>
          <input value={form.name} onChange={update('name')} required
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Email *</label>
          <input type="email" value={form.email} onChange={update('email')} required
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Password *</label>
          <input type="password" value={form.password} onChange={update('password')} required
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Age</label>
          <input type="number" value={form.age} onChange={update('age')}
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Sector</label>
          <select value={form.sector} onChange={update('sector')}
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}>
            <option value="">Select sector</option>
            <option value="technology">Technology</option>
            <option value="finance">Finance</option>
            <option value="healthcare">Healthcare</option>
            <option value="manufacturing">Manufacturing</option>
            <option value="logistics">Logistics</option>
            <option value="retail">Retail</option>
            <option value="education">Education</option>
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Income Band</label>
          <select value={form.income_band} onChange={update('income_band')}
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}>
            <option value="">Select income band</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <button type="submit" style={{ padding: '10px 24px' }}>Register</button>
      </form>
      <p style={{ marginTop: 16 }}>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
};

export default RegisterPage;
