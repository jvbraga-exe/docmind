import { useCallback, useEffect, useState } from 'react';
import { errorMessage } from '../../lib/api';
import { documentsApi } from './api';
import type { Answer, Document } from './types';

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const refresh = useCallback(async () => {
    try {
      const items = await documentsApi.list();
      setDocuments(items);
      setSelectedId((current) =>
        items.some((item) => item.id === current) ? current : items[0]?.id || '',
      );
      setError('');
    } catch (failure) {
      setError(errorMessage(failure));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function upload(file: File): Promise<boolean> {
    if (file.size > 8 * 1024 * 1024) {
      setError('O arquivo deve ter até 8 MB.');
      return false;
    }
    setUploading(true);
    setError('');
    setMessage('');
    try {
      const result = await documentsApi.upload(file);
      setMessage(`${result.name} indexado com ${result.chunks} trechos.`);
      await refresh();
      return true;
    } catch (failure) {
      setError(errorMessage(failure));
      return false;
    } finally {
      setUploading(false);
    }
  }

  async function remove(document: Document) {
    if (!window.confirm(`Excluir ${document.name} e seus trechos?`)) return;
    try {
      await documentsApi.remove(document.id);
      setAnswer(null);
      setMessage('Documento excluído.');
      await refresh();
    } catch (failure) {
      setError(errorMessage(failure));
    }
  }

  async function ask(question: string): Promise<void> {
    setSearching(true);
    setAnswer(null);
    setError('');
    setMessage('');
    try {
      setAnswer(await documentsApi.ask(question.trim(), selectedId));
    } catch (failure) {
      setError(errorMessage(failure));
    } finally {
      setSearching(false);
    }
  }

  return {
    documents,
    selectedId,
    setSelectedId,
    answer,
    loading,
    uploading,
    searching,
    error,
    message,
    refresh,
    upload,
    remove,
    ask,
  };
}
