export function dateTime(value?: string | null): string {
  return value
    ? new Date(value).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
    : '—';
}

// Reservado para uso futuro — atualmente sem importações ativas no projeto.
export function timeOnly(value?: string | null): string {
  return value
    ? new Date(value).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    : '—';
}
