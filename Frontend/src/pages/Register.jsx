import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useTranslation } from 'react-i18next';
import AuthLayout from '../components/auth/AuthLayout';
import AuthCard from '../components/auth/AuthCard';
import AuthHeader from '../components/auth/AuthHeader';
import AuthInput from '../components/auth/AuthInput';
import AuthButton from '../components/auth/AuthButton';
import AuthFooter from '../components/auth/AuthFooter';

const Register = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { signUp } = useAuth();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
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

    if (formData.password !== formData.confirmPassword) {
      setErrorMessage(t('register.password_mismatch'));
      return;
    }

    setLoading(true);

    try {
      await signUp(formData.email, formData.password, formData.fullName);
      navigate('/login');
    } catch (error) {
      setErrorMessage(error?.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title={t('register.title')}
      subtitle={t('register.subtitle')}
    >
      <AuthCard>
        <AuthHeader
          title={t('register.title')}
          description={t('register.subtitle')}
        />

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <AuthInput
            label={t('register.full_name')}
            name="fullName"
            type="text"
            value={formData.fullName}
            onChange={handleChange}
            placeholder="John Doe"
            required
          />

          <AuthInput
            label={t('register.email')}
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="you@example.com"
            required
          />

          <AuthInput
            label={t('register.password')}
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="••••••••"
            minLength={6}
            required
          />

          <AuthInput
            label={t('register.confirm_password')}
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="••••••••"
            minLength={6}
            required
          />

          {errorMessage && (
            <div className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {errorMessage}
            </div>
          )}

          <AuthButton type="submit" loading={loading}>
            {loading ? t('register.submitting') : t('register.submit')}
          </AuthButton>
        </form>

        <AuthFooter
          message={t('register.have_account')}
          linkText={t('register.sign_in')}
          linkTo="/login"
        />
      </AuthCard>
    </AuthLayout>
  );
};

export default Register;
