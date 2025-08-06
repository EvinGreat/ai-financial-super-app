import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [user, setUser] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    phone: ''
  });
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

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('financialAppUser');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/users`, formData);
      setUser(response.data);
      localStorage.setItem('financialAppUser', JSON.stringify(response.data));
      alert('🎉 User created successfully!');
    } catch (error) {
      console.error('Error creating user:', error);
      alert('Error creating user: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  if (user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">🎉</h1>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Welcome to Your Financial Super-App!</h2>
          <div className="bg-emerald-50 rounded-lg p-4 mb-6">
            <p className="text-emerald-700 font-semibold">{user.full_name}</p>
            <p className="text-emerald-600">{user.email}</p>
            <p className="text-sm text-emerald-500">User ID: {user.id}</p>
          </div>
          <p className="text-gray-600 mb-6">Your billion-dollar financial journey starts here!</p>
          <button
            onClick={() => {
              setUser(null);
              localStorage.removeItem('financialAppUser');
            }}
            className="bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200"
          >
            Create Another User
          </button>
        </div>
      </div>
    );
  }

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
            Powered by AI • Built for Success
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
