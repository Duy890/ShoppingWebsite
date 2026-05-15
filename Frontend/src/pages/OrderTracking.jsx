import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { orderService } from '../services/orderService';
import { formatPrice } from '../utils/formatPrice';
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

const statusConfig = {
  pending: { label: 'Pending', color: 'text-yellow-600', bg: 'bg-yellow-50', icon: Clock },
  confirmed: { label: 'Confirmed', color: 'text-blue-600', bg: 'bg-blue-50', icon: CheckCircle },
  processing: { label: 'Processing', color: 'text-purple-600', bg: 'bg-purple-50', icon: Package },
  shipped: { label: 'Shipped', color: 'text-indigo-600', bg: 'bg-indigo-50', icon: Truck },
  out_for_delivery: { label: 'Out for Delivery', color: 'text-orange-600', bg: 'bg-orange-50', icon: Truck },
  delivered: { label: 'Delivered', color: 'text-green-600', bg: 'bg-green-50', icon: CheckCircle },
  cancelled: { label: 'Cancelled', color: 'text-red-600', bg: 'bg-red-50', icon: AlertCircle },
  payment_failed: { label: 'Payment Failed', color: 'text-red-600', bg: 'bg-red-50', icon: AlertCircle },
  return_requested: { label: 'Return Requested', color: 'text-gray-600', bg: 'bg-gray-50', icon: Package },
  returned: { label: 'Returned', color: 'text-gray-600', bg: 'bg-gray-50', icon: Package },
  refunded: { label: 'Refunded', color: 'text-green-600', bg: 'bg-green-50', icon: CheckCircle },
};

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
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadOrderTracking();
  }, [orderId]);

  const loadOrderTracking = async () => {
    try {
      setLoading(true);
      const [orderData, timelineData] = await Promise.all([
        orderService.getOrderTracking(orderId),
        orderService.getOrderTimeline(orderId),
      ]);
      setOrder(orderData);
      setTimeline(timelineData.history);
    } catch (err) {
      setError(err.message || 'Failed to load order tracking');
      toast.error('Failed to load order tracking');
    } finally {
      setLoading(false);
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
            Back to Orders
          </Link>
        </div>
      </div>
    );
  }

  const currentStatusIndex = getCurrentStatusIndex(order.status);
  const statusInfo = statusConfig[order.status];

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
            Back to Orders
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Order Tracking</h1>
          <p className="text-gray-600 mt-2">Order #{order.order_id}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Status Progress */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Order Status</h2>
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
                    const config = statusConfig[status];
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
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Order Timeline</h2>
              <div className="space-y-6">
                {timeline.map((event, index) => {
                  const config = statusConfig[event.new_status];
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
                            Changed from {statusConfig[event.old_status].label}
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
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Shipping Information</h3>
              <div className="space-y-3">
                {order.tracking_code && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Tracking Code</label>
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
                    <label className="text-sm font-medium text-gray-500">Estimated Delivery</label>
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
                {formatPrice(order.total_amount)}
              </div>
              <p className="text-sm text-gray-600">
                {order.items?.length || 0} item{order.items?.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderTracking;