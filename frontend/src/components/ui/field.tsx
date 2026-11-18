import * as React from 'react';
import { cn } from '../../lib/utils';

const classes =
  'w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 outline-none placeholder:text-slate-400 focus:border-[var(--accent)] focus:ring-2 focus:ring-[color:var(--accent-soft)] disabled:bg-slate-50 disabled:text-slate-400';

export function Input({ className, ...props }: React.ComponentProps<'input'>) {
  return <input className={cn(classes, 'h-9', className)} {...props} />;
}

export function Textarea({ className, ...props }: React.ComponentProps<'textarea'>) {
  return (
    <textarea className={cn(classes, 'min-h-24 resize-y leading-relaxed', className)} {...props} />
  );
}

export function Select({ className, ...props }: React.ComponentProps<'select'>) {
  return <select className={cn(classes, 'h-9', className)} {...props} />;
}

export function Field({
  label,
  htmlFor,
  hint,
  children,
}: {
  label: string;
  htmlFor: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-medium text-slate-700" htmlFor={htmlFor}>
        {label}
      </label>
      {children}
      {hint && <p className="text-xs text-slate-500">{hint}</p>}
    </div>
  );
}
