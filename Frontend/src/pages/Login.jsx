import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useTranslation } from 'react-i18next';
import AuthLayout from '../components/auth/AuthLayout';
import AuthCard from '../components/auth/AuthCard';
import AuthHeader from '../components/auth/AuthHeader';
import AuthInput from '../components/auth/AuthInput';
import AuthButton from '../components/auth/AuthButton';
import AuthFooter from '../components/auth/AuthFooter';

const Login = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { signIn } = useAuth();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setLoading(true);

    try {
      await signIn(formData.email, formData.password);
      navigate('/');
    } catch (error) {
      setErrorMessage(error?.message || 'Unable to sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title={t('login.title')}
      subtitle={t('login.subtitle')}
    >
      <AuthCard>
        <AuthHeader
          title={t('login.title')}
          description={t('login.subtitle')}
        />

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <AuthInput
            label={t('login.email')}
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="you@example.com"
            required
          />

          <AuthInput
            label={t('login.password')}
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="******"
            required
          />

          <div className="flex justify-end">
            <Link to="/forgot-password" className="text-sm font-semibold text-primary hover:text-orange-600 transition-colors">
              {t('login.forgot_password')}
            </Link>
          </div>

          {errorMessage && (
            <div className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {errorMessage}
            </div>
          )}

          <AuthButton type="submit" loading={loading}>
            {loading ? t('login.submitting') : t('login.submit')}
          </AuthButton>
        </form>

        <AuthFooter
          message={t('login.no_account')}
          linkText={t('login.sign_up')}
          linkTo="/signup"
        />
      </AuthCard>
    </AuthLayout>
  );
};

export default Login;
