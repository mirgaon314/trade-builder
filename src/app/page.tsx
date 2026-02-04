/**
 * Home Page - Landing page for Trade Builder
 * 
 * This is the main entry point for the application, showcasing features
 * and providing navigation to all major sections.
 */

import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <section className="px-6 py-16 md:py-24">
        <div className="mx-auto max-w-6xl text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
            Trade Builder
          </h1>
          <p className="text-xl md:text-2xl text-blue-600 font-semibold mb-6">
            AI-Enhanced Trading Algorithm Platform
          </p>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto mb-8">
            The Duolingo + Spotify of trading algorithms. Build, backtest, and share ML-enhanced 
            trading strategies in a safe, educational environment.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/builder">
              <Button variant="primary" size="lg" className="w-full sm:w-auto">
                Start Building →
              </Button>
            </Link>
            <Link href="/learn">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Learn How It Works
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="px-6 py-16 bg-white">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Key Features
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature 1: ML-Enhanced Algorithms */}
            <Card>
              <div className="space-y-3">
                <div className="text-4xl">🤖</div>
                <h3 className="text-xl font-semibold text-gray-900">
                  ML-Enhanced Algorithms
                </h3>
                <p className="text-gray-600">
                  Machine learning suggests optimal indicator weights based on historical performance. 
                  Let AI help you discover winning combinations.
                </p>
                <p className="text-sm text-blue-600 font-medium">
                  Coming in Phase 4
                </p>
              </div>
            </Card>

            {/* Feature 2: Visual Algorithm Builder */}
            <Card>
              <div className="space-y-3">
                <div className="text-4xl">🎨</div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Visual Algorithm Builder
                </h3>
                <p className="text-gray-600">
                  No coding required. Select technical indicators, adjust weights with sliders, 
                  and see your strategy come to life.
                </p>
                <Link href="/builder">
                  <p className="text-sm text-blue-600 font-medium hover:underline">
                    Try the Builder →
                  </p>
                </Link>
              </div>
            </Card>

            {/* Feature 3: Community Library */}
            <Card>
              <div className="space-y-3">
                <div className="text-4xl">📚</div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Community Library
                </h3>
                <p className="text-gray-600">
                  Like Spotify playlists, discover and remix algorithms shared by other traders. 
                  Learn from proven strategies.
                </p>
                <Link href="/library">
                  <p className="text-sm text-blue-600 font-medium hover:underline">
                    Explore Library →
                  </p>
                </Link>
              </div>
            </Card>

            {/* Feature 4: Comprehensive Backtesting */}
            <Card>
              <div className="space-y-3">
                <div className="text-4xl">📊</div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Comprehensive Backtesting
                </h3>
                <p className="text-gray-600">
                  Test your strategies against years of historical data. See detailed performance 
                  metrics, trade logs, and risk analysis.
                </p>
                <Link href="/backtest">
                  <p className="text-sm text-blue-600 font-medium hover:underline">
                    View Backtesting →
                  </p>
                </Link>
              </div>
            </Card>

            {/* Feature 5: Paper Trading */}
            <Card>
              <div className="space-y-3">
                <div className="text-4xl">💰</div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Paper Trading
                </h3>
                <p className="text-gray-600">
                  Practice with virtual money in real-time markets. Build confidence before 
                  considering live trading.
                </p>
                <Link href="/paper-trading">
                  <p className="text-sm text-blue-600 font-medium hover:underline">
                    Start Paper Trading →
                  </p>
                </Link>
              </div>
            </Card>

            {/* Feature 6: Educational Tutorials */}
            <Card>
              <div className="space-y-3">
                <div className="text-4xl">🎓</div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Educational Tutorials
                </h3>
                <p className="text-gray-600">
                  Learn trading concepts through interactive tutorials. Understand not just how, 
                  but why strategies work.
                </p>
                <Link href="/learn">
                  <p className="text-sm text-blue-600 font-medium hover:underline">
                    Start Learning →
                  </p>
                </Link>
              </div>
            </Card>

            {/* Feature 7: Personality Profiling */}
            <Card>
              <div className="space-y-3">
                <div className="text-4xl">🎯</div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Personality-Based Recommendations
                </h3>
                <p className="text-gray-600">
                  Like Duolingo adapts to your learning style, we adapt to your trading personality. 
                  Get strategies that match your risk tolerance.
                </p>
                <Link href="/profile">
                  <p className="text-sm text-blue-600 font-medium hover:underline">
                    View Profile →
                  </p>
                </Link>
              </div>
            </Card>

            {/* Feature 8: Explainability */}
            <Card>
              <div className="space-y-3">
                <div className="text-4xl">💡</div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Explainable AI
                </h3>
                <p className="text-gray-600">
                  Understand why your algorithm makes each trade. Clear explanations help you 
                  learn and improve your strategies.
                </p>
                <p className="text-sm text-blue-600 font-medium">
                  Coming in Phase 10
                </p>
              </div>
            </Card>

            {/* Feature 9: Safety First */}
            <Card>
              <div className="space-y-3">
                <div className="text-4xl">🛡️</div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Safety & Education First
                </h3>
                <p className="text-gray-600">
                  Built for learning with comprehensive risk warnings, bias detection, 
                  and educational disclaimers throughout.
                </p>
                <p className="text-sm text-blue-600 font-medium">
                  Core Principle
                </p>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="px-6 py-16">
        <div className="mx-auto max-w-4xl">
          <Card className="bg-gradient-to-r from-blue-600 to-blue-700 border-0 text-white">
            <div className="text-center space-y-4 py-8">
              <h2 className="text-3xl font-bold">
                Ready to Start Building?
              </h2>
              <p className="text-lg text-blue-100 max-w-2xl mx-auto">
                Join the future of educational algorithmic trading. Learn, experiment, and 
                optimize your strategies in a safe environment.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
                <Link href="/builder">
                  <Button variant="secondary" size="lg" className="w-full sm:w-auto bg-white text-blue-600 hover:bg-blue-50">
                    Build Your First Algorithm
                  </Button>
                </Link>
                <a
                  href="https://github.com/mirgaon314/trade-builder"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Button variant="outline" size="lg" className="w-full sm:w-auto border-white text-white hover:bg-blue-800">
                    View on GitHub
                  </Button>
                </a>
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 border-t border-gray-200">
        <div className="mx-auto max-w-6xl">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Trade Builder</h3>
              <p className="text-sm text-gray-600">
                An educational trading platform for learning algorithmic trading 
                in a safe, ML-enhanced environment.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/builder" className="text-gray-600 hover:text-blue-600">Algorithm Builder</Link></li>
                <li><Link href="/backtest" className="text-gray-600 hover:text-blue-600">Backtesting</Link></li>
                <li><Link href="/library" className="text-gray-600 hover:text-blue-600">Community Library</Link></li>
                <li><Link href="/learn" className="text-gray-600 hover:text-blue-600">Learn</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Resources</h3>
              <ul className="space-y-2 text-sm">
                <li><a href="https://github.com/mirgaon314/trade-builder" className="text-gray-600 hover:text-blue-600">GitHub</a></li>
                <li><Link href="/learn" className="text-gray-600 hover:text-blue-600">Documentation</Link></li>
                <li><a href="https://github.com/mirgaon314/trade-builder/blob/main/ROADMAP.md" className="text-gray-600 hover:text-blue-600">Roadmap</a></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-6 border-t border-gray-200 text-center text-sm text-gray-600">
            <p>
              ⚠️ <strong>Educational Purpose Only</strong> - Not financial advice. 
              Always do your own research before making investment decisions.
            </p>
            <p className="mt-2">
              Built by a CS student learning full-stack development. Open source under MIT License.
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}
