import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Brain, BarChart3, Settings, RefreshCw, Bell } from 'lucide-react';

// Mock data structures and API simulation
interface MarketData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high24h: number;
  low24h: number;
  timestamp: string;
  history: { date: string; price: number; volume: number }[];
}

interface Alert {
  id: string;
  message: string;
  type: 'warning' | 'info' | 'success' | 'error';
  timestamp: string;
}

interface AIInsight {
  summary: string;
  recommendations: string[];
  volatilityAnalysis: string;
  trendDirection: 'bullish' | 'bearish' | 'neutral';
}

const MarketMirror: React.FC = () => {
  const [marketType, setMarketType] = useState<'stocks' | 'crypto' | 'ecommerce'>('crypto');
  const [selectedItems, setSelectedItems] = useState<string[]>(['BTC', 'ETH', 'SOL']);
  const [timeRange, setTimeRange] = useState<string>('7d');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [aiInsights, setAiInsights] = useState<AIInsight | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [alertThreshold, setAlertThreshold] = useState<number>(8);

  // Mock API data generator
  const generateMockData = (symbol: string, type: string): MarketData => {
    const basePrice = type === 'crypto' ? 
      (symbol === 'BTC' ? 65000 : symbol === 'ETH' ? 3200 : 180) :
      type === 'stocks' ?
      (symbol === 'AAPL' ? 190 : symbol === 'GOOGL' ? 140 : 350) :
      (Math.random() * 100 + 50);

    const change = (Math.random() - 0.5) * basePrice * 0.1;
    const changePercent = (change / basePrice) * 100;

    // Generate historical data
    const history = [];
    let currentPrice = basePrice;
    const days = timeRange === '1d' ? 24 : timeRange === '7d' ? 7 : timeRange === '1m' ? 30 : 90;
    
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const volatility = (Math.random() - 0.5) * 0.05;
      currentPrice *= (1 + volatility);
      history.push({
        date: date.toISOString().split('T')[0],
        price: currentPrice,
        volume: Math.random() * 1000000 + 100000
      });
    }

    return {
      symbol,
      name: symbol,
      price: basePrice + change,
      change,
      changePercent,
      volume: Math.random() * 1000000 + 100000,
      high24h: basePrice * 1.05,
      low24h: basePrice * 0.95,
      timestamp: new Date().toISOString(),
      history
    };
  };

  // AI Analysis simulation
  const generateAIInsights = (data: MarketData[]): AIInsight => {
    const avgChange = data.reduce((sum, item) => sum + item.changePercent, 0) / data.length;
    const volatility = data.reduce((sum, item) => sum + Math.abs(item.changePercent), 0) / data.length;
    
    const trendDirection = avgChange > 2 ? 'bullish' : avgChange < -2 ? 'bearish' : 'neutral';
    
    const summary = `Market analysis for ${data.length} assets over ${timeRange}. Average change: ${avgChange.toFixed(2)}%. ` +
      `${trendDirection === 'bullish' ? 'Strong upward momentum observed.' : 
        trendDirection === 'bearish' ? 'Downward pressure detected.' : 'Sideways movement with mixed signals.'}`;

    const recommendations = [
      avgChange > 5 ? 'Consider taking profits on strong performers' : 'Hold current positions',
      volatility > 10 ? 'High volatility detected - use caution' : 'Stable conditions for entry',
      trendDirection === 'bullish' ? 'Look for dip-buying opportunities' : 'Consider defensive positioning'
    ];

    return {
      summary,
      recommendations,
      volatilityAnalysis: `Current volatility: ${volatility.toFixed(1)}% - ${volatility > 15 ? 'High' : volatility > 8 ? 'Moderate' : 'Low'}`,
      trendDirection
    };
  };

  // Alert detection
  const checkAlerts = (data: MarketData[]) => {
    const newAlerts: Alert[] = [];
    
    data.forEach(item => {
      if (Math.abs(item.changePercent) > alertThreshold) {
        newAlerts.push({
          id: `${item.symbol}-${Date.now()}`,
          message: `${item.symbol} ${item.changePercent > 0 ? 'surged' : 'dropped'} ${Math.abs(item.changePercent).toFixed(1)}% in the last period`,
          type: item.changePercent > 0 ? 'success' : 'warning',
          timestamp: new Date().toLocaleTimeString()
        });
      }
    });

    if (newAlerts.length > 0) {
      setAlerts(prev => [...prev, ...newAlerts].slice(-10)); // Keep last 10 alerts
    }
  };

  // Data fetching simulation
  const fetchMarketData = async () => {
    setIsLoading(true);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const data = selectedItems.map(item => generateMockData(item, marketType));
    setMarketData(data);
    
    // Generate AI insights
    const insights = generateAIInsights(data);
    setAiInsights(insights);
    
    // Check for alerts
    checkAlerts(data);
    
    setIsLoading(false);
  };

  // Auto-refresh data
  useEffect(() => {
    fetchMarketData();
    const interval = setInterval(fetchMarketData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [selectedItems, timeRange, marketType]);

  const PriceChart: React.FC<{ data: MarketData }> = ({ data }) => {
    const maxPrice = Math.max(...data.history.map(h => h.price));
    const minPrice = Math.min(...data.history.map(h => h.price));
    const range = maxPrice - minPrice;

    return (
      <div className="bg-gray-800 rounded-lg p-4 mb-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-lg font-semibold text-white">{data.symbol}</h3>
          <div className={`flex items-center gap-1 ${data.changePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {data.changePercent >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span className="font-medium">{data.changePercent.toFixed(2)}%</span>
          </div>
        </div>
        
        <div className="text-2xl font-bold text-white mb-2">
          ${data.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </div>
        
        {/* Simple SVG chart */}
        <div className="h-32 w-full">
          <svg width="100%" height="100%" className="overflow-visible">
            <polyline
              fill="none"
              stroke={data.changePercent >= 0 ? "#10b981" : "#ef4444"}
              strokeWidth="2"
              points={data.history.map((point, index) => {
                const x = (index / (data.history.length - 1)) * 100;
                const y = ((maxPrice - point.price) / range) * 100;
                return `${x}%,${y}%`;
              }).join(' ')}
            />
          </svg>
        </div>
        
        <div className="flex justify-between text-sm text-gray-400 mt-2">
          <span>24h High: ${data.high24h.toLocaleString()}</span>
          <span>24h Low: ${data.low24h.toLocaleString()}</span>
        </div>
      </div>
    );
  };

  const AlertPanel: React.FC = () => (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <Bell className="text-yellow-400" size={20} />
        <h3 className="text-lg font-semibold text-white">Recent Alerts</h3>
      </div>
      
      <div className="space-y-2 max-h-40 overflow-y-auto">
        {alerts.length === 0 ? (
          <p className="text-gray-400 text-sm">No recent alerts</p>
        ) : (
          alerts.map(alert => (
            <div
              key={alert.id}
              className={`p-2 rounded text-sm border-l-4 ${
                alert.type === 'success' ? 'bg-green-900/20 border-green-400 text-green-100' :
                alert.type === 'warning' ? 'bg-yellow-900/20 border-yellow-400 text-yellow-100' :
                alert.type === 'error' ? 'bg-red-900/20 border-red-400 text-red-100' :
                'bg-blue-900/20 border-blue-400 text-blue-100'
              }`}
            >
              <div className="flex justify-between items-start">
                <span>{alert.message}</span>
                <span className="text-xs opacity-70">{alert.timestamp}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  const AIInsightPanel: React.FC = () => (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <Brain className="text-purple-400" size={20} />
        <h3 className="text-lg font-semibold text-white">AI Market Insights</h3>
      </div>
      
      {aiInsights ? (
        <div className="space-y-3">
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-1">Summary</h4>
            <p className="text-sm text-gray-100">{aiInsights.summary}</p>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-1">Trend Direction</h4>
            <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
              aiInsights.trendDirection === 'bullish' ? 'bg-green-900/30 text-green-300' :
              aiInsights.trendDirection === 'bearish' ? 'bg-red-900/30 text-red-300' :
              'bg-gray-700 text-gray-300'
            }`}>
              {aiInsights.trendDirection === 'bullish' ? <TrendingUp size={12} /> :
               aiInsights.trendDirection === 'bearish' ? <TrendingDown size={12} /> :
               <BarChart3 size={12} />}
              {aiInsights.trendDirection.toUpperCase()}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-1">Recommendations</h4>
            <ul className="text-sm text-gray-100 space-y-1">
              {aiInsights.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-1">Volatility Analysis</h4>
            <p className="text-sm text-gray-100">{aiInsights.volatilityAnalysis}</p>
          </div>
        </div>
      ) : (
        <p className="text-gray-400 text-sm">Generating insights...</p>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="text-blue-400" size={32} />
              <div>
                <h1 className="text-2xl font-bold">Market Mirror</h1>
                <p className="text-gray-400 text-sm">AI-Powered Market Analysis</p>
              </div>
            </div>
            
            <button
              onClick={fetchMarketData}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={isLoading ? 'animate-spin' : ''} size={16} />
              {isLoading ? 'Updating...' : 'Refresh'}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Controls */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Market Type</label>
              <select
                value={marketType}
                onChange={(e) => setMarketType(e.target.value as any)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="crypto">Cryptocurrency</option>
                <option value="stocks">Stocks</option>
                <option value="ecommerce">E-commerce</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Time Range</label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="1d">1 Day</option>
                <option value="7d">7 Days</option>
                <option value="1m">1 Month</option>
                <option value="3m">3 Months</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Items to Track</label>
              <input
                type="text"
                value={selectedItems.join(', ')}
                onChange={(e) => setSelectedItems(e.target.value.split(', ').map(s => s.trim()))}
                placeholder="BTC, ETH, SOL"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Alert Threshold (%)</label>
              <input
                type="number"
                value={alertThreshold}
                onChange={(e) => setAlertThreshold(Number(e.target.value))}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Charts Column */}
          <div className="lg:col-span-2">
            <div className="mb-4">
              <h2 className="text-xl font-semibold mb-4">Price Charts</h2>
              {isLoading ? (
                <div className="bg-gray-800 rounded-lg p-8 text-center">
                  <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                  <p className="text-gray-400">Loading market data...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {marketData.map(data => (
                    <PriceChart key={data.symbol} data={data} />
                  ))}
                </div>
              )}
            </div>
            
            {/* Comparative Table */}
            {!isLoading && marketData.length > 0 && (
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">Performance Comparison</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left py-2 text-gray-300">Symbol</th>
                        <th className="text-right py-2 text-gray-300">Price</th>
                        <th className="text-right py-2 text-gray-300">Change</th>
                        <th className="text-right py-2 text-gray-300">Volume</th>
                      </tr>
                    </thead>
                    <tbody>
                      {marketData.map(data => (
                        <tr key={data.symbol} className="border-b border-gray-700/50">
                          <td className="py-2 font-medium">{data.symbol}</td>
                          <td className="text-right py-2">${data.price.toLocaleString()}</td>
                          <td className={`text-right py-2 ${data.changePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {data.changePercent >= 0 ? '+' : ''}{data.changePercent.toFixed(2)}%
                          </td>
                          <td className="text-right py-2 text-gray-400">{data.volume.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <AIInsightPanel />
            <AlertPanel />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketMirror;