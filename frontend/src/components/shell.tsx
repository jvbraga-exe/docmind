import type { ReactNode } from 'react';
import { Badge } from './ui/badge';

export function Shell({
  app,
  name,
  eyebrow,
  title,
  subtitle,
  actions,
  children,
}: {
  app: string;
  name: string;
  eyebrow: string;
  title: string;
  subtitle: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div data-app={app} className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-4 sm:px-8">
          <a href="/" className="flex items-center gap-3 text-sm font-semibold tracking-tight">
            <span className="flex size-9 items-center justify-center rounded-xl bg-[var(--accent)] text-white shadow-sm">
              <span className="text-sm font-bold">D</span>
            </span>
            <span>
              <span className="block text-sm font-semibold tracking-tight">{name}</span>
              <span className="mt-0.5 block text-[11px] font-normal text-slate-500">
                Busca em documentos
              </span>
            </span>
          </a>
          <Badge>PDF e TXT</Badge>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-5 py-8 sm:px-8 sm:py-11">
        <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-[var(--accent)]">
              {eyebrow}
            </p>
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{title}</h1>
            <p className="mt-2 max-w-xl text-sm text-slate-500">{subtitle}</p>
          </div>
          {actions}
        </div>
        {children}
      </main>
      <footer className="mx-auto max-w-7xl px-5 pb-8 text-xs text-slate-500 sm:px-8">
        {name} · Respostas geradas por IA podem conter erros. Confira as citações no documento
        original.
      </footer>
    </div>
  );
}
