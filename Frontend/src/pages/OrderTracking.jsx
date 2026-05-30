import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-hot-toast';
import { orderService } from '../services/orderService';
import { formatPrice } from '../utils/formatPrice';
import { SHIPPING_METHOD_LABELS } from '../utils/constants';
import {
  Package,
  Truck,
  CheckCircle,
  Clock,
  MapPin,
  CreditCard,
  ArrowLeft,
  Loader,
  AlertCircle,
} from 'lucide-react';

const STATUS_CONFIG = (t) => ({
  pending: { label: t('order_tracking.status_pending'), color: 'text-yellow-600', bg: 'bg-yellow-50', icon: Clock },
  confirmed: { label: t('order_tracking.status_confirmed'), color: 'text-blue-600', bg: 'bg-blue-50', icon: CheckCircle },
  processing: { label: t('order_tracking.status_processing'), color: 'text-purple-600', bg: 'bg-purple-50', icon: Package },
  shipped: { label: t('order_tracking.status_shipped'), color: 'text-indigo-600', bg: 'bg-indigo-50', icon: Truck },
  out_for_delivery: { label: t('order_tracking.status_out_for_delivery'), color: 'text-orange-600', bg: 'bg-orange-50', icon: Truck },
  delivered: { label: t('order_tracking.status_delivered'), color: 'text-green-600', bg: 'bg-green-50', icon: CheckCircle },
  cancelled: { label: t('order_tracking.status_cancelled'), color: 'text-red-600', bg: 'bg-red-50', icon: AlertCircle },
  payment_failed: { label: t('order_tracking.status_payment_failed'), color: 'text-red-600', bg: 'bg-red-50', icon: AlertCircle },
  return_requested: { label: t('order_tracking.status_return_requested'), color: 'text-gray-600', bg: 'bg-gray-50', icon: Package },
  returned: { label: t('order_tracking.status_returned'), color: 'text-gray-600', bg: 'bg-gray-50', icon: Package },
  refunded: { label: t('order_tracking.status_refunded'), color: 'text-green-600', bg: 'bg-green-50', icon: CheckCircle },
});

const statusOrder = [
  'pending',
  'confirmed',
  'processing',
  'shipped',
  'out_for_delivery',
  'delivered',
  'return_requested',
  'returned',
  'refunded',
];

const OrderTracking = () => {
  const { t } = useTranslation();
  const statusConfig = STATUS_CONFIG(t);
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    loadOrderTracking();
  }, [orderId]);

  const loadOrderTracking = async () => {
    try {
      setLoading(true);
      const [orderData, timelineData] = await Promise.all([
        orderService.getOrderById(orderId),
        orderService.getOrderTimeline(orderId),
      ]);
      console.log('ORDER RESPONSE', orderData);
      setOrder(orderData);
      setTimeline(timelineData.history || []);
    } catch (err) {
      setError(err.message || t('order_tracking.not_found'));
      toast.error(t('order_tracking.not_found'));
    } finally {
      setLoading(false);
    }
  };

  const handleCancelOrder = async () => {
    try {
      setCancelling(true);
      await orderService.cancelOrder(orderId);
      toast.success('Đơn hàng đã được huỷ thành công.');
      setShowCancelModal(false);
      await loadOrderTracking();
    } catch (err) {
      toast.error(err.message || 'Huỷ đơn hàng thất bại.');
    } finally {
      setCancelling(false);
    }
  };

  const getCurrentStatusIndex = (status) => {
    return statusOrder.indexOf(status);
  };

  const isStatusCompleted = (status, currentStatus) => {
    return getCurrentStatusIndex(status) <= getCurrentStatusIndex(currentStatus);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-gray-600">Loading order tracking...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Tracking</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link
            to="/profile"
            className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-full hover:bg-orange-600 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            {t('order_tracking.back_to_orders')}
          </Link>
        </div>
      </div>
    );
  }

  const currentStatusIndex = getCurrentStatusIndex(order.status);
  const statusInfo = statusConfig[order.status] || { label: order.status, color: 'text-gray-600', bg: 'bg-gray-50', icon: Package };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/profile"
            className="inline-flex items-center text-primary hover:text-orange-600 mb-4"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            {t('order_tracking.back_to_orders')}
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">{t('order_tracking.title')}</h1>
          <p className="text-gray-600 mt-2">{t('order_tracking.order_id')} #{order.id}</p>

          {order.status === 'pending' && (
            <button
              onClick={() => setShowCancelModal(true)}
              className="mt-4 inline-flex items-center gap-2 px-5 py-2.5 rounded-full border-2 border-red-400 text-red-600 font-semibold text-sm hover:bg-red-50 transition-colors"
            >
              <AlertCircle className="h-4 w-4" />
              Huỷ đơn hàng
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Status Progress */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">{t('order_tracking.status')}</h2>
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusInfo.bg} ${statusInfo.color}`}>
                  <statusInfo.icon className="h-4 w-4 mr-2" />
                  {statusInfo.label}
                </div>
              </div>

              {/* Progress Bar */}
              <div className="relative mb-8">
                <div className="flex items-center justify-between">
                  {statusOrder.slice(0, 6).map((status, index) => {
                    const isCompleted = isStatusCompleted(status, order.status);
                    const isCurrent = status === order.status;
                    const config = statusConfig[status] || { label: status, icon: Package };
                    const Icon = config.icon;

                    return (
                      <div key={status} className="flex flex-col items-center flex-1">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-2 ${
                          isCompleted ? 'bg-primary text-white' : isCurrent ? 'bg-primary/20 text-primary border-2 border-primary' : 'bg-gray-100 text-gray-400'
                        }`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <span className={`text-xs font-medium text-center ${
                          isCompleted || isCurrent ? 'text-gray-900' : 'text-gray-400'
                        }`}>
                          {config.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
                <div className="absolute top-5 left-5 right-5 h-0.5 bg-gray-200 -z-10">
                  <div
                    className="h-full bg-primary transition-all duration-500"
                    style={{ width: `${(currentStatusIndex / 5) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">{t('order_tracking.title')}</h2>
              <div className="space-y-6">
                {timeline.map((event, index) => {
                  const config = statusConfig[event.new_status] || { label: event.new_status, color: 'text-gray-600', bg: 'bg-gray-50', icon: Package };
                  const Icon = config.icon;
                  return (
                    <div key={event.id} className="flex items-start space-x-4">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${config.bg}`}>
                        <Icon className={`h-5 w-5 ${config.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-medium text-gray-900">
                            {config.label}
                          </h3>
                          <time className="text-sm text-gray-500">
                            {new Date(event.created_at).toLocaleString()}
                          </time>
                        </div>
                        {event.note && (
                          <p className="text-sm text-gray-600 mt-1">{event.note}</p>
                        )}
                        {event.old_status && (
                          <p className="text-xs text-gray-500 mt-1">
                            Changed from {(statusConfig[event.old_status] || { label: event.old_status }).label}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Order Details Sidebar */}
          <div className="space-y-6">
            {/* Shipping Info */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('profile.addresses')}</h3>
              <div className="space-y-3">
                {order.shipping_method && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Shipping Method</label>
                    <p className="text-sm text-gray-900 font-semibold">
                      {SHIPPING_METHOD_LABELS[order.shipping_method] || order.shipping_method}
                    </p>
                  </div>
                )}
                {order.estimated_delivery_days !== null && order.estimated_delivery_days !== undefined && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">{t('order_tracking.estimated_delivery')}</label>
                    <p className="text-sm text-gray-900">
                      {order.estimated_delivery_days === 0
                        ? t('order_tracking.same_day')
                        : order.estimated_delivery_days === 1
                        ? '1 business day'
                        : `${order.estimated_delivery_days} business days`}
                    </p>
                  </div>
                )}
                {order.tracking_code && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">{t('order_tracking.tracking_code')}</label>
                    <p className="text-sm text-gray-900 font-mono">{order.tracking_code}</p>
                  </div>
                )}
                {order.shipping_provider && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Shipping Provider</label>
                    <p className="text-sm text-gray-900">{order.shipping_provider}</p>
                  </div>
                )}
                {order.estimated_delivery && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">{t('order_tracking.estimated_delivery')}</label>
                    <p className="text-sm text-gray-900">
                      {new Date(order.estimated_delivery).toLocaleDateString()}
                    </p>
                  </div>
                )}
                {order.delivered_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Delivered At</label>
                    <p className="text-sm text-gray-900">
                      {new Date(order.delivered_at).toLocaleString()}
                    </p>
                  </div>
                )}
                {order.order_note && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Order Note</label>
                    <p className="text-sm text-gray-900 italic">{order.order_note}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Payment Info */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Information</h3>
              <div className="space-y-3">
                <div className="flex items-center">
                  <CreditCard className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {order.payment_method || 'Cash on Delivery'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Order Summary */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Summary</h3>
              <div className="text-2xl font-bold text-gray-900 mb-2">
                {formatPrice(Number(order?.total_amount || 0))}
              </div>
              <p className="text-sm text-gray-600">
                {(order?.items || []).reduce((sum, item) => sum + Number(item?.quantity || 0), 0)} {t('order_tracking.items')}
              </p>
              {(order?.items || []).length > 0 && (
                <div className="mt-4 space-y-2 border-t border-gray-100 pt-4">
                  {(order?.items || []).map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <span className="text-gray-600">
                        {item.product?.name || 'Product'} × {item.quantity}
                      </span>
                      <span className="font-medium">
                        {formatPrice(Number(item?.price || 0) * Number(item?.quantity || 0))}
                      </span>
                    </div>
                  ))}
                  {Number(order?.shipping_fee || 0) > 0 && (
                    <div className="flex justify-between text-sm pt-2 border-t border-gray-50">
                      <span className="text-gray-600">Shipping</span>
                      <span className="font-medium">
                        {formatPrice(Number(order?.shipping_fee || 0))}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {showCancelModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 animate-fade-in">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-full bg-yellow-50 flex items-center justify-center">
                <AlertCircle className="h-9 w-9 text-yellow-500" />
              </div>
            </div>

            <h3 className="text-xl font-bold text-gray-900 text-center mb-2">
              Xác nhận huỷ đơn hàng
            </h3>

            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-5">
              <p className="text-sm text-yellow-800 text-center leading-relaxed">
                ⚠️ Bạn có chắc chắn muốn <strong>huỷ đơn hàng #{orderId}</strong> không?
                <br />
                Hành động này <strong>không thể hoàn tác</strong>.
                Đơn hàng sẽ bị huỷ và bạn sẽ không thể khôi phục lại.
              </p>
            </div>

            <div className="bg-gray-50 rounded-xl p-3 mb-6 text-sm text-gray-700">
              <div className="flex justify-between">
                <span>Tổng tiền:</span>
                <span className="font-bold">{formatPrice(Number(order?.total_amount || 0))}</span>
              </div>
              <div className="flex justify-between mt-1">
                <span>Trạng thái hiện tại:</span>
                <span className="text-yellow-600 font-semibold">Chờ xác nhận</span>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowCancelModal(false)}
                disabled={cancelling}
                className="flex-1 py-3 rounded-full border-2 border-gray-200 text-gray-700 font-semibold hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Không, giữ lại
              </button>
              <button
                onClick={handleCancelOrder}
                disabled={cancelling}
                className="flex-1 py-3 rounded-full bg-red-500 text-white font-semibold hover:bg-red-600 transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
              >
                {cancelling ? (
                  <>
                    <Loader className="h-4 w-4 animate-spin" />
                    Đang huỷ...
                  </>
                ) : (
                  'Xác nhận huỷ'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderTracking;