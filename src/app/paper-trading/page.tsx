/**
 * Paper Trading Page
 * 
 * Virtual trading dashboard for testing algorithms with fake money.
 * Features coming in Phase 6:
 * - Real-time paper trading
 * - Virtual portfolio management
 * - Position tracking
 * - Performance analytics
 * - Order execution simulation
 */

import Link from 'next/link';
import { Card } from '@/components/ui/Card';

export default function PaperTradingPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Paper Trading</h1>
            <p className="mt-2 text-gray-600">
              Practice trading with virtual money in real-time markets
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
          description="Phase 6: Virtual Trading (Paper Trading)"
        >
          <div className="space-y-4">
            <p className="text-gray-700">
              Paper trading will be available in Phase 6. This feature will allow you to:
            </p>
            
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>Create virtual portfolios with simulated starting capital</li>
              <li>Execute your algorithms in real-time with live market data</li>
              <li>Track positions, P&L, and portfolio performance</li>
              <li>Practice order types (market, limit, stop-loss)</li>
              <li>Test multiple algorithms simultaneously</li>
              <li>Learn without risking real money</li>
              <li>Build confidence before considering live trading</li>
            </ul>
            
            <div className="pt-4 border-t border-gray-200 bg-amber-50 -mx-4 -mb-4 px-4 py-3 rounded-b-xl">
              <p className="text-sm text-amber-900">
                <strong>⚠️ Educational Purpose Only</strong> - Paper trading is for learning and testing. 
                Past performance does not guarantee future results.
              </p>
            </div>
          </div>
        </Card>

        {/* Feature Preview */}
        <div className="grid md:grid-cols-3 gap-6">
          <Card title="Virtual Portfolio">
            <p className="text-sm text-gray-600">
              Start with $100,000 in virtual cash and see how your strategies perform
            </p>
          </Card>
          
          <Card title="Real-Time Execution">
            <p className="text-sm text-gray-600">
              Your algorithms run against live market data, simulating real trading conditions
            </p>
          </Card>
          
          <Card title="Risk-Free Learning">
            <p className="text-sm text-gray-600">
              Make mistakes, learn, and improve without any financial risk
            </p>
          </Card>
        </div>
      </div>
    </main>
  );
}
