import { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import AuthLayout from '../components/auth/AuthLayout';
import AuthCard from '../components/auth/AuthCard';
import AuthHeader from '../components/auth/AuthHeader';
import AuthInput from '../components/auth/AuthInput';
import AuthButton from '../components/auth/AuthButton';
import { authService } from '../services/authService';

const ResetPassword = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  const [form, setForm] = useState({ password: '', confirm: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) { setError(t('register.password_mismatch')); return; }
    if (form.password.length < 6) { setError(t('edit_profile.password_too_short')); return; }
    setError(''); setLoading(true);
    try {
      await authService.resetPassword(token, form.password);
      navigate('/login?reset=success');
    } catch (err) {
      setError(err?.message || t('forgot_password.error'));
    } finally { setLoading(false); }
  };

  if (!token) return (
    <AuthLayout title={t('forgot_password.error')}>
      <AuthCard>
        <p className="text-center text-sm text-slate-500 mt-4">
          {t('forgot_password.error')}{' '}
          <Link to="/forgot-password" className="font-semibold text-primary hover:text-orange-600">{t('forgot_password.title')}</Link>
        </p>
      </AuthCard>
    </AuthLayout>
  );

  return (
    <AuthLayout title={t('edit_profile.change_password')} subtitle={t('forgot_password.subtitle')}>
      <AuthCard>
        <AuthHeader title={t('edit_profile.change_password')} description={t('edit_profile.confirm_password')} />
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <AuthInput label={t('edit_profile.new_password')} name="password" type="password"
            value={form.password} onChange={(e) => setForm({...form, password: e.target.value})}
            placeholder="••••••••" required />
          <AuthInput label={t('edit_profile.confirm_password')} name="confirm" type="password"
            value={form.confirm} onChange={(e) => setForm({...form, confirm: e.target.value})}
            placeholder="••••••••" required />
          {error && <div className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}
          <AuthButton type="submit" loading={loading}>{loading ? t('edit_profile.saving') : t('edit_profile.change_password')}</AuthButton>
        </form>
      </AuthCard>
    </AuthLayout>
  );
};

export default ResetPassword;
