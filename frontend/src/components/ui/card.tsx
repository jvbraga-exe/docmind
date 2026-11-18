import * as React from 'react';
import { cn } from '../../lib/utils';

type Props = React.HTMLAttributes<HTMLDivElement>;

export function Card({ className, ...props }: Props) {
  return (
    <section
      className={cn(
        'rounded-xl border border-slate-200 bg-white shadow-[0_2px_6px_rgba(15,23,42,0.025)]',
        className,
      )}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: Props) {
  return (
    <div
      className={cn(
        'flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 px-5 py-4',
        className,
      )}
      {...props}
    />
  );
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2
      className={cn('text-sm font-semibold tracking-tight text-slate-900', className)}
      {...props}
    />
  );
}

export function CardDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn('mt-1 text-xs leading-relaxed text-slate-500', className)} {...props} />;
}

export function CardContent({ className, ...props }: Props) {
  return <div className={cn('p-5', className)} {...props} />;
}
