import { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import AuthLayout from '../components/auth/AuthLayout';
import AuthCard from '../components/auth/AuthCard';
import AuthHeader from '../components/auth/AuthHeader';
import AuthInput from '../components/auth/AuthInput';
import AuthButton from '../components/auth/AuthButton';
import { authService } from '../services/authService';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  const [form, setForm] = useState({ password: '', confirm: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) { setError('Passwords do not match.'); return; }
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return; }
    setError(''); setLoading(true);
    try {
      await authService.resetPassword(token, form.password);
      navigate('/login?reset=success');
    } catch (err) {
      setError(err?.message || 'Reset failed. The link may have expired.');
    } finally { setLoading(false); }
  };

  if (!token) return (
    <AuthLayout title="Invalid link">
      <AuthCard>
        <p className="text-center text-sm text-slate-500 mt-4">
          This reset link is invalid or expired.{' '}
          <Link to="/forgot-password" className="font-semibold text-primary hover:text-orange-600">Request a new one</Link>
        </p>
      </AuthCard>
    </AuthLayout>
  );

  return (
    <AuthLayout title="Set new password" subtitle="Choose a strong password for your account.">
      <AuthCard>
        <AuthHeader title="New password" description="Enter and confirm your new password." />
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <AuthInput label="New Password" name="password" type="password"
            value={form.password} onChange={(e) => setForm({...form, password: e.target.value})}
            placeholder="••••••••" required />
          <AuthInput label="Confirm Password" name="confirm" type="password"
            value={form.confirm} onChange={(e) => setForm({...form, confirm: e.target.value})}
            placeholder="••••••••" required />
          {error && <div className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}
          <AuthButton type="submit" loading={loading}>{loading ? 'Saving...' : 'Set New Password'}</AuthButton>
        </form>
      </AuthCard>
    </AuthLayout>
  );
};

export default ResetPassword;
