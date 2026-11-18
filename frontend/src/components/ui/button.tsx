import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { LoaderCircle } from 'lucide-react';
import { cn } from '../../lib/utils';

const variants = cva(
  'inline-flex h-9 items-center justify-center gap-2 whitespace-nowrap rounded-md px-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-[var(--accent)] text-white hover:brightness-90',
        outline: 'border border-slate-200 bg-white text-slate-800 hover:bg-slate-50',
        ghost: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
        destructive: 'bg-red-600 text-white hover:bg-red-700',
      },
      size: { default: 'h-9 px-3', sm: 'h-8 px-2.5 text-xs', icon: 'h-8 w-8 px-0' },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  },
);

type ButtonProps = React.ComponentProps<'button'> &
  VariantProps<typeof variants> & {
    asChild?: boolean;
    busy?: boolean;
  };

export function Button({
  asChild = false,
  busy = false,
  variant,
  size,
  className,
  children,
  disabled,
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : 'button';
  return (
    <Component
      className={cn(variants({ variant, size, className }))}
      disabled={disabled || busy}
      {...props}
    >
      {busy ? <LoaderCircle className="size-4 animate-spin" aria-hidden="true" /> : children}
    </Component>
  );
}
