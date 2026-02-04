/**
 * Algorithm Builder Page
 * 
 * Main interface for building trading algorithms by selecting and weighting technical indicators.
 * This is the core feature of Phase 1.
 */

'use client';

import Link from 'next/link';
import { Card, SimpleCard } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useState } from 'react';

export default function BuilderPage() {
  const [selectedIndicators] = useState(0);

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Algorithm Builder</h1>
            <p className="text-sm text-gray-600 mt-1">
              Create your trading algorithm by selecting and weighting indicators
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm">
              Reset
            </Button>
            <Button variant="primary" size="sm">
              Save Algorithm
            </Button>
            <Link
              href="/"
              className="text-blue-600 hover:text-blue-700 underline text-sm ml-2"
            >
              ← Home
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content - Three Column Layout */}
      <div className="mx-auto max-w-7xl p-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Panel - Indicator Selection */}
          <div className="lg:col-span-3 space-y-4">
            <Card title="Select Indicators" description="Choose indicators to include in your algorithm">
              <div className="space-y-3">
                {/* Category filters */}
                <div className="flex flex-wrap gap-2">
                  <button className="px-3 py-1 text-xs rounded-full bg-blue-100 text-blue-700 font-medium">
                    All
                  </button>
                  <button className="px-3 py-1 text-xs rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200">
                    Momentum
                  </button>
                  <button className="px-3 py-1 text-xs rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200">
                    Trend
                  </button>
                  <button className="px-3 py-1 text-xs rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200">
                    Volatility
                  </button>
                </div>

                {/* Search */}
                <input
                  type="text"
                  placeholder="Search indicators..."
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                {/* Indicator list placeholder */}
                <div className="space-y-2 pt-2">
                  <div className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors">
                    <p className="text-sm font-medium text-gray-900">RSI</p>
                    <p className="text-xs text-gray-600">Momentum indicator</p>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors">
                    <p className="text-sm font-medium text-gray-900">MACD</p>
                    <p className="text-xs text-gray-600">Momentum indicator</p>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors">
                    <p className="text-sm font-medium text-gray-900">SMA</p>
                    <p className="text-xs text-gray-600">Trend indicator</p>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors">
                    <p className="text-sm font-medium text-gray-900">EMA</p>
                    <p className="text-xs text-gray-600">Trend indicator</p>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors">
                    <p className="text-sm font-medium text-gray-900">Bollinger Bands</p>
                    <p className="text-xs text-gray-600">Volatility indicator</p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Educational tip */}
            <SimpleCard padding="sm">
              <div className="flex gap-2">
                <span className="text-lg">💡</span>
                <div>
                  <p className="text-xs font-semibold text-gray-900">Tip</p>
                  <p className="text-xs text-gray-600 mt-1">
                    Start with 2-3 indicators. Combining different categories often works best!
                  </p>
                </div>
              </div>
            </SimpleCard>
          </div>

          {/* Center Panel - Algorithm Preview */}
          <div className="lg:col-span-6 space-y-4">
            <Card 
              title="Your Algorithm" 
              description="Preview and configure your trading strategy"
            >
              <div className="space-y-4">
                {/* Algorithm name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Algorithm Name
                  </label>
                  <input
                    type="text"
                    placeholder="My Trading Strategy"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Selected indicators */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Selected Indicators ({selectedIndicators})
                  </label>
                  
                  {selectedIndicators === 0 ? (
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                      <p className="text-gray-500">
                        No indicators selected yet
                      </p>
                      <p className="text-sm text-gray-400 mt-1">
                        Choose indicators from the left panel to get started
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {/* Placeholder for selected indicators */}
                      <p className="text-sm text-gray-600">
                        Selected indicators will appear here with their settings
                      </p>
                    </div>
                  )}
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description (optional)
                  </label>
                  <textarea
                    placeholder="Describe your trading strategy..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  />
                </div>
              </div>
            </Card>

            {/* Chart preview placeholder */}
            <Card title="Chart Preview">
              <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                <p className="text-gray-500">
                  Chart visualization will appear here
                </p>
              </div>
            </Card>
          </div>

          {/* Right Panel - Weight Adjustment */}
          <div className="lg:col-span-3 space-y-4">
            <Card 
              title="Indicator Weights" 
              description="Adjust the influence of each indicator"
            >
              <div className="space-y-4">
                {selectedIndicators === 0 ? (
                  <p className="text-sm text-gray-500">
                    Select indicators to adjust their weights
                  </p>
                ) : (
                  <div>
                    <p className="text-sm text-gray-600">
                      Weight sliders will appear here for each selected indicator
                    </p>
                  </div>
                )}

                {/* Total weight indicator */}
                <div className="pt-4 mt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      Total Weight
                    </span>
                    <span className="text-sm font-bold text-gray-900">
                      0%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-600 transition-all"
                      style={{ width: '0%' }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Weights should sum to 100%
                  </p>
                </div>
              </div>
            </Card>

            {/* Actions */}
            <Card title="Actions">
              <div className="space-y-2">
                <Button variant="primary" className="w-full" disabled>
                  Backtest Strategy
                </Button>
                <Button variant="outline" className="w-full" disabled>
                  ML Auto-Optimize
                </Button>
                <p className="text-xs text-gray-500 pt-2">
                  Add indicators to enable actions
                </p>
              </div>
            </Card>

            {/* Phase 1 Notice */}
            <SimpleCard padding="sm">
              <div className="space-y-1">
                <p className="text-xs font-semibold text-gray-900">
                  🚧 Phase 1: Core Builder UI
                </p>
                <p className="text-xs text-gray-600">
                  This wireframe shows the planned layout. Full functionality will be implemented in Phase 1.
                </p>
              </div>
            </SimpleCard>
          </div>
        </div>
      </div>
    </main>
  );
}
