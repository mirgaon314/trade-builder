/**
 * Common utility functions for the Trade Builder application
 * 
 * These helpers are used throughout the app for formatting, calculations,
 * and common operations.
 */

/**
 * Clamp a number between min and max values
 * @param value - The number to clamp
 * @param min - Minimum allowed value
 * @param max - Maximum allowed value
 * @returns The clamped value
 * 
 * @example
 * clamp(150, 0, 100) // returns 100
 * clamp(-10, 0, 100) // returns 0
 * clamp(50, 0, 100)  // returns 50
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Format a number as a percentage
 * @param value - The decimal value to format (e.g., 0.1234)
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted percentage string
 * 
 * @example
 * formatPercent(0.1234)    // returns "12.34%"
 * formatPercent(0.1234, 1) // returns "12.3%"
 * formatPercent(-0.05)     // returns "-5.00%"
 */
export function formatPercent(value: number, decimals: number = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format a number as currency
 * @param value - The number to format
 * @param currency - Currency code (default: 'USD')
 * @returns Formatted currency string
 * 
 * @example
 * formatCurrency(1234.56)       // returns "$1,234.56"
 * formatCurrency(1234.56, 'EUR') // returns "€1,234.56"
 */
export function formatCurrency(value: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(value);
}

/**
 * Conditionally join class names together
 * Useful for combining Tailwind CSS classes with conditions
 * @param classes - Array of class names or conditionals
 * @returns Combined class string
 * 
 * @example
 * cn('px-4', 'py-2', isActive && 'bg-blue-500')
 * // returns "px-4 py-2 bg-blue-500" if isActive is true
 * // returns "px-4 py-2" if isActive is false
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Format a large number with k, M, B suffixes
 * @param value - The number to format
 * @returns Formatted string with suffix
 * 
 * @example
 * formatCompactNumber(1234)      // returns "1.2K"
 * formatCompactNumber(1234567)   // returns "1.2M"
 * formatCompactNumber(1234567890) // returns "1.2B"
 */
export function formatCompactNumber(value: number): string {
  const formatter = new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 1,
  });
  return formatter.format(value);
}

/**
 * Calculate the sum of weights for validation
 * @param weights - Array of weight values
 * @returns Sum of all weights
 */
export function sumWeights(weights: number[]): number {
  return weights.reduce((sum, weight) => sum + weight, 0);
}

/**
 * Normalize weights to sum to 100
 * @param weights - Array of weight values
 * @returns Normalized weights that sum to 100
 * 
 * @example
 * normalizeWeights([50, 50, 50]) // returns [33.33, 33.33, 33.33]
 */
export function normalizeWeights(weights: number[]): number[] {
  const sum = sumWeights(weights);
  if (sum === 0) return weights.map(() => 0);
  return weights.map(weight => (weight / sum) * 100);
}

/**
 * Generate a unique ID
 * @returns A unique identifier string
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Format a date to a readable string
 * @param date - Date to format
 * @param includeTime - Whether to include time (default: false)
 * @returns Formatted date string
 * 
 * @example
 * formatDate(new Date('2024-01-15')) // returns "Jan 15, 2024"
 */
export function formatDate(date: Date, includeTime: boolean = false): string {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  };
  
  if (includeTime) {
    options.hour = '2-digit';
    options.minute = '2-digit';
  }
  
  return new Intl.DateTimeFormat('en-US', options).format(date);
}
