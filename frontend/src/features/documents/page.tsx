import { useRef, useState, type FormEvent } from 'react';
import {
  BookOpen,
  FileSearch,
  FileText,
  RefreshCw,
  Search,
  Sparkles,
  Trash2,
  UploadCloud,
} from 'lucide-react';
import { MarkdownAnswer } from '../../components/markdown-answer';
import { Shell } from '../../components/shell';
import { Button } from '../../components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Field, Select, Textarea } from '../../components/ui/field';
import { Empty, Feedback } from '../../components/states';
import { dateTime } from '../../lib/format';
import { useDocuments } from './use-documents';

export function DocumentsPage() {
  const library = useDocuments();
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState('');
  const fileInput = useRef<HTMLInputElement>(null);

  async function upload(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    if (await library.upload(file)) {
      setFile(null);
      if (fileInput.current) fileInput.current.value = '';
    }
  }

  function ask(event: FormEvent) {
    event.preventDefault();
    void library.ask(question);
  }

  return (
    <Shell
      app="docmind"
      name="DocMind"
      eyebrow="Biblioteca de documentos"
      title="Encontre respostas nos seus arquivos"
      subtitle="Adicione PDFs ou textos e consulte o conteúdo com referências às páginas originais."
    >
      <Feedback error={library.error} message={library.message} />

      <div className="grid items-start gap-6 lg:grid-cols-[310px_minmax(0,1fr)]">
        <aside className="space-y-5 lg:sticky lg:top-6">
          <Card className="overflow-hidden">
            <CardHeader>
              <div className="flex items-center gap-3">
                <span className="section-icon">
                  <BookOpen aria-hidden="true" />
                </span>
                <div>
                  <CardTitle>Seus documentos</CardTitle>
                  <CardDescription>
                    {library.documents.length} arquivos na biblioteca
                  </CardDescription>
                </div>
              </div>
              <Button
                size="icon"
                variant="ghost"
                title="Atualizar biblioteca"
                aria-label="Atualizar biblioteca"
                onClick={() => void library.refresh()}
              >
                <RefreshCw className={`size-4 ${library.loading ? 'animate-spin' : ''}`} />
              </Button>
            </CardHeader>
            <CardContent className="space-y-5">
              <form className="space-y-3" onSubmit={upload}>
                <label htmlFor="document-file" className="upload-zone">
                  <span className="upload-icon">
                    <UploadCloud aria-hidden="true" />
                  </span>
                  <span className="text-sm font-semibold text-slate-800">
                    {file?.name || 'Escolher um arquivo'}
                  </span>
                  <span className="text-xs text-slate-500">PDF ou TXT, até 8 MB</span>
                </label>
                <input
                  ref={fileInput}
                  type="file"
                  id="document-file"
                  className="sr-only"
                  accept=".pdf,.txt"
                  onChange={(event) => setFile(event.target.files?.[0] || null)}
                />
                <Button type="submit" className="w-full" disabled={!file} busy={library.uploading}>
                  <UploadCloud className="size-4" /> Indexar documento
                </Button>
              </form>

              <div className="border-t border-slate-100 pt-4">
                <div className="mb-3 flex items-center justify-between">
                  <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Arquivos indexados
                  </h2>
                  <Badge>{library.documents.length}</Badge>
                </div>
                {library.documents.length ? (
                  <ul className="space-y-2">
                    {library.documents.map((document) => (
                      <li key={document.id}>
                        <div
                          className={`document-row ${library.selectedId === document.id ? 'document-row-active' : ''}`}
                        >
                          <FileText
                            className="mt-0.5 size-4 shrink-0 text-[var(--accent)]"
                            aria-hidden="true"
                          />
                          <button
                            type="button"
                            className="min-w-0 flex-1 text-left"
                            onClick={() => library.setSelectedId(document.id)}
                            aria-pressed={library.selectedId === document.id}
                          >
                            <span
                              className="block truncate text-sm font-medium text-slate-800"
                              title={document.name}
                            >
                              {document.name}
                            </span>
                            <span className="mt-1 block text-xs text-slate-500">
                              {document.chunks} trechos · {dateTime(document.created_at)}
                            </span>
                          </button>
                          <Button
                            size="icon"
                            variant="ghost"
                            title={`Excluir ${document.name}`}
                            aria-label={`Excluir ${document.name}`}
                            onClick={() => void library.remove(document)}
                          >
                            <Trash2 className="size-4" />
                          </Button>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <Empty>
                    {library.loading ? 'Carregando arquivos…' : 'Sua biblioteca está vazia.'}
                  </Empty>
                )}
              </div>
            </CardContent>
          </Card>
          <p className="px-1 text-xs leading-relaxed text-slate-500">
            Os trechos recuperados são enviados ao provedor de IA quando você pede uma resposta
            gerada.
          </p>
        </aside>

        <main className="space-y-5">
          <Card className="overflow-hidden">
            <CardHeader>
              <div className="flex items-center gap-3">
                <span className="section-icon">
                  <Search aria-hidden="true" />
                </span>
                <div>
                  <CardTitle>Faça uma pergunta</CardTitle>
                  <CardDescription>
                    Busque um detalhe ou peça um resumo do documento.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form className="space-y-4" onSubmit={ask}>
                <Field label="Buscar em" htmlFor="document-filter">
                  <Select
                    id="document-filter"
                    value={library.selectedId}
                    onChange={(event) => library.setSelectedId(event.target.value)}
                  >
                    <option value="">Todos os documentos</option>
                    {library.documents.map((document) => (
                      <option key={document.id} value={document.id}>
                        {document.name}
                      </option>
                    ))}
                  </Select>
                </Field>
                <Field label="Sua pergunta" htmlFor="document-question">
                  <Textarea
                    id="document-question"
                    required
                    minLength={4}
                    maxLength={500}
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="Ex.: Quais foram minhas responsabilidades na última empresa?"
                    rows={3}
                  />
                </Field>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="inline-flex items-center gap-2 text-xs text-slate-500">
                    <Sparkles className="size-3.5 text-[var(--accent)]" aria-hidden="true" />
                    As respostas incluem referências para você conferir.
                  </p>
                  <Button
                    type="submit"
                    disabled={!library.documents.length || library.searching}
                    busy={library.searching}
                  >
                    <Search className="size-4" /> Consultar documentos
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {library.answer ? (
            <Card className="overflow-hidden">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <span className="section-icon section-icon-answer">
                    <Sparkles aria-hidden="true" />
                  </span>
                  <div>
                    <CardTitle>Resposta</CardTitle>
                    <CardDescription>Confira as citações nas fontes abaixo.</CardDescription>
                  </div>
                </div>
                <Badge variant={library.answer.mode === 'generated' ? 'success' : 'warning'}>
                  {library.answer.mode === 'generated' ? 'Resposta gerada' : 'Busca nos trechos'}
                </Badge>
              </CardHeader>
              <CardContent className="answer-content">
                <MarkdownAnswer value={library.answer.answer} />

                <section className="sources-section" aria-labelledby="sources-title">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div>
                      <h3 id="sources-title" className="text-sm font-semibold text-slate-800">
                        Fontes consultadas
                      </h3>
                      <p className="mt-1 text-xs text-slate-500">
                        {library.answer.sources.length} trechos do documento
                      </p>
                    </div>
                  </div>
                  {library.answer.sources.length ? (
                    <div className="space-y-2">
                      {library.answer.sources.map((source) => (
                        <article
                          className="source-item"
                          key={`${source.document}-${source.page}-${source.number}`}
                        >
                          <div className="source-item-heading">
                            <span className="source-number">[{source.number}]</span>
                            <span className="min-w-0 flex-1 truncate">{source.document}</span>
                            <Badge>Página {source.page}</Badge>
                          </div>
                          <p>{source.text || 'O trecho não foi retornado pela busca.'}</p>
                        </article>
                      ))}
                    </div>
                  ) : (
                    <Empty>Nenhum trecho relevante foi encontrado.</Empty>
                  )}
                </section>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent>
                <div className="empty-search">
                  <span className="empty-search-icon">
                    <FileSearch aria-hidden="true" />
                  </span>
                  <strong>
                    {library.searching ? 'Lendo seus documentos…' : 'Sua resposta aparece aqui'}
                  </strong>
                  <p>
                    {library.documents.length
                      ? 'Escolha um documento, faça uma pergunta e consulte as fontes usadas.'
                      : 'Adicione um PDF ou TXT à biblioteca para começar.'}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    </Shell>
  );
}
