import type { ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';

export function Feedback({ error, message }: { error?: string; message?: string }) {
  if (!error && !message) return null;
  return (
    <div
      role="status"
      aria-live="polite"
      className={`mt-3 flex items-start gap-2 rounded-md border p-3 text-xs ${error ? 'border-rose-200 bg-rose-50 text-rose-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700'}`}
    >
      {error && <AlertCircle className="size-4 shrink-0" aria-hidden="true" />}
      {error || message}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-32 items-center justify-center px-4 py-8 text-center text-sm leading-relaxed text-slate-400">
      {children}
    </div>
  );
}
