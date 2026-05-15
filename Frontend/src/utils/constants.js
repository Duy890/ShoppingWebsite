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
};

export const PAYMENT_METHOD_LABELS = {
  credit_card: 'Credit Card',
  debit_card: 'Debit Card',
  paypal: 'PayPal',
  cash_on_delivery: 'Cash on Delivery',
};
