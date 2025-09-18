import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Database, Book, Search, TrendingUp, RefreshCw } from 'lucide-react';

const KnowledgeBaseStats = ({ stats }) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await fetch('/api/knowledge/categories');
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const refreshStats = async () => {
    setIsRefreshing(true);
    try {
      const response = await fetch('/api/knowledge/stats');
      const newStats = await response.json();
      // Parent component would handle this update
      console.log('Refreshed stats:', newStats);
    } catch (error) {
      console.error('Failed to refresh stats:', error);
    } finally {
      setTimeout(() => setIsRefreshing(false), 1000); // Visual feedback
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Technology': 'bg-blue-100 text-blue-800',
      'Solutions': 'bg-green-100 text-green-800',
      'Industry': 'bg-purple-100 text-purple-800',
      'Business': 'bg-orange-100 text-orange-800',
      'Regulatory': 'bg-red-100 text-red-800',
      'Partners': 'bg-indigo-100 text-indigo-800',
      'Resources': 'bg-gray-100 text-gray-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const totalItems = stats?.total_items || 0;
  const categoryCounts = stats?.categories || {};

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.1 }}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800 flex items-center">
          <Database className="w-5 h-5 mr-2 text-blue-600" />
          Knowledge Base
        </h3>
        <button
          onClick={refreshStats}
          disabled={isRefreshing}
          className="text-gray-500 hover:text-gray-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-blue-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-600">{totalItems}</div>
          <div className="text-xs text-blue-700">Total Items</div>
        </div>
        <div className="bg-green-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-green-600">
            {Object.keys(categoryCounts).length}
          </div>
          <div className="text-xs text-green-700">Categories</div>
        </div>
      </div>

      {/* Category Breakdown */}
      {Object.keys(categoryCounts).length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Book className="w-4 h-4 mr-1" />
            Category Breakdown
          </div>

          <div className="space-y-1">
            {Object.entries(categoryCounts)
              .sort(([,a], [,b]) => b - a)
              .map(([category, count]) => (
                <div key={category} className="flex items-center justify-between">
                  <div className="flex items-center flex-1">
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(category)}`}>
                      {category}
                    </span>
                  </div>
                  <div className="text-sm font-medium text-gray-600 ml-2">
                    {count}
                  </div>
                </div>
              ))}
          </div>

          {/* Progress Bars */}
          <div className="space-y-1 mt-3">
            {Object.entries(categoryCounts)
              .sort(([,a], [,b]) => b - a)
              .slice(0, 3) // Show top 3 categories
              .map(([category, count]) => {
                const percentage = totalItems > 0 ? (count / totalItems) * 100 : 0;
                return (
                  <div key={`bar-${category}`} className="space-y-1">
                    <div className="flex justify-between text-xs text-gray-600">
                      <span>{category}</span>
                      <span>{percentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 1, delay: 0.5 }}
                        className="bg-blue-500 h-1.5 rounded-full"
                      />
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* Quality Indicators */}
      {stats && (
        <div className="mt-4 pt-3 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Avg Quality:</span>
              <div className="flex items-center">
                <TrendingUp className="w-3 h-3 text-green-500 mr-1" />
                <span className="font-medium">
                  {stats.avg_importance ? stats.avg_importance.toFixed(1) : 'N/A'}
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Vector DB:</span>
              <span className="font-medium text-blue-600">
                {stats.vector_collection_count || 0}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {totalItems === 0 && (
        <div className="text-center py-4">
          <Search className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-500">No knowledge base data</p>
          <p className="text-xs text-gray-400 mt-1">
            Run the spider to populate Rick's knowledge
          </p>
        </div>
      )}

      {/* Load Categories Info */}
      {categories.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <details className="group">
            <summary className="text-xs text-gray-600 cursor-pointer hover:text-gray-800 transition-colors">
              Available Categories ({categories.length})
            </summary>
            <div className="mt-2 space-y-1">
              {categories.map((cat, index) => (
                <div key={index} className="text-xs text-gray-500">
                  <span className="font-medium">{cat.name}:</span> {cat.description}
                </div>
              ))}
            </div>
          </details>
        </div>
      )}
    </motion.div>
  );
};

export default KnowledgeBaseStats;