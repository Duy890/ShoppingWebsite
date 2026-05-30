import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useTranslation } from 'react-i18next';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import AuthLayout from '../components/auth/AuthLayout';
import AuthCard from '../components/auth/AuthCard';
import AuthHeader from '../components/auth/AuthHeader';
import AuthInput from '../components/auth/AuthInput';
import AuthButton from '../components/auth/AuthButton';
import AuthFooter from '../components/auth/AuthFooter';

const MFA_CHALLENGE_TIMEOUT = 5 * 60 * 1000;

const Login = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { signIn, verifyMFAChallenge } = useAuth();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [step, setStep] = useState('credentials');
  const [mfaChallengeToken, setMfaChallengeToken] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const mfaTimerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (mfaTimerRef.current) clearTimeout(mfaTimerRef.current);
    };
  }, []);

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
      const result = await signIn(formData.email, formData.password);
      if (result.mfa_required) {
        setMfaChallengeToken(result.mfa_challenge_token);
        setStep('mfa');
        mfaTimerRef.current = setTimeout(() => {
          setErrorMessage('Phiên xác thực hết hạn, vui lòng đăng nhập lại.');
          setStep('credentials');
          setMfaCode('');
          setMfaChallengeToken('');
        }, MFA_CHALLENGE_TIMEOUT);
      } else {
        navigate('/');
      }
    } catch (error) {
      setErrorMessage(error?.response?.data?.detail || error?.message || 'Unable to sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleMfaCodeChange = (e) => {
    const val = e.target.value.replace(/\D/g, '').slice(0, 6);
    setMfaCode(val);
  };

  const handleMFASubmit = async (e) => {
    e.preventDefault();
    if (mfaCode.length !== 6) return;
    setErrorMessage('');
    setLoading(true);

    try {
      await verifyMFAChallenge(mfaChallengeToken, mfaCode);
      if (mfaTimerRef.current) clearTimeout(mfaTimerRef.current);
      navigate('/');
    } catch (error) {
      setErrorMessage(error?.response?.data?.detail || 'Mã xác thực không hợp lệ.');
      setMfaCode('');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToCredentials = () => {
    if (mfaTimerRef.current) clearTimeout(mfaTimerRef.current);
    setStep('credentials');
    setMfaCode('');
    setMfaChallengeToken('');
    setErrorMessage('');
  };

  if (step === 'mfa') {
    return (
      <AuthLayout
        title="Xác thực hai lớp"
        subtitle="Nhập mã 6 chữ số từ ứng dụng Authenticator của bạn"
      >
        <AuthCard>
          <div className="space-y-6 text-center">
            <div className="mx-auto inline-flex h-14 w-14 items-center justify-center rounded-3xl bg-primary/10 text-primary">
              <ShieldAlert className="h-7 w-7" />
            </div>
            <div>
              <h2 className="text-2xl font-black tracking-tight text-slate-950 dark:text-slate-100">
                Xác thực hai lớp
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">
                Nhập mã 6 chữ số từ ứng dụng Authenticator của bạn
              </p>
            </div>
          </div>

          <form onSubmit={handleMFASubmit} className="mt-8 space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-200 text-center">
                Mã xác thực
              </label>
              <input
                type="text"
                inputMode="numeric"
                maxLength={6}
                pattern="[0-9]*"
                autoComplete="one-time-code"
                value={mfaCode}
                onChange={handleMfaCodeChange}
                autoFocus
                className="mx-auto block w-48 text-center text-2xl tracking-[0.5em] rounded-2xl border border-slate-200 px-4 py-4 text-slate-900 shadow-sm transition duration-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                placeholder="000000"
              />
            </div>

            {errorMessage && (
              <div className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {errorMessage}
              </div>
            )}

            <AuthButton type="submit" loading={loading} disabled={mfaCode.length !== 6}>
              {loading ? 'Đang xác thực...' : 'Xác nhận'}
            </AuthButton>

            <button
              type="button"
              onClick={handleBackToCredentials}
              className="flex items-center justify-center gap-2 mx-auto text-sm font-semibold text-slate-500 hover:text-primary transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Quay lại đăng nhập
            </button>
          </form>
        </AuthCard>
      </AuthLayout>
    );
  }

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
