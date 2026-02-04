/**
 * Learn Page
 * 
 * Educational hub with tutorials and resources for learning trading algorithms.
 * Features coming in Phase 9:
 * - Interactive tutorials
 * - Technical indicator explanations
 * - Step-by-step guides
 * - Video content
 * - Glossary
 * - Best practices
 */

import Link from 'next/link';
import { Card } from '@/components/ui/Card';

export default function LearnPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Learn</h1>
            <p className="mt-2 text-gray-600">
              Master trading algorithms through interactive tutorials and guides
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
          description="Phase 9: Tutorials & Educational Content"
        >
          <div className="space-y-4">
            <p className="text-gray-700">
              The educational content hub is being developed in Phase 9. You'll have access to:
            </p>
            
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>Interactive tutorials for each technical indicator</li>
              <li>Step-by-step guides for building your first algorithm</li>
              <li>Video walkthroughs and animated explanations</li>
              <li>Comprehensive glossary of trading terms</li>
              <li>Best practices and common pitfalls to avoid</li>
              <li>Achievement system to track your learning progress</li>
              <li>Quizzes and challenges to test your knowledge</li>
            </ul>
            
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                <strong>Coming in Phase 9</strong> - Educational content will be added throughout development
              </p>
            </div>
          </div>
        </Card>

        {/* Learning Path Preview */}
        <div className="grid md:grid-cols-2 gap-6">
          <Card title="📚 Beginner Path">
            <div className="space-y-2 text-sm text-gray-600">
              <p>• What are technical indicators?</p>
              <p>• Understanding RSI and MACD</p>
              <p>• Building your first algorithm</p>
              <p>• Backtesting basics</p>
            </div>
          </Card>
          
          <Card title="🚀 Advanced Path">
            <div className="space-y-2 text-sm text-gray-600">
              <p>• ML-weighted indicator strategies</p>
              <p>• Risk management techniques</p>
              <p>• Portfolio optimization</p>
              <p>• Avoiding overfitting</p>
            </div>
          </Card>
        </div>

        {/* Educational Philosophy */}
        <Card title="Learning Philosophy">
          <p className="text-gray-700">
            Like Duolingo makes language learning accessible, Trade Builder makes algorithmic trading 
            educational and approachable. Every feature includes clear explanations, helpful tooltips, 
            and educational content to help you understand not just <em>how</em> to use the platform, 
            but <em>why</em> certain strategies work.
          </p>
        </Card>
      </div>
    </main>
  );
}
