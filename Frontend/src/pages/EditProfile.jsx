import { useRef, useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useTranslation } from 'react-i18next';
import { authService } from '../services/authService';
import { toast } from 'react-hot-toast';
import { User, Mail, KeyRound, Camera, ArrowLeft, CheckCircle, Loader2, Eye, EyeOff, ShieldCheck, ShieldOff, Smartphone, X } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
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

const parseApiError = (err) => {
  if (!err?.response?.data) return err?.message || 'Đã xảy ra lỗi.';
  const detail = err.response.data.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || d.message).join('; ');
  }
  return err.response.data.message || 'Đã xảy ra lỗi.';
};

const EditProfile = () => {
  const { t } = useTranslation();
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

  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [mfaInitialized, setMfaInitialized] = useState(false);
  const [mfaSetupState, setMfaSetupState] = useState('idle');
  const [mfaSecret, setMfaSecret] = useState('');
  const [mfaQrUrl, setMfaQrUrl] = useState('');
  const [mfaConfirmCode, setMfaConfirmCode] = useState('');
  const [mfaSetupPassword, setMfaSetupPassword] = useState('');
  const [mfaLoading, setMfaLoading] = useState(false);
  const [mfaError, setMfaError] = useState('');
  const [mfaDisablePassword, setMfaDisablePassword] = useState('');
  const [mfaDisableCode, setMfaDisableCode] = useState('');
  const [showDisableModal, setShowDisableModal] = useState(false);

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || '');
    }
  }, [profile]);

  useEffect(() => {
    authService.getMFAStatus().then(({ mfa_enabled }) => {
      setMfaEnabled(mfa_enabled);
      setMfaInitialized(true);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (searchParams.get('email_changed') === '1') {
      toast.success(t('edit_profile.avatar_success'));
    }
    if (searchParams.get('email_error') === '1') {
      toast.error(t('edit_profile.email_error'));
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
      toast.success(t('edit_profile.avatar_success'));
    } catch (err) {
      toast.error(parseApiError(err));
    } finally {
      setAvatarLoading(false);
    }
  };

  const handleNameSubmit = async (e) => {
    e.preventDefault();
    if (!fullName.trim()) { toast.error(t('edit_profile.name_empty')); return; }
    setNameLoading(true);
    try {
      await updateProfile({ full_name: fullName.trim(), avatar_url: profile?.avatar_url });
      toast.success(t('edit_profile.name_success'));
    } catch (err) {
      toast.error(parseApiError(err));
    } finally {
      setNameLoading(false);
    }
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    if (!newEmail.trim() || newEmail === profile?.email) {
      toast.error(t('edit_profile.email_same'));
      return;
    }
    setEmailLoading(true);
    try {
      await authService.requestEmailChange(newEmail.trim());
      setEmailSent(true);
      toast.success(t('edit_profile.email_success'));
    } catch (err) {
      toast.error(parseApiError(err));
    } finally {
      setEmailLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (pwForm.next !== pwForm.confirm) { toast.error(t('edit_profile.passwords_mismatch')); return; }
    if (pwForm.next.length < 6) { toast.error(t('edit_profile.password_too_short')); return; }
    setPwLoading(true);
    try {
      await authService.changePassword(pwForm.current, pwForm.next);
      toast.success(t('edit_profile.password_success'));
      setPwForm({ current: '', next: '', confirm: '' });
    } catch (err) {
      toast.error(parseApiError(err));
    } finally {
      setPwLoading(false);
    }
  };

  const togglePw = (field) => setShowPw((v) => ({ ...v, [field]: !v[field] }));

  const handleSetupMFA = async () => {
    if (!mfaSetupPassword) return;
    setMfaLoading(true);
    setMfaError('');
    try {
      const { secret, qr_code_url } = await authService.setupMFA(mfaSetupPassword);
      setMfaSecret(secret);
      setMfaQrUrl(qr_code_url);
      setMfaSetupPassword('');
      setMfaSetupState('show_qr');
    } catch (err) {
      setMfaError(parseApiError(err));
    } finally {
      setMfaLoading(false);
    }
  };

  const handleActivateMFA = async () => {
    if (mfaConfirmCode.length !== 6) return;
    setMfaLoading(true);
    setMfaError('');
    try {
      await authService.verifyMFA(mfaConfirmCode);
      setMfaEnabled(true);
      setMfaSetupState('idle');
      setMfaSecret('');
      setMfaQrUrl('');
      setMfaConfirmCode('');
      setMfaSetupPassword('');
    } catch (err) {
      setMfaError(parseApiError(err));
      setMfaConfirmCode('');
    } finally {
      setMfaLoading(false);
    }
  };

  const handleDisableMFA = async () => {
    if (!mfaDisablePassword || mfaDisableCode.length !== 6) return;
    setMfaLoading(true);
    setMfaError('');
    try {
      await authService.disableMFA(mfaDisablePassword, mfaDisableCode);
      setMfaEnabled(false);
      setShowDisableModal(false);
      setMfaDisablePassword('');
      setMfaDisableCode('');
    } catch (err) {
      setMfaError(parseApiError(err));
    } finally {
      setMfaLoading(false);
    }
  };

  const handleStartSetup = () => {
    setMfaSetupState('password_prompt');
    setMfaSetupPassword('');
    setMfaError('');
  };

  const handleCancelSetup = () => {
    setMfaSetupState('idle');
    setMfaSetupPassword('');
    setMfaSecret('');
    setMfaQrUrl('');
    setMfaConfirmCode('');
    setMfaError('');
  };

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
          {t('edit_profile.back')}
        </button>

        <h1 className="text-3xl font-bold text-gray-900 mb-8">{t('edit_profile.title')}</h1>

        <div className="space-y-6">

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-5">
              <Camera className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-bold text-gray-900">{t('edit_profile.save_photo')}</h2>
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
                  {avatarLoading ? t('edit_profile.saving') : t('edit_profile.save_photo')}
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
              <h2 className="text-lg font-bold text-gray-900">{t('edit_profile.full_name')}</h2>
            </div>
            <form onSubmit={handleNameSubmit} className="space-y-4">
              <Field label={t('edit_profile.full_name')} icon={null}>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className={inputCls}
                  placeholder={t('edit_profile.your_name')}
                  required
                />
              </Field>
              <SaveButton loading={nameLoading}>
                {nameLoading ? t('edit_profile.saving') : t('edit_profile.save_name')}
              </SaveButton>
            </form>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-5">
              <Mail className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-bold text-gray-900">{t('edit_profile.email_section')}</h2>
            </div>

            <div className="mb-4 rounded-md bg-gray-50 border border-gray-200 px-4 py-3 text-sm text-gray-600">
              {t('edit_profile.current_email')}: <span className="font-semibold text-gray-900">{profile?.email}</span>
            </div>

            {emailSent ? (
              <div className="rounded-md border border-green-200 bg-green-50 px-4 py-4 text-sm text-green-700">
                <p className="font-semibold mb-1">✓ {t('edit_profile.email_success')}</p>
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
                <Field label={t('edit_profile.new_email')} icon={null}>
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
                  {emailLoading ? t('edit_profile.sending') : t('edit_profile.send_verification')}
                </SaveButton>
              </form>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <KeyRound className="w-5 h-5 text-orange-500" />
                <h2 className="text-lg font-bold text-gray-900">
                  {t('edit_profile.change_password')}
                </h2>
              </div>
              <Link
                to="/forgot-password"
                className="text-xs font-semibold text-primary hover:text-orange-600 hover:underline transition-colors"
              >
                {t('edit_profile.forgot_password_link')}
              </Link>
            </div>
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <PasswordInput
                field="current"
                label={t('edit_profile.current_password')}
                value={pwForm.current}
                onChange={(e) => setPwForm({ ...pwForm, current: e.target.value })}
              />
              <PasswordInput
                field="next"
                label={t('edit_profile.new_password')}
                value={pwForm.next}
                onChange={(e) => setPwForm({ ...pwForm, next: e.target.value })}
              />
              <PasswordInput
                field="confirm"
                label={t('edit_profile.confirm_password')}
                value={pwForm.confirm}
                onChange={(e) => setPwForm({ ...pwForm, confirm: e.target.value })}
              />
              <SaveButton loading={pwLoading}>
                {pwLoading ? t('edit_profile.saving') : t('edit_profile.change_password_btn')}
              </SaveButton>
            </form>
          </div>

          {/* MFA Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-5">
              <ShieldCheck className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-bold text-gray-900">
                Bảo mật &mdash; Xác thực hai lớp (MFA)
              </h2>
            </div>

            {!mfaInitialized ? (
              <div className="flex items-center justify-center py-6">
                <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
              </div>
            ) : mfaEnabled ? (
              /* State C: MFA already enabled */
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    Đã bật
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  Tài khoản đang được bảo vệ bởi xác thực hai lớp.
                </p>
                <button
                  type="button"
                  onClick={() => { setShowDisableModal(true); setMfaError(''); }}
                  className="flex items-center gap-2 rounded-full border border-rose-300 px-5 py-2 text-sm font-semibold text-rose-600 hover:bg-rose-50 transition-colors"
                >
                  <ShieldOff className="w-4 h-4" />
                  Tắt xác thực hai lớp
                </button>

                {showDisableModal && (
                  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
                    <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-gray-900">Tắt xác thực hai lớp</h3>
                        <button onClick={() => { setShowDisableModal(false); setMfaError(''); }} className="text-gray-400 hover:text-gray-600">
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-1">Mật khẩu hiện tại</label>
                          <input
                            type="password"
                            value={mfaDisablePassword}
                            onChange={(e) => setMfaDisablePassword(e.target.value)}
                            className={inputCls}
                            placeholder="Nhập mật khẩu"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-1">Mã xác thực 6 chữ số</label>
                          <input
                            type="text"
                            inputMode="numeric"
                            maxLength={6}
                            value={mfaDisableCode}
                            onChange={(e) => setMfaDisableCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                            className={inputCls + ' tracking-[0.3em] text-center'}
                            placeholder="000000"
                          />
                        </div>
                        {mfaError && (
                          <div className="rounded-md bg-rose-50 border border-rose-200 px-3 py-2 text-sm text-rose-600">
                            {mfaError}
                          </div>
                        )}
                        <div className="flex gap-3">
                          <button
                            type="button"
                            onClick={() => { setShowDisableModal(false); setMfaError(''); }}
                            className="flex-1 rounded-md border border-gray-300 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
                          >
                            Hủy
                          </button>
                          <button
                            type="button"
                            onClick={handleDisableMFA}
                            disabled={mfaLoading || !mfaDisablePassword || mfaDisableCode.length !== 6}
                            className="flex-1 rounded-md bg-rose-600 py-2.5 text-sm font-semibold text-white hover:bg-rose-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                          >
                            {mfaLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                            {mfaLoading ? 'Đang tắt...' : 'Xác nhận tắt'}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : mfaSetupState === 'password_prompt' ? (
              /* State A step 1: ask for password before setup */
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Vui lòng nhập mật khẩu hiện tại để bắt đầu thiết lập xác thực hai lớp.
                </p>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Mật khẩu hiện tại</label>
                  <input
                    type="password"
                    value={mfaSetupPassword}
                    onChange={(e) => setMfaSetupPassword(e.target.value)}
                    className={inputCls}
                    placeholder="Nhập mật khẩu"
                  />
                </div>
                {mfaError && (
                  <div className="rounded-md bg-rose-50 border border-rose-200 px-3 py-2 text-sm text-rose-600">
                    {mfaError}
                  </div>
                )}
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={handleCancelSetup}
                    className="flex-1 rounded-md border border-gray-300 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Hủy
                  </button>
                  <button
                    type="button"
                    onClick={handleSetupMFA}
                    disabled={mfaLoading || !mfaSetupPassword}
                    className="flex-1 rounded-md bg-primary py-2.5 text-sm font-semibold text-white hover:bg-orange-600 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {mfaLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                    {mfaLoading ? 'Đang xử lý...' : 'Tiếp tục'}
                  </button>
                </div>
              </div>
            ) : mfaSetupState === 'show_qr' ? (
              /* State B: show QR code + confirm code */
              <div className="space-y-6">
                <div className="space-y-3">
                  <p className="text-sm font-semibold text-gray-700">Bước 1: Quét mã QR</p>
                  <p className="text-xs text-gray-500">
                    Sử dụng Google Authenticator, Authy hoặc ứng dụng tương tự để quét mã QR bên dưới.
                  </p>
                  <div className="flex justify-center">
                    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                      {mfaQrUrl && <QRCodeSVG value={mfaQrUrl} size={200} />}
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-semibold text-gray-700">Hoặc nhập mã thủ công:</p>
                  <div className="rounded-md bg-gray-50 border border-gray-200 px-4 py-3">
                    <code className="text-sm font-mono text-gray-800 break-all select-all">
                      {mfaSecret}
                    </code>
                  </div>
                </div>

                <div className="space-y-3">
                  <p className="text-sm font-semibold text-gray-700">Bước 2: Xác nhận thiết lập</p>
                  <p className="text-xs text-gray-500">
                    Nhập mã 6 chữ số từ ứng dụng Authenticator để kích hoạt.
                  </p>
                  <input
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    value={mfaConfirmCode}
                    onChange={(e) => setMfaConfirmCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    className={inputCls + ' tracking-[0.3em] text-center'}
                    placeholder="000000"
                  />
                </div>

                {mfaError && (
                  <div className="rounded-md bg-rose-50 border border-rose-200 px-3 py-2 text-sm text-rose-600">
                    {mfaError}
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={handleCancelSetup}
                    className="flex-1 rounded-md border border-gray-300 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Hủy
                  </button>
                  <button
                    type="button"
                    onClick={handleActivateMFA}
                    disabled={mfaLoading || mfaConfirmCode.length !== 6}
                    className="flex-1 rounded-md bg-primary py-2.5 text-sm font-semibold text-white hover:bg-orange-600 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {mfaLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                    {mfaLoading ? 'Đang kích hoạt...' : 'Kích hoạt MFA'}
                  </button>
                </div>
              </div>
            ) : (
              /* State A: MFA not enabled */
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
                    <ShieldOff className="w-3.5 h-3.5" />
                    Chưa bật
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  Bảo vệ tài khoản bằng mã xác thực từ ứng dụng Google Authenticator hoặc tương tự.
                </p>
                <button
                  type="button"
                  onClick={handleStartSetup}
                  className="flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-white hover:bg-orange-600 transition-colors shadow-sm"
                >
                  <Smartphone className="w-4 h-4" />
                  Bật xác thực hai lớp
                </button>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
};

export default EditProfile;
