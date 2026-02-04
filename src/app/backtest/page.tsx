/**
 * Backtesting Page
 * 
 * This page will allow users to test their trading algorithms against historical data.
 * Features coming in Phase 3:
 * - Historical data selection (date range, symbol)
 * - Algorithm selection
 * - Backtesting execution
 * - Performance metrics display
 * - Trade log visualization
 */

import Link from 'next/link';
import { Card } from '@/components/ui/Card';

export default function BacktestPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Backtesting</h1>
            <p className="mt-2 text-gray-600">
              Test your algorithms against historical market data
            </p>
          </div>
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-700 underline text-sm"
          >
            ← Back to Home
          </Link>
        </div>

        {/* Coming Soon Notice */}
        <Card
          title="Under Construction"
          description="Phase 3: Backtesting Engine"
        >
          <div className="space-y-4">
            <p className="text-gray-700">
              The backtesting engine is currently under development. Once complete, you'll be able to:
            </p>
            
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>Select any stock symbol and date range for testing</li>
              <li>Run your custom algorithms against historical data</li>
              <li>View detailed performance metrics (returns, Sharpe ratio, max drawdown)</li>
              <li>Analyze trade-by-trade execution logs</li>
              <li>Compare multiple algorithms side-by-side</li>
              <li>Export results for further analysis</li>
            </ul>
            
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                <strong>Coming in Phase 3</strong> - Expected delivery: 2-3 weeks after Phase 1 completion
              </p>
            </div>
          </div>
        </Card>

        {/* Feature Preview Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          <Card title="Historical Data">
            <p className="text-sm text-gray-600">
              Access years of historical price data for comprehensive backtesting
            </p>
          </Card>
          
          <Card title="Performance Metrics">
            <p className="text-sm text-gray-600">
              Detailed analytics including returns, risk metrics, and statistical analysis
            </p>
          </Card>
          
          <Card title="Trade Visualization">
            <p className="text-sm text-gray-600">
              See exactly where your algorithm would have entered and exited positions
            </p>
          </Card>
        </div>
      </div>
    </main>
  );
}
