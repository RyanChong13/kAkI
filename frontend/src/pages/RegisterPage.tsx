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
    <div className="page-shell">
      <div className="auth-card" style={{ maxWidth: 480 }}>
        <span className="eyebrow">Get started</span>
        <h1>Create account</h1>
        {error && <p className="error-text">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name *</label>
            <input value={form.name} onChange={update('name')} required />
          </div>
          <div className="form-group">
            <label>Email *</label>
            <input type="email" value={form.email} onChange={update('email')} required />
          </div>
          <div className="form-group">
            <label>Password *</label>
            <input type="password" value={form.password} onChange={update('password')} required />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Age</label>
              <input type="number" value={form.age} onChange={update('age')} />
            </div>
            <div className="form-group">
              <label>Income band</label>
              <select value={form.income_band} onChange={update('income_band')}>
                <option value="">Select income band</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Sector</label>
            <select value={form.sector} onChange={update('sector')}>
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
          <button type="submit" className="btn btn-primary btn-block">
            Register
          </button>
        </form>
        <p style={{ marginTop: 20, marginBottom: 0 }}>
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
