import { useState } from 'react';
import { Link } from 'react-router-dom';
import AuthLayout from '../components/auth/AuthLayout';
import AuthCard from '../components/auth/AuthCard';
import AuthHeader from '../components/auth/AuthHeader';
import AuthInput from '../components/auth/AuthInput';
import AuthButton from '../components/auth/AuthButton';
import { authService } from '../services/authService';

const ForgotPassword = () => {
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
      setError(err?.message || 'Unable to send reset email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Forgot password?" subtitle="Enter your email and we'll send you a reset link.">
      <AuthCard>
        <AuthHeader title="Reset password" description="We'll send a secure link to your email address." />
        {success ? (
          <div className="mt-8 space-y-4 text-center">
            <div className="rounded-3xl border border-green-200 bg-green-50 px-4 py-4 text-sm text-green-700">
              ✓ Reset link sent! Check your inbox.
            </div>
            <Link to="/login" className="block text-sm font-semibold text-primary hover:text-orange-600 transition-colors">
              ← Back to Sign in
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            <AuthInput label="Email" name="email" type="email" value={email}
              onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
            {error && <div className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}
            <AuthButton type="submit" loading={loading}>{loading ? 'Sending...' : 'Send Reset Link'}</AuthButton>
            <p className="text-center text-sm text-slate-500">
              Remember your password?{' '}
              <Link to="/login" className="font-semibold text-primary hover:text-orange-600 transition-colors">Sign in</Link>
            </p>
          </form>
        )}
      </AuthCard>
    </AuthLayout>
  );
};

export default ForgotPassword;
