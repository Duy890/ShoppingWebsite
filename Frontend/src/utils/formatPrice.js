export const formatPrice = (price) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(price);
};

export const calculateTotal = (items) => {
  return items.reduce((total, item) => total + (item.price * item.quantity), 0);
};
