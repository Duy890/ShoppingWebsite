import { useRef, useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/authService';
import { toast } from 'react-hot-toast';
import { User, Mail, KeyRound, Camera, ArrowLeft, CheckCircle, Loader2, Eye, EyeOff } from 'lucide-react';
import AvatarUploader from '../components/AvatarUploader';

const Field = ({ label, icon: Icon, children }) => (
  <div>
    <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
      {Icon && <Icon className="w-4 h-4 text-orange-500" />}
      {label}
    </label>
    {children}
  </div>
);

const inputCls =
  'w-full px-4 py-2.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition';

const SaveButton = ({ loading, children, disabled }) => (
  <button
    type="submit"
    disabled={loading || disabled}
    className="w-full bg-primary text-white py-2.5 rounded-md font-semibold hover:bg-orange-600 transition-colors shadow-sm active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
  >
    {loading && <Loader2 className="w-4 h-4 animate-spin" />}
    {children}
  </button>
);

const EditProfile = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { profile, user, updateProfile } = useAuth();
  const fileInputRef = useRef(null);

  const [avatarPreview, setAvatarPreview] = useState('');
  const [selectedAvatarFile, setSelectedAvatarFile] = useState(null);
  const [avatarLoading, setAvatarLoading] = useState(false);

  const [fullName, setFullName] = useState('');
  const [nameLoading, setNameLoading] = useState(false);

  const [newEmail, setNewEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const [pwForm, setPwForm] = useState({ current: '', next: '', confirm: '' });
  const [pwLoading, setPwLoading] = useState(false);
  const [showPw, setShowPw] = useState({ current: false, next: false, confirm: false });

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || '');
    }
  }, [profile]);

  useEffect(() => {
    if (searchParams.get('email_changed') === '1') {
      toast.success('Email updated successfully!');
    }
    if (searchParams.get('email_error') === '1') {
      toast.error('Email verification failed or link expired.');
    }
  }, []);

  const handleAvatarSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const handleAvatarSave = async () => {
    if (!selectedAvatarFile) return;
    setAvatarLoading(true);
    try {
      const result = await authService.uploadAvatar(selectedAvatarFile);
      await updateProfile({ full_name: profile?.full_name, avatar_url: result.avatar_url });
      setSelectedAvatarFile(null);
      setAvatarPreview('');
      toast.success('Avatar updated!');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update avatar.');
    } finally {
      setAvatarLoading(false);
    }
  };

  const handleNameSubmit = async (e) => {
    e.preventDefault();
    if (!fullName.trim()) { toast.error('Name cannot be empty.'); return; }
    setNameLoading(true);
    try {
      await updateProfile({ full_name: fullName.trim(), avatar_url: profile?.avatar_url });
      toast.success('Name updated!');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update name.');
    } finally {
      setNameLoading(false);
    }
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    if (!newEmail.trim() || newEmail === profile?.email) {
      toast.error('Please enter a different email address.');
      return;
    }
    setEmailLoading(true);
    try {
      await authService.requestEmailChange(newEmail.trim());
      setEmailSent(true);
      toast.success(`Verification link sent to ${newEmail}`);
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to send verification email.');
    } finally {
      setEmailLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (pwForm.next !== pwForm.confirm) { toast.error('New passwords do not match.'); return; }
    if (pwForm.next.length < 6) { toast.error('Password must be at least 6 characters.'); return; }
    setPwLoading(true);
    try {
      await authService.changePassword(pwForm.current, pwForm.next);
      toast.success('Password changed successfully!');
      setPwForm({ current: '', next: '', confirm: '' });
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to change password.');
    } finally {
      setPwLoading(false);
    }
  };

  const togglePw = (field) => setShowPw((v) => ({ ...v, [field]: !v[field] }));

  const PasswordInput = ({ field, label, value, onChange }) => (
    <Field label={label} icon={KeyRound}>
      <div className="relative">
        <input
          type={showPw[field] ? 'text' : 'password'}
          value={value}
          onChange={onChange}
          className={inputCls + ' pr-10'}
          placeholder="••••••••"
          required
        />
        <button
          type="button"
          onClick={() => togglePw(field)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          {showPw[field] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </div>
    </Field>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">

        <button
          onClick={() => navigate('/profile')}
          className="flex items-center gap-2 text-sm font-semibold text-primary hover:text-orange-600 transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Profile
        </button>

        <h1 className="text-3xl font-bold text-gray-900 mb-8">Edit Profile</h1>

        <div className="space-y-6">

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-5">
              <Camera className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-bold text-gray-900">Profile Photo</h2>
            </div>
            <div className="flex flex-col items-center gap-4">
              <AvatarUploader
                avatarUrl={profile?.avatar_url}
                previewUrl={avatarPreview}
                inputRef={fileInputRef}
                onClick={() => fileInputRef.current?.click()}
                onFileChange={handleAvatarSelect}
              />
              {selectedAvatarFile && (
                <button
                  type="button"
                  onClick={handleAvatarSave}
                  disabled={avatarLoading}
                  className="flex items-center gap-2 bg-primary text-white px-6 py-2 rounded-full text-sm font-semibold hover:bg-orange-600 transition disabled:opacity-60"
                >
                  {avatarLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                  {avatarLoading ? 'Saving...' : 'Save Photo'}
                </button>
              )}
              {!selectedAvatarFile && (
                <p className="text-xs text-gray-400">Click the photo to upload a new one</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-5">
              <User className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-bold text-gray-900">Display Name</h2>
            </div>
            <form onSubmit={handleNameSubmit} className="space-y-4">
              <Field label="Full Name" icon={null}>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className={inputCls}
                  placeholder="Your name"
                  required
                />
              </Field>
              <SaveButton loading={nameLoading}>
                {nameLoading ? 'Saving...' : 'Save Name'}
              </SaveButton>
            </form>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-5">
              <Mail className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-bold text-gray-900">Email Address</h2>
            </div>

            <div className="mb-4 rounded-md bg-gray-50 border border-gray-200 px-4 py-3 text-sm text-gray-600">
              Current email: <span className="font-semibold text-gray-900">{profile?.email}</span>
            </div>

            {emailSent ? (
              <div className="rounded-md border border-green-200 bg-green-50 px-4 py-4 text-sm text-green-700">
                <p className="font-semibold mb-1">✓ Verification email sent!</p>
                <p>Check your inbox at <strong>{newEmail}</strong> and click the link to confirm the change.</p>
                <button
                  onClick={() => { setEmailSent(false); setNewEmail(''); }}
                  className="mt-3 text-xs font-semibold text-green-700 underline"
                >
                  Send to a different address
                </button>
              </div>
            ) : (
              <form onSubmit={handleEmailSubmit} className="space-y-4">
                <Field label="New Email Address" icon={null}>
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    className={inputCls}
                    placeholder="new@example.com"
                    required
                  />
                </Field>
                <p className="text-xs text-gray-400">
                  A verification link will be sent to the new address. Your email will only
                  change after you click that link.
                </p>
                <SaveButton loading={emailLoading}>
                  {emailLoading ? 'Sending...' : 'Send Verification Link'}
                </SaveButton>
              </form>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-5">
              <KeyRound className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-bold text-gray-900">Change Password</h2>
            </div>
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <PasswordInput
                field="current"
                label="Current Password"
                value={pwForm.current}
                onChange={(e) => setPwForm({ ...pwForm, current: e.target.value })}
              />
              <PasswordInput
                field="next"
                label="New Password"
                value={pwForm.next}
                onChange={(e) => setPwForm({ ...pwForm, next: e.target.value })}
              />
              <PasswordInput
                field="confirm"
                label="Confirm New Password"
                value={pwForm.confirm}
                onChange={(e) => setPwForm({ ...pwForm, confirm: e.target.value })}
              />
              <SaveButton loading={pwLoading}>
                {pwLoading ? 'Saving...' : 'Change Password'}
              </SaveButton>
            </form>
          </div>

        </div>
      </div>
    </div>
  );
};

export default EditProfile;
