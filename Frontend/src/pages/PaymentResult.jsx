import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

const PaymentResult = () => {
  const { t, i18n } = useTranslation();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    const resultCode = searchParams.get('resultCode');
    if (resultCode === '0') {
      setStatus('success');
    } else if (resultCode !== null) {
      setStatus('failed');
    } else {
      setStatus('unknown');
    }
  }, [searchParams]);

  const orderId = searchParams.get('orderId') || '';
  const message = searchParams.get('message') || '';
  const amount = searchParams.get('amount');

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }

  const formattedAmount = amount
    ? new Intl.NumberFormat(i18n.language === 'vi' ? 'vi-VN' : 'en-US', {
        style: 'currency',
        currency: 'VND',
        maximumFractionDigits: 0,
      }).format(Number(amount))
    : null;

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-10 max-w-md w-full text-center">
        {status === 'success' ? (
          <>
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h1 className="text-2xl font-black text-gray-900 mb-2">{t('payment_result.success_title')}</h1>
            <p className="text-gray-500 text-sm mb-2">
              {t('payment_result.order_confirmed', { order: orderId.slice(0, 8) })}
            </p>
            {formattedAmount && (
              <p className="text-lg font-black text-primary mb-6">
                {formattedAmount}
              </p>
            )}
          </>
        ) : (
          <>
            <XCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
            <h1 className="text-2xl font-black text-gray-900 mb-2">{t('payment_result.failed_title')}</h1>
            <p className="text-gray-500 text-sm mb-6">
              {message || t('payment_result.failed_message')}
            </p>
          </>
        )}

        <div className="flex flex-col gap-3">
          <Link
            to="/profile"
            className="w-full bg-primary text-white py-3 rounded-2xl font-bold hover:bg-orange-600 transition-colors text-sm"
          >
            {t('payment_result.view_orders')}
          </Link>
          <Link
            to="/"
            className="w-full bg-gray-100 text-gray-700 py-3 rounded-2xl font-bold hover:bg-gray-200 transition-colors text-sm"
          >
            {t('payment_result.back_home')}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PaymentResult;
