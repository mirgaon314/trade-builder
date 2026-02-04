/**
 * Profile Page
 * 
 * User profile and trading personality dashboard.
 * Features coming in Phase 7:
 * - Trading personality profile
 * - Behavioral analysis
 * - Risk tolerance assessment
 * - Performance history
 * - Achievement badges
 * - Personalized recommendations
 */

import Link from 'next/link';
import { Card } from '@/components/ui/Card';

export default function ProfilePage() {
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Your Profile</h1>
            <p className="mt-2 text-gray-600">
              Understand your trading personality and track your progress
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
          description="Phase 7: Trading Personality Analysis"
        >
          <div className="space-y-4">
            <p className="text-gray-700">
              The personality profiling system will be introduced in Phase 7. You'll be able to:
            </p>
            
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>Discover your trading personality type (conservative, moderate, aggressive)</li>
              <li>Understand your behavioral patterns and biases</li>
              <li>Take a risk tolerance assessment</li>
              <li>Receive personalized algorithm recommendations</li>
              <li>Track your learning progress and achievements</li>
              <li>Compare your style with community averages</li>
              <li>Set and monitor personal trading goals</li>
            </ul>
            
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                <strong>Coming in Phase 7</strong> - Personality analysis will help you trade in alignment with your natural tendencies
              </p>
            </div>
          </div>
        </Card>

        {/* Personality Types Preview */}
        <div className="grid md:grid-cols-3 gap-6">
          <Card title="🛡️ Conservative">
            <div className="space-y-2 text-sm text-gray-600">
              <p><strong>Focus:</strong> Capital preservation</p>
              <p><strong>Style:</strong> Long-term, low volatility</p>
              <p><strong>Indicators:</strong> Moving averages, trend following</p>
            </div>
          </Card>
          
          <Card title="⚖️ Moderate">
            <div className="space-y-2 text-sm text-gray-600">
              <p><strong>Focus:</strong> Balanced growth</p>
              <p><strong>Style:</strong> Swing trading, medium-term</p>
              <p><strong>Indicators:</strong> RSI, MACD, support/resistance</p>
            </div>
          </Card>
          
          <Card title="🚀 Aggressive">
            <div className="space-y-2 text-sm text-gray-600">
              <p><strong>Focus:</strong> Maximum returns</p>
              <p><strong>Style:</strong> Day trading, high frequency</p>
              <p><strong>Indicators:</strong> Volume, momentum, volatility</p>
            </div>
          </Card>
        </div>

        {/* Adaptive Learning Note */}
        <Card title="Adaptive Learning">
          <p className="text-gray-700">
            Like Duolingo adapts to your learning style, Trade Builder will learn from your 
            preferences and suggest strategies that match your personality. The platform analyzes 
            your indicator choices, holding periods, and risk decisions to provide personalized guidance.
          </p>
        </Card>
      </div>
    </main>
  );
}
