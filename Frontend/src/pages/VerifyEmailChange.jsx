import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

const VerifyEmailChange = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setStatus('error');
      setMessage('Token không hợp lệ hoặc đã hết hạn.');
      return;
    }
    authService.verifyEmailChange(token)
      .then(() => {
        setStatus('success');
        setMessage('Email đã được xác nhận thành công!');
        setTimeout(() => navigate('/profile'), 3000);
      })
      .catch((err) => {
        setStatus('error');
        setMessage(err?.response?.data?.detail || 'Xác nhận thất bại. Token có thể đã hết hạn.');
      });
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-4 max-w-md">
        {status === 'loading' && <p>Đang xác nhận email...</p>}
        {status === 'success' && (
          <>
            <p className="text-green-600 font-semibold">{message}</p>
            <p className="text-sm text-gray-500">Đang chuyển hướng về trang Profile...</p>
          </>
        )}
        {status === 'error' && (
          <>
            <p className="text-red-600 font-semibold">{message}</p>
            <button onClick={() => navigate('/profile')} className="text-primary underline">
              Về trang Profile
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default VerifyEmailChange;
