/**
 * Available technical indicators for the Trade Builder platform
 * 
 * This file defines all the indicators users can select and configure
 * when building their trading algorithms.
 */

import { Indicator } from '@/lib/types';

/**
 * List of all available technical indicators
 * Each indicator includes metadata, parameters, and educational descriptions
 */
export const AVAILABLE_INDICATORS: Indicator[] = [
  {
    id: 'rsi',
    name: 'Relative Strength Index (RSI)',
    category: 'momentum',
    description: 'Measures the speed and magnitude of price changes. RSI < 30 suggests oversold, > 70 suggests overbought.',
    parameters: [
      {
        name: 'period',
        type: 'number',
        defaultValue: 14,
        min: 2,
        max: 50,
      },
    ],
  },
  {
    id: 'macd',
    name: 'MACD',
    category: 'momentum',
    description: 'Moving Average Convergence Divergence - shows relationship between two moving averages.',
    parameters: [
      {
        name: 'fastPeriod',
        type: 'number',
        defaultValue: 12,
        min: 2,
        max: 50,
      },
      {
        name: 'slowPeriod',
        type: 'number',
        defaultValue: 26,
        min: 2,
        max: 100,
      },
      {
        name: 'signalPeriod',
        type: 'number',
        defaultValue: 9,
        min: 2,
        max: 50,
      },
    ],
  },
  {
    id: 'sma',
    name: 'Simple Moving Average (SMA)',
    category: 'trend',
    description: 'Average price over a specified period. Used to identify trends.',
    parameters: [
      {
        name: 'period',
        type: 'number',
        defaultValue: 20,
        min: 2,
        max: 200,
      },
    ],
  },
  {
    id: 'ema',
    name: 'Exponential Moving Average (EMA)',
    category: 'trend',
    description: 'Weighted moving average that gives more importance to recent prices.',
    parameters: [
      {
        name: 'period',
        type: 'number',
        defaultValue: 20,
        min: 2,
        max: 200,
      },
    ],
  },
  {
    id: 'bollinger',
    name: 'Bollinger Bands',
    category: 'volatility',
    description: 'Shows price volatility using standard deviations around a moving average.',
    parameters: [
      {
        name: 'period',
        type: 'number',
        defaultValue: 20,
        min: 2,
        max: 50,
      },
      {
        name: 'standardDeviations',
        type: 'number',
        defaultValue: 2,
        min: 1,
        max: 4,
      },
    ],
  },
];

/**
 * Indicator categories for filtering and organization
 */
export const INDICATOR_CATEGORIES = [
  'momentum',
  'trend',
  'volatility',
  'volume',
] as const;

/**
 * Helper function to get an indicator by ID
 */
export function getIndicatorById(id: string): Indicator | undefined {
  return AVAILABLE_INDICATORS.find(indicator => indicator.id === id);
}

/**
 * Helper function to get indicators by category
 */
export function getIndicatorsByCategory(category: Indicator['category']): Indicator[] {
  return AVAILABLE_INDICATORS.filter(indicator => indicator.category === category);
}
