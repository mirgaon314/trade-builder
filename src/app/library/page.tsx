/**
 * Community Library Page
 * 
 * This page will showcase algorithms shared by the community.
 * Features coming in Phase 8:
 * - Browse public algorithms
 * - Search and filter by category, performance, popularity
 * - View algorithm details and performance
 * - Fork/remix algorithms
 * - Rate and review algorithms
 */

import Link from 'next/link';
import { Card } from '@/components/ui/Card';

export default function LibraryPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Algorithm Library</h1>
            <p className="mt-2 text-gray-600">
              Discover and learn from community-shared trading algorithms
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
          description="Phase 8: Community & Sharing"
        >
          <div className="space-y-4">
            <p className="text-gray-700">
              The community library is planned for Phase 8. This feature will enable:
            </p>
            
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>Browse algorithms shared by other traders</li>
              <li>Filter by strategy type, performance, and risk level</li>
              <li>View detailed algorithm configurations and backtesting results</li>
              <li>Fork and customize algorithms for your own use</li>
              <li>Rate and review algorithms you've tried</li>
              <li>Follow top contributors and get notified of new strategies</li>
              <li>Share your own algorithms with the community</li>
            </ul>
            
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                <strong>Coming in Phase 8</strong> - Community features will be added once core functionality is stable
              </p>
            </div>
          </div>
        </Card>

        {/* Vision Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          <Card title="Like Spotify Playlists">
            <p className="text-sm text-gray-600">
              Discover curated collections of algorithms organized by strategy type and market conditions
            </p>
          </Card>
          
          <Card title="Learn by Example">
            <p className="text-sm text-gray-600">
              See how experienced traders configure their indicators and understand their reasoning
            </p>
          </Card>
          
          <Card title="Remix & Improve">
            <p className="text-sm text-gray-600">
              Start with proven strategies and customize them to match your trading personality
            </p>
          </Card>
        </div>
      </div>
    </main>
  );
}
