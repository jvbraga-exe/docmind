import { postJSON, request } from '../../lib/api';
import type { Answer, Document } from './types';

export const documentsApi = {
  list: () => request<Document[]>('/api/documents'),

  upload: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return request<{ id: string; name: string; chunks: number }>('/api/documents', {
      method: 'POST',
      body: form,
    });
  },

  remove: (id: string) =>
    request<{ deleted: boolean }>(`/api/documents/${id}`, { method: 'DELETE' }),
  ask: (question: string, documentId?: string) =>
    request<Answer>(
      '/api/ask',
      postJSON({
        question,
        document_id: documentId || null,
      }),
    ),
};
