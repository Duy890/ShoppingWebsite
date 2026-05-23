import { useEffect, useState } from 'react';
import { Package, ShoppingCart, Coins, Users } from 'lucide-react';
import { adminService } from '../../services/adminService';
import { formatPrice } from '../../utils/formatPrice';

const formatCurrency = (value) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(value);

const formatShortAmount = (value, yearly = false) => {
  if (yearly && value >= 1000000000) return `${(value / 1000000000).toFixed(1)}B`;
  if (value >= 1000000) return `${(value / 1000000).toFixed(0)}M`;
  return `${(value / 1000).toFixed(0)}K`;
};

const RevenueBarChart = ({ data }) => {
  const maxRevenue = Math.max(...data.map((item) => item.revenue), 1);

  return (
    <div className="h-80">
      <div className="flex h-64 items-end gap-2 border-l border-b border-gray-100 px-3 pt-6">
        {data.map((item) => {
          const height = Math.max((item.revenue / maxRevenue) * 220, item.revenue > 0 ? 6 : 0);
          return (
            <div key={item.month} className="flex flex-1 flex-col items-center justify-end gap-2">
              <div className="relative group flex w-full items-end justify-center h-56">
                <div
                  className="w-full max-w-9 rounded-t bg-orange-500 transition-colors group-hover:bg-orange-600"
                  style={{ height }}
                />
                <div className="pointer-events-none absolute bottom-full mb-2 hidden rounded-lg bg-gray-900 px-2 py-1 text-[10px] font-bold text-white group-hover:block">
                  {formatCurrency(item.revenue)}
                </div>
              </div>
              <span className="text-[10px] font-semibold text-gray-500">{item.month}</span>
            </div>
          );
        })}
      </div>
      <div className="mt-4 flex items-center justify-between text-xs text-gray-400">
        <span>0</span>
        <span>Max: {formatShortAmount(maxRevenue)}</span>
      </div>
    </div>
  );
};

const RevenueLineChart = ({ data }) => {
  const width = 720;
  const height = 260;
  const padding = 36;
  const maxRevenue = Math.max(...data.map((item) => item.revenue), 1);
  const points = data.map((item, index) => {
    const x = padding + (index * (width - padding * 2)) / Math.max(data.length - 1, 1);
    const y = height - padding - (item.revenue / maxRevenue) * (height - padding * 2);
    return { ...item, x, y };
  });
  const path = points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ');

  return (
    <div className="h-80 overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="min-w-[560px] w-full h-72">
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#e5e7eb" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#e5e7eb" />
        {[0.25, 0.5, 0.75, 1].map((tick) => (
          <line
            key={tick}
            x1={padding}
            y1={height - padding - tick * (height - padding * 2)}
            x2={width - padding}
            y2={height - padding - tick * (height - padding * 2)}
            stroke="#f3f4f6"
            strokeDasharray="4 4"
          />
        ))}
        <path d={path} fill="none" stroke="#f97316" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        {points.map((point) => (
          <g key={point.year}>
            <circle cx={point.x} cy={point.y} r="6" fill="#f97316" />
            <text x={point.x} y={height - 10} textAnchor="middle" className="fill-gray-500 text-xs font-semibold">
              {point.year}
            </text>
            <text x={point.x} y={point.y - 12} textAnchor="middle" className="fill-gray-500 text-[10px] font-semibold">
              {formatShortAmount(point.revenue, true)}
            </text>
          </g>
        ))}
      </svg>
      <div className="mt-1 flex items-center gap-2 text-xs font-semibold text-gray-500">
        <span className="h-3 w-3 rounded-full bg-orange-500" />
        Revenue
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    totalUsers: 0,
  });
  const [loading, setLoading] = useState(true);
  const [revenueByMonth, setRevenueByMonth] = useState([]);
  const [revenueByYear, setRevenueByYear] = useState([]);
  const [chartLoading, setChartLoading] = useState(true);
  const [activeChart, setActiveChart] = useState('month');
  const [topSearches, setTopSearches] = useState([]);
  const [topViewed, setTopViewed] = useState([]);
  const [abandonment, setAbandonment] = useState([]);

  useEffect(() => {
    loadStats();
    loadCharts();
    loadAnalytics();
  }, []);

  const loadStats = async () => {
    try {
      const stats = await adminService.getStats();
      setStats(stats);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      const [searches, viewed, abandon] = await Promise.all([
        adminService.getTopSearches(),
        adminService.getTopViewed(),
        adminService.getCartAbandonment(),
      ]);
      setTopSearches(searches);
      setTopViewed(viewed);
      setAbandonment(abandon);
    } catch (error) {
      console.error('Analytics load error:', error);
    }
  };

  const loadCharts = async () => {
    try {
      const [monthly, yearly] = await Promise.all([
        adminService.getRevenueByMonth(),
        adminService.getRevenueByYear(),
      ]);
      setRevenueByMonth(monthly);
      setRevenueByYear(yearly);
    } catch (error) {
      console.error('Chart load error:', error);
    } finally {
      setChartLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Products',
      value: stats.totalProducts,
      icon: Package,
      color: 'bg-blue-500',
    },
    {
      title: 'Total Orders',
      value: stats.totalOrders,
      icon: ShoppingCart,
      color: 'bg-green-500',
    },
    {
      title: 'Total Revenue',
      value: formatPrice(stats.totalRevenue),
      icon: Coins,
      color: 'bg-yellow-500',
    },
    {
      title: 'Total Users',
      value: stats.totalUsers,
      icon: Users,
      color: 'bg-purple-500',
    },
  ];

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {statCards.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
            <h3 className="text-gray-600 text-sm font-medium mb-1">{stat.title}</h3>
            <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-2xl shadow-md p-8 mt-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Revenue Overview</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveChart('month')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                activeChart === 'month'
                  ? 'bg-orange-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              By Month
            </button>
            <button
              onClick={() => setActiveChart('year')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                activeChart === 'year'
                  ? 'bg-orange-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              By Year
            </button>
          </div>
        </div>

        {chartLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-orange-500" />
          </div>
        ) : activeChart === 'month' ? (
          <RevenueBarChart data={revenueByMonth} />
        ) : (
          <RevenueLineChart data={revenueByYear} />
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-bold text-gray-800 mb-4">Top Searches</h3>
          <div className="space-y-2">
            {topSearches.slice(0, 8).map((s, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-gray-700">{s.query}</span>
                <span className="text-gray-400 font-mono">{s.count}</span>
              </div>
            ))}
            {topSearches.length === 0 && (
              <p className="text-sm text-gray-400">No data yet</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-bold text-gray-800 mb-4">Most Viewed Products</h3>
          <div className="space-y-2">
            {topViewed.slice(0, 8).map((p, i) => (
              <div key={p.id} className="flex justify-between text-sm">
                <span className="text-gray-700 truncate max-w-[160px]">{p.name}</span>
                <span className="text-gray-400 font-mono">{p.view_count} views</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-bold text-gray-800 mb-4">Cart Abandonment</h3>
          <div className="space-y-2">
            {abandonment.slice(0, 8).map((p, i) => (
              <div key={p.id} className="flex justify-between text-sm">
                <span className="text-gray-700 truncate max-w-[140px]">{p.name}</span>
                <span className={`font-mono text-xs px-2 py-0.5 rounded-full ${
                  p.abandonment_rate > 70
                    ? 'bg-red-100 text-red-700'
                    : p.abandonment_rate > 40
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-green-100 text-green-700'
                }`}>
                  {p.abandonment_rate}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
