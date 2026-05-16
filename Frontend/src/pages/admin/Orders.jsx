import { useEffect, useState } from 'react';
import { orderService } from '../../services/orderService';
import { formatPrice } from '../../utils/formatPrice';
import { ORDER_STATUS, ORDER_STATUS_LABELS } from '../../utils/constants';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const data = await orderService.getAllOrders();
      setOrders(data);
    } catch (error) {
      console.error('Error loading orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (orderId, newStatus, note = null) => {
    try {
      await orderService.updateOrderStatus(orderId, newStatus, note);
      await loadOrders();
      alert('Order status updated successfully!');
    } catch (error) {
      alert(error.message);
    }
  };

  const handleSimulateNext = async (orderId) => {
    try {
      await orderService.simulateNextOrderStatus(orderId);
      await loadOrders();
      alert('Order status simulated successfully!');
    } catch (error) {
      alert(error.message);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-black text-gray-900 mb-8 tracking-tight">Orders</h1>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {orders.length > 0 ? (
          <table className="min-w-full divide-y divide-gray-100">
            <thead className="bg-gray-50/50">
              <tr>
                <th className="px-6 py-4 text-left text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  Order ID
                </th>
                <th className="px-6 py-4 text-left text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  Customer
                </th>
                <th className="px-6 py-4 text-left text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  Date
                </th>
                <th className="px-6 py-4 text-left text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  Total
                </th>
                <th className="px-6 py-4 text-left text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-[10px] font-black text-gray-400 uppercase tracking-widest">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-50">
              {orders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-xs font-mono font-bold text-primary bg-primary/5 px-2 py-1 rounded">
                      #{order.id.slice(0, 8)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-gray-900">
                        {order.user?.full_name || 'N/A'}
                      </span>
                      <span className="text-[11px] font-medium text-gray-400">{order.user?.email}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-600">
                    {new Date(order.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-black text-gray-900">
                      {formatPrice(order.total_amount)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`inline-flex px-3 py-1 text-[10px] font-black uppercase tracking-tight rounded-full ${
                        order.status === 'delivered'
                          ? 'bg-green-100 text-green-700'
                          : order.status === 'cancelled'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-primary/10 text-primary'
                      }`}
                    >
                      {ORDER_STATUS_LABELS[order.status]}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <select
                        value={order.status}
                        onChange={(e) => handleStatusChange(order.id, e.target.value)}
                        className="text-xs font-bold border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all cursor-pointer bg-gray-50"
                      >
                        {Object.values(ORDER_STATUS).map((status) => (
                          <option key={status} value={status}>
                            {ORDER_STATUS_LABELS[status]}
                          </option>
                        ))}
                      </select>
                      <button
                        onClick={() => handleSimulateNext(order.id)}
                        className="text-xs font-bold bg-primary text-white px-3 py-1.5 rounded-lg hover:bg-orange-600 transition-colors"
                        title="Simulate next status"
                      >
                        Next
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-20">
            <p className="text-gray-400 font-medium">No orders found.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Orders;
