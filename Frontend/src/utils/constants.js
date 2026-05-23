export const ORDER_STATUS = {
  PENDING: 'pending',
  CONFIRMED: 'confirmed',
  PROCESSING: 'processing',
  SHIPPED: 'shipped',
  OUT_FOR_DELIVERY: 'out_for_delivery',
  DELIVERED: 'delivered',
  CANCELLED: 'cancelled',
  PAYMENT_FAILED: 'payment_failed',
  RETURN_REQUESTED: 'return_requested',
  RETURNED: 'returned',
  REFUNDED: 'refunded',
};

export const ORDER_STATUS_LABELS = {
  pending: 'Pending',
  confirmed: 'Confirmed',
  processing: 'Processing',
  shipped: 'Shipped',
  out_for_delivery: 'Out for Delivery',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
  payment_failed: 'Payment Failed',
  return_requested: 'Return Requested',
  returned: 'Returned',
  refunded: 'Refunded',
};

export const PAYMENT_METHODS = {
  CREDIT_CARD: 'credit_card',
  DEBIT_CARD: 'debit_card',
  PAYPAL: 'paypal',
  CASH_ON_DELIVERY: 'cash_on_delivery',
  MOMO: 'momo',
};

export const PAYMENT_METHOD_LABELS = {
  credit_card: 'Credit Card',
  debit_card: 'Debit Card',
  paypal: 'PayPal',
  cash_on_delivery: 'Cash on Delivery',
  momo: 'Ví MoMo',
};

export const SHIPPING_METHODS = {
  STANDARD: 'standard',
  EXPRESS: 'express',
  SAME_DAY: 'same_day',
};

export const SHIPPING_METHOD_CONFIG = {
  standard: {
    code: 'standard',
    name: 'Standard Delivery',
    description: '2-5 business days',
    estimated_days: 3,
    shipping_fee: 15000,
  },
  express: {
    code: 'express',
    name: 'Express Delivery',
    description: '1-2 business days',
    estimated_days: 1,
    shipping_fee: 35000,
  },
  same_day: {
    code: 'same_day',
    name: 'Same Day Delivery',
    description: 'Delivered today',
    estimated_days: 0,
    shipping_fee: 75000,
  },
};

export const SHIPPING_METHOD_LABELS = {
  standard: 'Standard Delivery',
  express: 'Express Delivery',
  same_day: 'Same Day Delivery',
};
