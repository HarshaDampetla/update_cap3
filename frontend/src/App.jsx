import React, { useState, useEffect } from 'react';
import {
  TrendingUp, TrendingDown, DollarSign, Wallet, Shield, Activity,
  Search, Plus, Trash2, Edit2, RefreshCw, CheckCircle2, AlertTriangle,
  ArrowUpRight, ArrowDownRight, Layers, BarChart3, PieChart, Users,
  ShoppingBag, X, LogOut, Lock, User as UserIcon
} from 'lucide-react';

const API_BASE = '/api';

export default function App() {
  // Authentication State
  const [token, setToken] = useState(localStorage.getItem('marketscope_token') || '');
  const [currentUser, setCurrentUser] = useState(null);
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'register'
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authError, setAuthError] = useState('');

  // Active Main Navigation Tab
  const [activeTab, setActiveTab] = useState('catalog'); // 'catalog' | 'order' | 'watchlists' | 'portfolio' | 'analytics' | 'admin'

  // Application Data States
  const [healthStatus, setHealthStatus] = useState('checking');
  const [stocks, setStocks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sectorFilter, setSectorFilter] = useState('');
  const [exchangeFilter, setExchangeFilter] = useState('');

  // Portfolio & Cash
  const [cashBalance, setCashBalance] = useState('0.0000');
  const [portfolioStats, setPortfolioStats] = useState(null);
  const [holdings, setHoldings] = useState([]);

  // Watchlists
  const [watchlists, setWatchlists] = useState([]);
  const [activeWatchlistId, setActiveWatchlistId] = useState(null);
  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [newWatchlistSymbols, setNewWatchlistSymbols] = useState('');
  const [addSymbolInput, setAddSymbolInput] = useState('');

  // Order Widget
  const [selectedStock, setSelectedStock] = useState(null);
  const [orderSide, setOrderSide] = useState('BUY');
  const [orderType, setOrderType] = useState('MARKET');
  const [orderQuantity, setOrderQuantity] = useState('10');
  const [orderLimitPrice, setOrderLimitPrice] = useState('');
  const [orderMessage, setOrderMessage] = useState(null);
  const [ordersList, setOrdersList] = useState([]);

  // Analytics
  const [dailyMovers, setDailyMovers] = useState({ top_gainers: [], top_losers: [] });
  const [sectorExposure, setSectorExposure] = useState({ sectors: [], total_market_value: '0.0000' });

  // Admin Data
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminOrderStats, setAdminOrderStats] = useState(null);
  const [newStockSymbol, setNewStockSymbol] = useState('');
  const [newStockName, setNewStockName] = useState('');
  const [newStockSector, setNewStockSector] = useState('');
  const [newStockExchange, setNewStockExchange] = useState('NASDAQ');
  const [newStockPrice, setNewStockPrice] = useState('100.0000');
  const [adminActionMessage, setAdminActionMessage] = useState(null);

  // Health check on mount
  useEffect(() => {
    fetch('/health')
      .then(res => res.json())
      .then(data => setHealthStatus(data.status))
      .catch(() => setHealthStatus('offline'));
  }, []);

  // Fetch Current User Profile on Token Change
  useEffect(() => {
    if (token) {
      fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => {
          if (!res.ok) throw new Error('Session expired');
          return res.json();
        })
        .then(user => {
          setCurrentUser(user);
          localStorage.setItem('marketscope_token', token);
        })
        .catch(() => {
          handleLogout();
        });
    } else {
      setCurrentUser(null);
      localStorage.removeItem('marketscope_token');
    }
  }, [token]);

  // Initial & Polled Data Fetching
  const refreshMarketData = () => {
    let url = `${API_BASE}/stocks?include_delisted=false`;
    if (searchQuery) url += `&query=${encodeURIComponent(searchQuery)}`;
    if (sectorFilter) url += `&sector=${encodeURIComponent(sectorFilter)}`;
    if (exchangeFilter) url += `&exchange=${encodeURIComponent(exchangeFilter)}`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        setStocks(data.items || []);
        if (!selectedStock && data.items && data.items.length > 0) {
          setSelectedStock(data.items[0]);
        }
      })
      .catch(console.error);
  };

  const refreshUserData = () => {
    if (!token) return;
    const headers = { Authorization: `Bearer ${token}` };

    // Cash
    fetch(`${API_BASE}/portfolio/cash`, { headers })
      .then(res => res.json())
      .then(data => setCashBalance(data.available_cash || '0.0000'))
      .catch(console.error);

    // Portfolio Stats
    fetch(`${API_BASE}/portfolio/statistics`, { headers })
      .then(res => res.json())
      .then(data => setPortfolioStats(data))
      .catch(console.error);

    // Holdings
    fetch(`${API_BASE}/portfolio/holdings`, { headers })
      .then(res => res.json())
      .then(data => setHoldings(data || []))
      .catch(console.error);

    // Watchlists
    fetch(`${API_BASE}/watchlists`, { headers })
      .then(res => res.json())
      .then(data => {
        setWatchlists(data || []);
        if (data && data.length > 0 && !activeWatchlistId) {
          setActiveWatchlistId(data[0].id);
        }
      })
      .catch(console.error);

    // Orders
    fetch(`${API_BASE}/orders`, { headers })
      .then(res => res.json())
      .then(data => setOrdersList(data || []))
      .catch(console.error);

    // Analytics
    fetch(`${API_BASE}/analytics/daily-performance`, { headers })
      .then(res => res.json())
      .then(data => setDailyMovers(data))
      .catch(console.error);

    fetch(`${API_BASE}/analytics/sector-exposure`, { headers })
      .then(res => res.json())
      .then(data => setSectorExposure(data))
      .catch(console.error);

    // Admin Telemetry if Admin
    if (currentUser?.role === 'ADMIN') {
      fetch(`${API_BASE}/admin/users`, { headers })
        .then(res => res.json())
        .then(setAdminUsers)
        .catch(console.error);

      fetch(`${API_BASE}/admin/statistics/orders`, { headers })
        .then(res => res.json())
        .then(setAdminOrderStats)
        .catch(console.error);
    }
  };

  useEffect(() => {
    refreshMarketData();
  }, [searchQuery, sectorFilter, exchangeFilter]);

  useEffect(() => {
    refreshUserData();
  }, [token, currentUser]);

  // Auth Handlers
  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    const endpoint = authMode === 'login' ? `${API_BASE}/auth/login` : `${API_BASE}/auth/register`;

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, password: authPassword })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || data.detail?.message || 'Authentication failed');
      }

      if (authMode === 'register') {
        // Auto login on register
        const loginRes = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: authEmail, password: authPassword })
        });
        const loginData = await loginRes.json();
        setToken(loginData.access_token);
      } else {
        setToken(data.access_token);
      }
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleLogout = () => {
    setToken('');
    setCurrentUser(null);
    localStorage.removeItem('marketscope_token');
  };

  // Quick Seed Credentials Filler
  const quickFillAuth = (email, password) => {
    setAuthEmail(email);
    setAuthPassword(password);
  };

  // Order Placement
  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    setOrderMessage(null);
    if (!token) {
      setOrderMessage({ type: 'error', text: 'Please sign in to execute trades.' });
      return;
    }
    if (!selectedStock) {
      setOrderMessage({ type: 'error', text: 'Please select a stock first.' });
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          symbol: selectedStock.symbol,
          side: orderSide,
          order_type: orderType,
          quantity: orderQuantity,
          limit_price: orderType === 'LIMIT' ? orderLimitPrice : null
        })
      });

      const data = await res.json();
      if (!res.ok) {
        if (data.code === 'INSUFFICIENT_FUNDS') {
          throw new Error(`Insufficient funds: Required $${data.required_funds} exceeds available $${data.available_cash} (AC-08)`);
        }
        throw new Error(data.message || data.detail?.message || 'Order failed');
      }

      setOrderMessage({
        type: 'success',
        text: `Order filled successfully: ${orderSide} ${orderQuantity} ${selectedStock.symbol} @ $${data.quote_price}`
      });
      refreshUserData();
      refreshMarketData();
    } catch (err) {
      setOrderMessage({ type: 'error', text: err.message });
    }
  };

  // Order Cancellation
  const handleCancelOrder = async (orderId) => {
    try {
      const res = await fetch(`${API_BASE}/orders/${orderId}/cancel`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || 'Cancellation failed');
      }
      refreshUserData();
    } catch (err) {
      alert(err.message);
    }
  };

  // Watchlist Actions
  const handleCreateWatchlist = async (e) => {
    e.preventDefault();
    try {
      const symList = newWatchlistSymbols.split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
      const res = await fetch(`${API_BASE}/watchlists`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ name: newWatchlistName, symbols: symList })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || 'Failed to create watchlist');
      }
      setNewWatchlistName('');
      setNewWatchlistSymbols('');
      refreshUserData();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleAddSymbolToWatchlist = async () => {
    if (!addSymbolInput || !activeWatchlistId) return;
    try {
      const res = await fetch(`${API_BASE}/watchlists/${activeWatchlistId}/symbols`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ symbols: [addSymbolInput.trim().toUpperCase()] })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || 'Symbol addition failed');
      }
      setAddSymbolInput('');
      refreshUserData();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleRemoveSymbol = async (watchlistId, symbol) => {
    try {
      await fetch(`${API_BASE}/watchlists/${watchlistId}/symbols/${symbol}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      refreshUserData();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteWatchlist = async (watchlistId) => {
    if (!confirm('Are you sure you want to delete this watchlist?')) return;
    try {
      await fetch(`${API_BASE}/watchlists/${watchlistId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      refreshUserData();
    } catch (err) {
      alert(err.message);
    }
  };

  // Market Tick Trigger
  const handleMarketTick = async () => {
    try {
      const res = await fetch(`${API_BASE}/market/tick`, { method: 'POST' });
      const data = await res.json();
      refreshMarketData();
      refreshUserData();
    } catch (err) {
      console.error('Tick error:', err);
    }
  };

  // Admin Actions
  const handleCreateStock = async (e) => {
    e.preventDefault();
    setAdminActionMessage(null);
    try {
      const res = await fetch(`${API_BASE}/admin/stocks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          symbol: newStockSymbol.trim().toUpperCase(),
          name: newStockName.trim(),
          sector: newStockSector.trim(),
          exchange: newStockExchange,
          initial_price: newStockPrice
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Stock creation failed');
      setAdminActionMessage({ type: 'success', text: `Stock ${data.symbol} added to catalog.` });
      setNewStockSymbol('');
      setNewStockName('');
      setNewStockSector('');
      refreshMarketData();
    } catch (err) {
      setAdminActionMessage({ type: 'error', text: err.message });
    }
  };

  const handleSoftDeleteStock = async (symbol) => {
    if (!confirm(`Are you sure you want to soft-delete ${symbol}? Row will be preserved as DELETED (AC-03).`)) return;
    try {
      const res = await fetch(`${API_BASE}/admin/stocks/${symbol}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Soft delete failed');
      setAdminActionMessage({ type: 'success', text: `Stock ${symbol} moved to DELETED state (AC-03).` });
      refreshMarketData();
    } catch (err) {
      setAdminActionMessage({ type: 'error', text: err.message });
    }
  };

  const handleUpdateUserRole = async (userId, targetRole) => {
    try {
      const res = await fetch(`${API_BASE}/admin/users/${userId}/role`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ role: targetRole })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Role update failed');
      setAdminActionMessage({ type: 'success', text: `User ${userId} role changed to ${targetRole} with audit log (AC-02).` });
      refreshUserData();
    } catch (err) {
      setAdminActionMessage({ type: 'error', text: err.message });
    }
  };

  // Calculations for Order Entry purchasing power
  const calculatedOrderPrice = selectedStock
    ? (orderType === 'LIMIT' && orderLimitPrice ? parseFloat(orderLimitPrice) || 0 : parseFloat(selectedStock.current_price) || 0)
    : 0;
  const calculatedTotalCost = calculatedOrderPrice * (parseFloat(orderQuantity) || 0);
  const isInsufficientFunds = orderSide === 'BUY' && calculatedTotalCost > parseFloat(cashBalance);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                MarketScope
              </span>
              <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                FinTech Platform
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* System Status */}
            <div className="flex items-center space-x-2 text-xs font-mono px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60">
              <span className={`w-2 h-2 rounded-full ${healthStatus === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`}></span>
              <span className="text-slate-400">API:</span>
              <span className={healthStatus === 'healthy' ? 'text-emerald-400 font-semibold' : 'text-rose-400'}>
                {healthStatus.toUpperCase()}
              </span>
            </div>

            {/* User Profile / Auth Toggle */}
            {currentUser ? (
              <div className="flex items-center space-x-3">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-semibold text-slate-200">{currentUser.email}</div>
                  <div className="flex items-center justify-end space-x-1">
                    <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                      currentUser.role === 'ADMIN' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                    }`}>
                      {currentUser.role}
                    </span>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  data-testid="logout-btn"
                  className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setAuthMode('login')}
                data-testid="open-login-btn"
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition shadow-md shadow-indigo-600/20"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* KPI Financial Overview Banner */}
        {currentUser && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="glass-card p-4 rounded-2xl glass-card-hover" data-testid="cash-balance-card">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium uppercase tracking-wider">Available Cash</span>
                <Wallet className="w-4 h-4 text-sky-400" />
              </div>
              <div className="text-2xl font-bold font-mono tracking-tight text-white" data-testid="cash-balance">
                ${parseFloat(cashBalance).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
              </div>
              <div className="text-xs text-slate-400 mt-1">Purchasing Power</div>
            </div>

            <div className="glass-card p-4 rounded-2xl glass-card-hover" data-testid="portfolio-invested-card">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium uppercase tracking-wider">Total Invested</span>
                <DollarSign className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-2xl font-bold font-mono tracking-tight text-white" data-testid="portfolio-total-invested">
                ${parseFloat(portfolioStats?.total_invested || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
              </div>
              <div className="text-xs text-slate-400 mt-1">Capital Basis</div>
            </div>

            <div className="glass-card p-4 rounded-2xl glass-card-hover" data-testid="portfolio-value-card">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium uppercase tracking-wider">Current Market Value</span>
                <Layers className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold font-mono tracking-tight text-white" data-testid="portfolio-current-value">
                ${parseFloat(portfolioStats?.current_value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
              </div>
              <div className="text-xs text-slate-400 mt-1">Active Positions</div>
            </div>

            <div className="glass-card p-4 rounded-2xl glass-card-hover" data-testid="portfolio-pnl-card">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium uppercase tracking-wider">Total P&L / Return</span>
                {parseFloat(portfolioStats?.absolute_pnl || 0) >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-rose-400" />
                )}
              </div>
              <div
                className={`text-2xl font-bold font-mono tracking-tight ${
                  parseFloat(portfolioStats?.absolute_pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
                }`}
                data-testid="portfolio-total-pnl"
              >
                {parseFloat(portfolioStats?.absolute_pnl || 0) >= 0 ? '+' : ''}
                ${parseFloat(portfolioStats?.absolute_pnl || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
              </div>
              <div className={`text-xs font-semibold ${
                parseFloat(portfolioStats?.percent_pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                {parseFloat(portfolioStats?.percent_pnl || 0) >= 0 ? '+' : ''}
                {portfolioStats?.percent_pnl || '0.0000'}% Return
              </div>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-2 overflow-x-auto space-x-2">
          <div className="flex space-x-2">
            {[
              { id: 'catalog', label: 'Stocks & Quotes', icon: BarChart3 },
              { id: 'order', label: 'Trade Execution', icon: ShoppingBag },
              { id: 'watchlists', label: 'Watchlists (AC-04)', icon: Layers },
              { id: 'portfolio', label: 'Portfolio Holdings', icon: PieChart },
              { id: 'analytics', label: 'Daily Analytics (AC-10)', icon: TrendingUp },
              ...(currentUser?.role === 'ADMIN' ? [{ id: 'admin', label: 'Admin Console (AC-02, AC-03)', icon: Shield }] : [])
            ].map(tab => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  data-testid={`nav-${tab.id}-btn`}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>

          <button
            onClick={handleMarketTick}
            data-testid="trigger-market-tick-btn"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 hover:text-white border border-slate-700/80 transition"
            title="Simulate Market Price Movement Tick"
          >
            <RefreshCw className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden sm:inline">Market Tick</span>
          </button>
        </div>

        {/* Tab 1: Stock Catalog & Discovery */}
        {activeTab === 'catalog' && (
          <div className="space-y-4">
            {/* Search & Filter Bar */}
            <div className="glass-card p-4 rounded-2xl flex flex-col md:flex-row gap-3 items-center justify-between">
              <div className="relative w-full md:w-80">
                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search ticker or company name..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  data-testid="stock-search-input"
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-9 pr-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center space-x-3 w-full md:w-auto">
                <select
                  value={sectorFilter}
                  onChange={e => setSectorFilter(e.target.value)}
                  data-testid="stock-sector-filter"
                  className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">All Sectors</option>
                  <option value="Technology">Technology</option>
                  <option value="Financials">Financials</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Consumer">Consumer Discretionary</option>
                  <option value="Energy">Energy</option>
                </select>

                <select
                  value={exchangeFilter}
                  onChange={e => setExchangeFilter(e.target.value)}
                  data-testid="stock-exchange-filter"
                  className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">All Exchanges</option>
                  <option value="NASDAQ">NASDAQ</option>
                  <option value="NYSE">NYSE</option>
                </select>
              </div>
            </div>

            {/* Stocks Table */}
            <div className="glass-card rounded-2xl overflow-hidden border border-slate-800">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm" data-testid="stocks-catalog-table">
                  <thead className="bg-slate-900/80 text-xs font-semibold uppercase tracking-wider text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Symbol</th>
                      <th className="py-3 px-4">Company Name</th>
                      <th className="py-3 px-4">Sector</th>
                      <th className="py-3 px-4">Exchange</th>
                      <th className="py-3 px-4 text-right">Current Price</th>
                      <th className="py-3 px-4 text-right">Day Change</th>
                      <th className="py-3 px-4 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono text-xs sm:text-sm">
                    {stocks.map(stock => {
                      const isUp = stock.change_percent?.startsWith('+') ?? false;
                      return (
                        <tr key={stock.symbol} className="hover:bg-slate-800/30 transition">
                          <td className="py-3 px-4 font-bold text-white flex items-center space-x-2">
                            <span>{stock.symbol}</span>
                          </td>
                          <td className="py-3 px-4 text-slate-300 font-sans font-medium">{stock.name}</td>
                          <td className="py-3 px-4 text-slate-400 font-sans">{stock.sector}</td>
                          <td className="py-3 px-4 text-slate-400 font-sans">{stock.exchange}</td>
                          <td className="py-3 px-4 text-right font-bold text-white">
                            ${parseFloat(stock.current_price).toFixed(4)}
                          </td>
                          <td className={`py-3 px-4 text-right font-semibold ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {stock.change_percent}
                          </td>
                          <td className="py-3 px-4 text-center">
                            <button
                              onClick={() => {
                                setSelectedStock(stock);
                                setActiveTab('order');
                              }}
                              data-testid={`trade-btn-${stock.symbol}`}
                              className="px-3 py-1 rounded-lg bg-indigo-600/20 text-indigo-300 hover:bg-indigo-600 hover:text-white border border-indigo-500/30 transition text-xs font-sans font-medium"
                            >
                              Trade
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Trade Execution Order Entry */}
        {activeTab === 'order' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Order Entry Form */}
            <div className="lg:col-span-1 glass-card p-6 rounded-2xl border border-slate-800 space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-base font-bold text-white">Order Entry</h3>
                {selectedStock && (
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-sky-400 border border-slate-700">
                    {selectedStock.symbol} • ${parseFloat(selectedStock.current_price).toFixed(4)}
                  </span>
                )}
              </div>

              {/* Side Switcher (BUY / SELL) */}
              <div className="grid grid-cols-2 gap-2 p-1 bg-slate-900 rounded-xl border border-slate-800">
                <button
                  type="button"
                  onClick={() => setOrderSide('BUY')}
                  data-testid="buy-order-btn"
                  className={`py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition ${
                    orderSide === 'BUY'
                      ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Buy
                </button>
                <button
                  type="button"
                  onClick={() => setOrderSide('SELL')}
                  data-testid="sell-order-btn"
                  className={`py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition ${
                    orderSide === 'SELL'
                      ? 'bg-rose-600 text-white shadow-md shadow-rose-600/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Sell
                </button>
              </div>

              <form onSubmit={handlePlaceOrder} className="space-y-4">
                {/* Symbol Selection */}
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Target Symbol</label>
                  <select
                    value={selectedStock?.symbol || ''}
                    onChange={e => {
                      const found = stocks.find(s => s.symbol === e.target.value);
                      if (found) setSelectedStock(found);
                    }}
                    data-testid="order-symbol-select"
                    className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 font-mono"
                  >
                    {stocks.map(s => (
                      <option key={s.symbol} value={s.symbol}>
                        {s.symbol} — {s.name} (${parseFloat(s.current_price).toFixed(2)})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Order Type */}
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Order Type</label>
                  <select
                    value={orderType}
                    onChange={e => setOrderType(e.target.value)}
                    data-testid="order-type-select"
                    className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="MARKET">Market Order</option>
                    <option value="LIMIT">Limit Order</option>
                  </select>
                </div>

                {/* Limit Price if LIMIT */}
                {orderType === 'LIMIT' && (
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Limit Price ($)</label>
                    <input
                      type="number"
                      step="0.0001"
                      placeholder="e.g. 150.0000"
                      value={orderLimitPrice}
                      onChange={e => setOrderLimitPrice(e.target.value)}
                      data-testid="order-limit-price-input"
                      required
                      className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-sm font-mono text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                )}

                {/* Quantity */}
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Quantity (Shares)</label>
                  <input
                    type="number"
                    step="1"
                    min="1"
                    value={orderQuantity}
                    onChange={e => setOrderQuantity(e.target.value)}
                    data-testid="order-quantity-input"
                    required
                    className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-sm font-mono text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>

                {/* Pre-trade Calculation & Warning (AC-08) */}
                <div className="p-3 bg-slate-900/90 rounded-xl border border-slate-800 space-y-1.5 text-xs font-mono">
                  <div className="flex justify-between text-slate-400">
                    <span>Est. Share Price:</span>
                    <span className="text-white">${calculatedOrderPrice.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Order Value:</span>
                    <span className="text-white font-bold">${calculatedTotalCost.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400 border-t border-slate-800 pt-1">
                    <span>Available Cash:</span>
                    <span className="text-sky-400">${parseFloat(cashBalance).toFixed(4)}</span>
                  </div>

                  {isInsufficientFunds && (
                    <div
                      data-testid="insufficient-funds-warning"
                      className="mt-2 p-2 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-300 font-sans text-xs flex items-start space-x-1.5"
                    >
                      <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                      <span>
                        <strong>Insufficient Funds (AC-08):</strong> Required ${calculatedTotalCost.toFixed(2)} exceeds available cash ${parseFloat(cashBalance).toFixed(2)}.
                      </span>
                    </div>
                  )}
                </div>

                {/* Status Message */}
                {orderMessage && (
                  <div
                    data-testid="order-status-banner"
                    className={`p-3 rounded-xl text-xs flex items-start space-x-2 ${
                      orderMessage.type === 'success'
                        ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                        : 'bg-rose-500/10 text-rose-300 border border-rose-500/30'
                    }`}
                  >
                    {orderMessage.type === 'success' ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                    )}
                    <span>{orderMessage.text}</span>
                  </div>
                )}

                <button
                  type="submit"
                  data-testid="submit-order-btn"
                  className={`w-full py-3 rounded-xl text-sm font-bold tracking-wide transition shadow-lg ${
                    orderSide === 'BUY'
                      ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20'
                      : 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/20'
                  }`}
                >
                  Submit {orderSide} Order
                </button>
              </form>
            </div>

            {/* Orders History & Live Queue */}
            <div className="lg:col-span-2 glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-base font-bold text-white">Order Execution Ledger (Append-Only NFR-02)</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm" data-testid="orders-history-table">
                  <thead className="bg-slate-900/80 text-xs font-semibold uppercase tracking-wider text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-3">Order ID</th>
                      <th className="py-3 px-3">Symbol</th>
                      <th className="py-3 px-3">Side</th>
                      <th className="py-3 px-3">Type</th>
                      <th className="py-3 px-3 text-right">Quantity</th>
                      <th className="py-3 px-3 text-right">Price</th>
                      <th className="py-3 px-3">Status</th>
                      <th className="py-3 px-3 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                    {ordersList.map(order => (
                      <tr key={order.id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3 px-3 text-slate-400">#{order.id}</td>
                        <td className="py-3 px-3 font-bold text-white">{order.symbol}</td>
                        <td className="py-3 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            order.side === 'BUY' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                          }`}>
                            {order.side}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-slate-400">{order.order_type}</td>
                        <td className="py-3 px-3 text-right text-white">{parseFloat(order.quantity).toFixed(2)}</td>
                        <td className="py-3 px-3 text-right text-white">${parseFloat(order.quote_price).toFixed(2)}</td>
                        <td className="py-3 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            order.status === 'EXECUTED'
                              ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                              : order.status === 'PENDING'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'bg-slate-700/40 text-slate-400 border border-slate-700'
                          }`}>
                            {order.status}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-center">
                          {order.status === 'PENDING' && (
                            <button
                              onClick={() => handleCancelOrder(order.id)}
                              data-testid={`cancel-order-btn-${order.id}`}
                              className="px-2 py-1 rounded bg-rose-500/20 text-rose-300 hover:bg-rose-500 hover:text-white transition text-[10px]"
                            >
                              Cancel
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                    {ordersList.length === 0 && (
                      <tr>
                        <td colSpan={8} className="py-6 text-center text-slate-500 font-sans">
                          No trade orders placed yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Watchlists (AC-04, AC-05) */}
        {activeTab === 'watchlists' && (
          <div className="space-y-6">
            {/* Create Watchlist Card */}
            <div className="glass-card p-4 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="text-sm font-bold text-white">Create New Watchlist (AC-04)</h3>
                <p className="text-xs text-slate-400">Maximum limit: 10 watchlists per customer.</p>
              </div>

              <form onSubmit={handleCreateWatchlist} className="flex flex-wrap items-center gap-2 w-full md:w-auto">
                <input
                  type="text"
                  placeholder="Watchlist Name..."
                  value={newWatchlistName}
                  onChange={e => setNewWatchlistName(e.target.value)}
                  data-testid="create-watchlist-name-input"
                  required
                  className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <input
                  type="text"
                  placeholder="Symbols (e.g. AAPL, NVDA)..."
                  value={newWatchlistSymbols}
                  onChange={e => setNewWatchlistSymbols(e.target.value)}
                  data-testid="create-watchlist-symbols-input"
                  required
                  className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  type="submit"
                  data-testid="create-watchlist-submit-btn"
                  className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition flex items-center space-x-1"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Create</span>
                </button>
              </form>
            </div>

            {/* Watchlist Tabs */}
            <div className="flex space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
              {watchlists.map(wl => (
                <div key={wl.id} className="flex items-center space-x-1">
                  <button
                    onClick={() => setActiveWatchlistId(wl.id)}
                    data-testid={`watchlist-tab-${wl.id}`}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold transition whitespace-nowrap ${
                      activeWatchlistId === wl.id
                        ? 'bg-slate-800 text-indigo-400 border border-indigo-500/40'
                        : 'text-slate-400 hover:text-white hover:bg-slate-900'
                    }`}
                  >
                    {wl.name} ({wl.symbols?.length || 0})
                  </button>
                  <button
                    onClick={() => handleDeleteWatchlist(wl.id)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 transition"
                    title="Delete Watchlist"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>

            {/* Active Watchlist Items */}
            {activeWatchlistId && (
              <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <span className="text-base font-bold text-white">
                      {watchlists.find(w => w.id === activeWatchlistId)?.name}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      ({watchlists.find(w => w.id === activeWatchlistId)?.symbols?.length || 0} stocks)
                    </span>
                  </div>

                  {/* Add Symbol Input */}
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      placeholder="Add ticker (e.g. MSFT)..."
                      value={addSymbolInput}
                      onChange={e => setAddSymbolInput(e.target.value)}
                      data-testid="add-symbol-input"
                      className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-white uppercase placeholder-slate-500 font-mono"
                    />
                    <button
                      onClick={handleAddSymbolToWatchlist}
                      data-testid="add-symbol-btn"
                      className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition flex items-center space-x-1"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Add</span>
                    </button>
                  </div>
                </div>

                {/* Items Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {watchlists
                    .find(w => w.id === activeWatchlistId)
                    ?.items?.map(item => {
                      const isUp = item.change_percent?.startsWith('+');
                      return (
                        <div
                          key={item.symbol}
                          className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 flex items-center justify-between hover:border-slate-700 transition"
                        >
                          <div>
                            <div className="text-sm font-bold text-white font-mono flex items-center space-x-2">
                              <span>{item.symbol}</span>
                              <span className={`text-xs ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {item.change_percent}
                              </span>
                            </div>
                            <div className="text-xs text-slate-400 truncate max-w-[140px]">{item.name}</div>
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className="text-right font-mono font-bold text-white text-sm">
                              ${parseFloat(item.current_price).toFixed(2)}
                            </div>
                            <button
                              onClick={() => handleRemoveSymbol(activeWatchlistId, item.symbol)}
                              data-testid={`remove-symbol-btn-${item.symbol}`}
                              className="text-slate-500 hover:text-rose-400 transition"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 4: Portfolio Holdings Table */}
        {activeTab === 'portfolio' && (
          <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-white">Active Portfolio Holdings</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm" data-testid="holdings-table">
                <thead className="bg-slate-900/80 text-xs font-semibold uppercase tracking-wider text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Symbol</th>
                    <th className="py-3 px-4">Asset Name</th>
                    <th className="py-3 px-4 text-right">Shares</th>
                    <th className="py-3 px-4 text-right">Avg Cost</th>
                    <th className="py-3 px-4 text-right">Current Price</th>
                    <th className="py-3 px-4 text-right">Market Value</th>
                    <th className="py-3 px-4 text-right">Unrealized P&L</th>
                    <th className="py-3 px-4 text-right">Return %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono text-xs sm:text-sm">
                  {holdings.map(h => {
                    const isUp = parseFloat(h.absolute_pnl) >= 0;
                    return (
                      <tr key={h.symbol} className="hover:bg-slate-800/30 transition">
                        <td className="py-3 px-4 font-bold text-white">{h.symbol}</td>
                        <td className="py-3 px-4 text-slate-300 font-sans">{h.name}</td>
                        <td className="py-3 px-4 text-right text-white">{parseFloat(h.shares_held).toFixed(2)}</td>
                        <td className="py-3 px-4 text-right text-slate-400">${parseFloat(h.average_buy_price).toFixed(2)}</td>
                        <td className="py-3 px-4 text-right text-white font-bold">${parseFloat(h.current_price).toFixed(2)}</td>
                        <td className="py-3 px-4 text-right text-white">${parseFloat(h.current_value).toFixed(2)}</td>
                        <td className={`py-3 px-4 text-right font-semibold ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {isUp ? '+' : ''}${parseFloat(h.absolute_pnl).toFixed(2)}
                        </td>
                        <td className={`py-3 px-4 text-right font-bold ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {isUp ? '+' : ''}{h.percent_pnl}%
                        </td>
                      </tr>
                    );
                  })}
                  {holdings.length === 0 && (
                    <tr>
                      <td colSpan={8} className="py-6 text-center text-slate-500 font-sans">
                        No active equity holdings found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 5: Analytics Dashboard (AC-10) */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Top 5 Gainers */}
              <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex items-center space-x-2 text-emerald-400 pb-2 border-b border-slate-800">
                  <ArrowUpRight className="w-5 h-5" />
                  <h3 className="text-base font-bold text-white">Top 5 Gainers (AC-10)</h3>
                </div>

                <div className="space-y-2">
                  {dailyMovers.top_gainers?.map(g => (
                    <div
                      key={g.symbol}
                      className="p-3 rounded-xl bg-slate-900/60 border border-emerald-500/20 flex items-center justify-between"
                    >
                      <div>
                        <div className="text-sm font-bold font-mono text-white">{g.symbol}</div>
                        <div className="text-xs text-slate-400">{g.name}</div>
                      </div>
                      <div className="text-right font-mono">
                        <div className="text-sm font-bold text-emerald-400">{g.change_percent}</div>
                        <div className="text-xs text-slate-400">+${parseFloat(g.change_amount).toFixed(2)}</div>
                      </div>
                    </div>
                  ))}
                  {dailyMovers.top_gainers?.length === 0 && (
                    <div className="text-xs text-slate-500 text-center py-4">No active gainers currently.</div>
                  )}
                </div>
              </div>

              {/* Top 5 Losers */}
              <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex items-center space-x-2 text-rose-400 pb-2 border-b border-slate-800">
                  <ArrowDownRight className="w-5 h-5" />
                  <h3 className="text-base font-bold text-white">Top 5 Losers (AC-10)</h3>
                </div>

                <div className="space-y-2">
                  {dailyMovers.top_losers?.map(l => (
                    <div
                      key={l.symbol}
                      className="p-3 rounded-xl bg-slate-900/60 border border-rose-500/20 flex items-center justify-between"
                    >
                      <div>
                        <div className="text-sm font-bold font-mono text-white">{l.symbol}</div>
                        <div className="text-xs text-slate-400">{l.name}</div>
                      </div>
                      <div className="text-right font-mono">
                        <div className="text-sm font-bold text-rose-400">{l.change_percent}</div>
                        <div className="text-xs text-slate-400">${parseFloat(l.change_amount).toFixed(2)}</div>
                      </div>
                    </div>
                  ))}
                  {dailyMovers.top_losers?.length === 0 && (
                    <div className="text-xs text-slate-500 text-center py-4">No active losers currently.</div>
                  )}
                </div>
              </div>
            </div>

            {/* Sector Exposure */}
            <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-base font-bold text-white">Sector Allocation Exposure</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {sectorExposure.sectors?.map(s => (
                  <div key={s.sector} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span className="font-semibold text-slate-200">{s.sector}</span>
                      <span className="font-bold text-indigo-400 font-mono">{s.weight_percent}</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden mb-2">
                      <div
                        className="bg-indigo-500 h-2 rounded-full"
                        style={{ width: s.weight_percent }}
                      ></div>
                    </div>
                    <div className="text-xs font-mono text-slate-400">
                      Market Value: ${parseFloat(s.market_value).toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 6: Admin Console (AC-02, AC-03) */}
        {activeTab === 'admin' && currentUser?.role === 'ADMIN' && (
          <div className="space-y-6">
            {adminActionMessage && (
              <div
                className={`p-3 rounded-xl text-xs flex items-center space-x-2 ${
                  adminActionMessage.type === 'success'
                    ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                    : 'bg-rose-500/10 text-rose-300 border border-rose-500/30'
                }`}
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{adminActionMessage.text}</span>
              </div>
            )}

            {/* Stock Catalog Creation Form */}
            <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-base font-bold text-white">Create Stock Symbol in Catalog (AC-03)</h3>
              <form onSubmit={handleCreateStock} className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                <input
                  type="text"
                  placeholder="Symbol (e.g. UBER)"
                  value={newStockSymbol}
                  onChange={e => setNewStockSymbol(e.target.value)}
                  data-testid="admin-stock-symbol-input"
                  required
                  className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs uppercase font-mono text-white"
                />
                <input
                  type="text"
                  placeholder="Company Name"
                  value={newStockName}
                  onChange={e => setNewStockName(e.target.value)}
                  data-testid="admin-stock-name-input"
                  required
                  className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white"
                />
                <input
                  type="text"
                  placeholder="Sector (e.g. Technology)"
                  value={newStockSector}
                  onChange={e => setNewStockSector(e.target.value)}
                  data-testid="admin-stock-sector-input"
                  required
                  className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white"
                />
                <select
                  value={newStockExchange}
                  onChange={e => setNewStockExchange(e.target.value)}
                  data-testid="admin-stock-exchange-select"
                  className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white"
                >
                  <option value="NASDAQ">NASDAQ</option>
                  <option value="NYSE">NYSE</option>
                </select>
                <input
                  type="number"
                  step="0.0001"
                  placeholder="Initial Price"
                  value={newStockPrice}
                  onChange={e => setNewStockPrice(e.target.value)}
                  data-testid="admin-stock-price-input"
                  required
                  className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs font-mono text-white"
                />
                <button
                  type="submit"
                  data-testid="admin-create-stock-btn"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition flex items-center justify-center space-x-1"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Stock</span>
                </button>
              </form>
            </div>

            {/* Catalog Soft-Delete Table */}
            <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-base font-bold text-white">Stock Catalog Soft-Delete Invariant (AC-03)</h3>
              <p className="text-xs text-slate-400">Soft-deleting sets status to DELETED. Row is never purged from SQL.</p>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-900/80 text-slate-400 uppercase border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Symbol</th>
                      <th className="py-2.5 px-3 font-sans">Name</th>
                      <th className="py-2.5 px-3 font-sans">Sector</th>
                      <th className="py-2.5 px-3 text-right">Price</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-center font-sans">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {stocks.map(s => (
                      <tr key={s.symbol}>
                        <td className="py-2.5 px-3 font-bold text-white">{s.symbol}</td>
                        <td className="py-2.5 px-3 text-slate-300 font-sans">{s.name}</td>
                        <td className="py-2.5 px-3 text-slate-400 font-sans">{s.sector}</td>
                        <td className="py-2.5 px-3 text-right text-white">${parseFloat(s.current_price).toFixed(2)}</td>
                        <td className="py-2.5 px-3">
                          <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">
                            {s.status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          <button
                            onClick={() => handleSoftDeleteStock(s.symbol)}
                            data-testid={`admin-delete-btn-${s.symbol}`}
                            className="px-2.5 py-1 rounded bg-rose-500/20 text-rose-300 hover:bg-rose-500 hover:text-white transition font-sans text-xs"
                          >
                            Soft Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* User Account Role Management (AC-02) */}
            <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-base font-bold text-white">User Role Administration & Audit Trail (AC-02)</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/80 text-slate-400 uppercase border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">User ID</th>
                      <th className="py-2.5 px-3">Email</th>
                      <th className="py-2.5 px-3">Current Role</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-center">Change Role</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {adminUsers.map(u => (
                      <tr key={u.id}>
                        <td className="py-2.5 px-3 text-slate-400">#{u.id}</td>
                        <td className="py-2.5 px-3 font-sans font-medium text-white">{u.email}</td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            u.role === 'ADMIN' ? 'bg-amber-500/20 text-amber-300' : 'bg-sky-500/20 text-sky-300'
                          }`}>
                            {u.role}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] ${
                            u.status === 'ACTIVE' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                          }`}>
                            {u.status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-center space-x-1 font-sans">
                          {['CUSTOMER', 'ADMIN', 'SUSPENDED'].map(r => (
                            <button
                              key={r}
                              onClick={() => handleUpdateUserRole(u.id, r)}
                              data-testid={`role-btn-${u.id}-${r}`}
                              disabled={u.role === r}
                              className={`px-2 py-0.5 rounded text-[10px] font-semibold transition ${
                                u.role === r
                                  ? 'opacity-40 cursor-not-allowed bg-slate-800 text-slate-500'
                                  : 'bg-indigo-600/30 text-indigo-300 hover:bg-indigo-600 hover:text-white'
                              }`}
                            >
                              {r}
                            </button>
                          ))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Auth Modal (if not signed in or opened) */}
      {!currentUser && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card max-w-md w-full p-6 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center mx-auto shadow-lg shadow-indigo-600/30">
                <Lock className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight">
                {authMode === 'login' ? 'Welcome to MarketScope' : 'Open Retail Brokerage Account'}
              </h2>
              <p className="text-xs text-slate-400">
                AI-Native Trading & Portfolio Analytics Engine (BC-AINE-006)
              </p>
            </div>

            {/* Quick Credentials Buttons */}
            <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 space-y-1.5">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Quick Fill Test Credentials:</div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => quickFillAuth('admin@marketscope.com', 'AdminPass123!')}
                  data-testid="quick-admin-login-btn"
                  className="px-2.5 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 transition text-left"
                >
                  <div className="font-bold">Admin Account</div>
                  <div className="text-[10px] text-slate-400 font-mono truncate">admin@marketscope.com</div>
                </button>
                <button
                  type="button"
                  onClick={() => quickFillAuth('trader1@marketscope.com', 'TraderPass123!')}
                  data-testid="quick-trader-login-btn"
                  className="px-2.5 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 transition text-left"
                >
                  <div className="font-bold">Customer 1 ($100k)</div>
                  <div className="text-[10px] text-slate-400 font-mono truncate">trader1@marketscope.com</div>
                </button>
              </div>
            </div>

            <form onSubmit={handleAuthSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Email Address</label>
                <input
                  type="email"
                  value={authEmail}
                  onChange={e => setAuthEmail(e.target.value)}
                  data-testid="auth-email-input"
                  required
                  placeholder="investor@example.com"
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Password</label>
                <input
                  type="password"
                  value={authPassword}
                  onChange={e => setAuthPassword(e.target.value)}
                  data-testid="auth-password-input"
                  required
                  placeholder="••••••••••••"
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              {authError && (
                <div data-testid="auth-error-banner" className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                  {authError}
                </div>
              )}

              <button
                type="submit"
                data-testid="auth-submit-btn"
                className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-bold tracking-wide transition shadow-lg shadow-indigo-600/25"
              >
                {authMode === 'login' ? 'Sign In to Account' : 'Register & Claim $100,000 Cash'}
              </button>
            </form>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                className="text-xs text-indigo-400 hover:text-indigo-300 transition"
              >
                {authMode === 'login' ? "Don't have an account? Register here" : 'Already registered? Sign In'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 mt-auto bg-slate-900/40 text-center text-xs text-slate-500">
        MarketScope Engine v1.0.0 • AI-Native Brokerage & Analytics Platform • Capstone BC-AINE-006
      </footer>
    </div>
  );
}
