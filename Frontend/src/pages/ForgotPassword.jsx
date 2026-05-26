import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import AuthLayout from '../components/auth/AuthLayout';
import AuthCard from '../components/auth/AuthCard';
import AuthHeader from '../components/auth/AuthHeader';
import AuthInput from '../components/auth/AuthInput';
import AuthButton from '../components/auth/AuthButton';
import { authService } from '../services/authService';

const ForgotPassword = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authService.forgotPassword(email);
      setSuccess(true);
    } catch (err) {
      setError(err?.message || t('forgot_password.error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title={t('forgot_password.title')} subtitle={t('forgot_password.subtitle')}>
      <AuthCard>
        <AuthHeader title={t('forgot_password.title')} description={t('forgot_password.subtitle')} />
        {success ? (
          <div className="mt-8 space-y-4 text-center">
            <div className="rounded-3xl border border-green-200 bg-green-50 px-4 py-4 text-sm text-green-700">
              ✓ {t('forgot_password.success')}
            </div>
            <Link to="/login" className="block text-sm font-semibold text-primary hover:text-orange-600 transition-colors">
              ← {t('forgot_password.back_to_login')}
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            <AuthInput label={t('forgot_password.email')} name="email" type="email" value={email}
              onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
            {error && <div className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}
            <AuthButton type="submit" loading={loading}>{loading ? t('forgot_password.submitting') : t('forgot_password.submit')}</AuthButton>
            <p className="text-center text-sm text-slate-500">
              {t('register.have_account')}{' '}
              <Link to="/login" className="font-semibold text-primary hover:text-orange-600 transition-colors">{t('register.sign_in')}</Link>
            </p>
          </form>
        )}
      </AuthCard>
    </AuthLayout>
  );
};

export default ForgotPassword;
