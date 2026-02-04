/**
 * Card Component
 * 
 * A container component for sections and content blocks.
 * Provides consistent styling and optional header/footer sections.
 */

import { cn } from '@/lib/utils';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  description?: string;
  footer?: React.ReactNode;
}

export function Card({ children, className, title, description, footer }: CardProps) {
  return (
    <div className={cn('rounded-xl border border-gray-200 bg-white shadow-sm', className)}>
      {(title || description) && (
        <div className="border-b border-gray-200 px-6 py-4">
          {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
          {description && <p className="mt-1 text-sm text-gray-600">{description}</p>}
        </div>
      )}
      
      <div className="px-6 py-4">
        {children}
      </div>
      
      {footer && (
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 rounded-b-xl">
          {footer}
        </div>
      )}
    </div>
  );
}

/**
 * Simple card variant without header/footer sections
 */
export interface SimpleCardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function SimpleCard({ children, className, padding = 'md' }: SimpleCardProps) {
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };
  
  return (
    <div className={cn('rounded-xl border border-gray-200 bg-white shadow-sm', paddingStyles[padding], className)}>
      {children}
    </div>
  );
}
