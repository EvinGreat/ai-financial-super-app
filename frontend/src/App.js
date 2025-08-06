import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { usePlaidLink } from 'react-plaid-link';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Plaid Bank Connection Component
const PlaidLinkButton = ({ user, onSuccess }) => {
  const [linkToken, setLinkToken] = useState(null);
  const [loading, setLoading] = useState(false);

  // Create link token when component mounts
  useEffect(() => {
    const createLinkToken = async () => {
      try {
        setLoading(true);
        const response = await axios.post(`${API}/users/${user.id}/plaid/create-link-token`);
        setLinkToken(response.data.link_token);
      } catch (error) {
        console.error('Error creating link token:', error);
        alert('Error setting up bank connection: ' + (error.response?.data?.detail || error.message));
      } finally {
        setLoading(false);
      }
    };

    if (user && !linkToken) {
      createLinkToken();
    }
  }, [user]);

  const config = {
    token: linkToken,
    onSuccess: async (public_token, metadata) => {
      try {
        setLoading(true);
        await axios.post(`${API}/users/${user.id}/plaid/exchange-public-token`, {
          public_token
        });
        
        // Sync accounts immediately
        await axios.post(`${API}/users/${user.id}/plaid/sync-accounts`);
        
        alert('🎉 Bank account connected successfully! Your transactions are being synced.');
        onSuccess();
      } catch (error) {
        console.error('Error connecting bank account:', error);
        alert('Error connecting bank account: ' + (error.response?.data?.detail || error.message));
      } finally {
        setLoading(false);
      }
    },
    onExit: (err, metadata) => {
      if (err) {
        console.error('Plaid Link exit error:', err);
      }
    },
    onEvent: (eventName, metadata) => {
      console.log('Plaid Link event:', eventName, metadata);
    },
  };

  const { open, ready } = usePlaidLink(config);

  if (!linkToken || loading) {
    return (
      <button
        disabled
        className="bg-gradient-to-r from-blue-400 to-blue-500 text-white font-bold py-3 px-6 rounded-lg opacity-50 cursor-not-allowed"
      >
        {loading ? '🔄 Setting up...' : '🏦 Loading Bank Connection...'}
      </button>
    );
  }

  return (
    <button
      onClick={() => open()}
      disabled={!ready || loading}
      className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 disabled:opacity-50"
    >
      🏦 Connect Real Bank Account
    </button>
  );
};
// Main Dashboard Component
const FinancialDashboard = ({ user, onCreateAccount, onRunAnalysis }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/users/${user.id}/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchInsights = async () => {
    try {
      const response = await axios.get(`${API}/users/${user.id}/insights?limit=10`);
      setInsights(response.data);
    } catch (error) {
      console.error('Error fetching insights:', error.response?.data || error.message);
    }
  };

  useEffect(() => {
    if (user) {
      fetchDashboard();
      fetchInsights();
    }
  }, [user]);

  const runSpendingAnalysis = async () => {
    try {
      setLoading(true);
      await axios.post(`${API}/users/${user.id}/analyze-spending`);
      await fetchInsights();
      alert('AI spending analysis completed! Check your insights below.');
    } catch (error) {
      alert('Error running analysis: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const calculateHealthScore = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/users/${user.id}/calculate-financial-health`);
      await fetchDashboard();
      alert(`Financial Health Score calculated: ${response.data.overall_score.toFixed(1)}/100`);
    } catch (error) {
      alert('Error calculating health score: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const generateBudgetRecommendations = async () => {
    try {
      setLoading(true);
      const monthlyIncome = prompt('Enter your monthly income (optional):');
      const income = monthlyIncome ? parseFloat(monthlyIncome) : null;
      
      const response = await axios.post(`${API}/users/${user.id}/generate-budget-recommendations${income ? `?monthly_income=${income}` : ''}`);
      console.log('Budget recommendations:', response.data.recommendations);
      alert('Budget recommendations generated! Check the console for details.');
    } catch (error) {
      alert('Error generating budget recommendations: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  if (loading && !dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Loading your financial dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 mb-2">
                💰 AI Financial Super-App
              </h1>
              <p className="text-xl text-gray-600">Welcome back, {user.full_name}!</p>
            </div>
            <div className="text-right">
              {dashboardData?.financial_health_score && (
                <div className="bg-emerald-100 rounded-lg p-4">
                  <p className="text-sm text-emerald-700">Financial Health Score</p>
                  <p className="text-3xl font-bold text-emerald-600">
                    {dashboardData.financial_health_score.overall_score.toFixed(1)}/100
                  </p>
                </div>
              )}
            </div>
          </div>
          {/* Quick Stats */}
          {dashboardData && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Net Worth</h3>
                <p className="text-3xl font-bold">${dashboardData.net_worth.toLocaleString()}</p>
              </div>
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Monthly Cash Flow</h3>
                <p className="text-3xl font-bold">${dashboardData.monthly_cash_flow.toLocaleString()}</p>
              </div>
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Active Accounts</h3>
                <p className="text-3xl font-bold">{dashboardData.accounts_summary.total_count}</p>
              </div>
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Financial Goals</h3>
                <p className="text-3xl font-bold">{dashboardData.financial_goals.length}</p>
              </div>
            </div>
          )}

          {/* AI Action Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <button
              onClick={runSpendingAnalysis}
              disabled={loading}
              className="bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 disabled:opacity-50"
            >
              🧠 AI Spending Analysis
            </button>
            <button
              onClick={calculateHealthScore}
              disabled={loading}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 disabled:opacity-50"
            >
              📊 Health Score
            </button>
            <button
              onClick={generateBudgetRecommendations}
              disabled={loading}
              className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 disabled:opacity-50"
            >
              💡 Budget AI
            </button>
            <PlaidLinkButton user={user} onSuccess={fetchDashboard} />
            <button
              onClick={onCreateAccount}
              className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200"
            >
              + Manual Account
            </button>
          </div>
        </div>

        {/* AI Insights Section */}
        {insights.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">🤖 AI Financial Insights</h2>
            <div className="space-y-4">
              {insights.map((insight) => (
                <div
                  key={insight.id}
                  className={`p-6 rounded-lg border-l-4 ${
                    insight.importance === 1
                      ? 'border-red-500 bg-red-50'
                      : insight.importance === 2
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-blue-500 bg-blue-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-800 mb-2">{insight.title}</h3>
                      <p className="text-gray-600 mb-3">{insight.description}</p>
                      {insight.action_items.length > 0 && (
                        <div className="mb-3">
                          <p className="font-medium text-gray-700 mb-2">Action Items:</p>
                          <ul className="list-disc list-inside space-y-1">
                            {insight.action_items.map((item, index) => (
                              <li key={index} className="text-gray-600">{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {insight.potential_savings && (
                        <p className="text-emerald-600 font-semibold">
                          💰 Potential monthly savings: ${insight.potential_savings.toFixed(2)}
                        </p>
                      )}
                    </div>
                    <div className="ml-4 text-right">
                      <p className="text-sm text-gray-500">
                        Confidence: {(insight.confidence_score * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-400">
                        {new Date(insight.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Accounts Section */}
        {dashboardData?.accounts_summary.accounts.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">💳 Your Accounts</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {dashboardData.accounts_summary.accounts.map((account) => (
                <div key={account.id} className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-800">{account.account_name}</h3>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {account.account_type}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-gray-800 mb-2">
                    ${account.balance_current.toLocaleString()}
                  </p>
                  <p className="text-gray-600">{account.institution_name}</p>
                  {account.balance_available && account.balance_available !== account.balance_current && (
                    <p className="text-sm text-gray-500 mt-2">
                      Available: ${account.balance_available.toLocaleString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Transactions */}
        {dashboardData?.recent_transactions.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">📝 Recent Transactions</h2>
            <div className="space-y-4">
              {dashboardData.recent_transactions.slice(0, 10).map((transaction) => (
                <div key={transaction.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800">{transaction.transaction_name}</h3>
                    {transaction.merchant_name && (
                      <p className="text-gray-600">{transaction.merchant_name}</p>
                    )}
                    <p className="text-sm text-gray-500">
                      {new Date(transaction.transaction_date).toLocaleDateString()} • {transaction.category}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${transaction.amount < 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                      {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                    </p>
                    {transaction.is_pending && (
                      <span className="text-xs text-orange-600">Pending</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// User Creation Form
const UserCreationForm = ({ onUserCreated }) => {
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    phone: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/users`, formData);
      onUserCreated(response.data);
    } catch (error) {
      alert('Error creating user: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-blue-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">💰</h1>
          <h2 className="text-3xl font-bold text-gray-800 mb-2">AI Financial Super-App</h2>
          <p className="text-gray-600">Your path to building billions starts here</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-700 font-semibold mb-2">Full Name</label>
            <input
              type="text"
              required
              value={formData.full_name}
              onChange={(e) => setFormData({...formData, full_name: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              placeholder="Enter your full name"
            />
          </div>
          
          <div>
            <label className="block text-gray-700 font-semibold mb-2">Email</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              placeholder="Enter your email"
            />
          </div>
          
          <div>
            <label className="block text-gray-700 font-semibold mb-2">Phone (optional)</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              placeholder="Enter your phone number"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Creating Account...' : 'Start Your Billion Dollar Journey'}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Powered by OpenAI GPT-4o • AI-Driven Financial Intelligence
          </p>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [user, setUser] = useState(null);
  const [showCreateAccount, setShowCreateAccount] = useState(false);
  const [loading, setLoading] = useState(false);

  // Test API connection on load
  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await axios.get(`${API}/`);
        console.log('API Connected:', response.data);
      } catch (error) {
        console.error('API Connection Failed:', error);
      }
    };
    testConnection();
  }, []);

  const handleUserCreated = (newUser) => {
    setUser(newUser);
    localStorage.setItem('financialAppUser', JSON.stringify(newUser));
  };

  const handleCreateAccount = async (accountData) => {
    setLoading(true);
    try {
      await axios.post(`${API}/users/${user.id}/accounts`, accountData);
      setShowCreateAccount(false);
      alert('Account added successfully!');
    } catch (error) {
      alert('Error creating account: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('financialAppUser');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  if (!user) {
    return <UserCreationForm onUserCreated={handleUserCreated} />;
  }

  return (
    <>
      <FinancialDashboard
        user={user}
        onCreateAccount={() => alert('Account creation coming soon!')}
        onRunAnalysis={() => {}}
      />
   
    </>
  );
}

export default App;
