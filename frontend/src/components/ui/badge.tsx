import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../lib/utils';

const variants = cva(
  'inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium',
  {
    variants: {
      variant: {
        neutral: 'border-slate-200 bg-slate-50 text-slate-600',
        success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
        destructive: 'border-rose-200 bg-rose-50 text-rose-700',
        warning: 'border-amber-200 bg-amber-50 text-amber-700',
      },
    },
    defaultVariants: { variant: 'neutral' },
  },
);

type Props = React.HTMLAttributes<HTMLSpanElement> & VariantProps<typeof variants>;

export function Badge({ variant, className, ...props }: Props) {
  return <span className={cn(variants({ variant }), className)} {...props} />;
}
