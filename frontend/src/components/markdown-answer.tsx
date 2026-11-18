import type { ReactNode } from 'react';

function cleanMarkdown(value: string): string {
  const entities: Record<string, string> = {
    '&nbsp;': ' ',
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',
    '&apos;': "'",
  };

  return value
    .replace(/(?:【|\[)\s*(\d+)(?:\s*[†‡]\s*L?\d+(?:\s*[-–]\s*L?\d+)?)?\s*(?:】|\])/gi, '[$1]')
    .replace(/\\([\\`*_{}\[\]()#+\-.!>])/g, '$1')
    .replace(/&#(x[\da-f]+|\d+);/gi, (_, code: string) => {
      const point =
        code[0].toLowerCase() === 'x'
          ? Number.parseInt(code.slice(1), 16)
          : Number.parseInt(code, 10);
      return Number.isFinite(point) ? String.fromCodePoint(point) : _;
    })
    .replace(
      /&(?:nbsp|amp|lt|gt|quot|apos);/gi,
      (entity) => entities[entity.toLowerCase()] ?? entity,
    )
    .replace(/[\u00a0\u202f]/g, ' ')
    .replace(/\\[ \t]*\r?\n/g, '\n')
    .replace(/[ \t]+\r?\n/g, '\n')
    .trim();
}

function inlineContent(text: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*|(?<!\*)\*[^*]+\*(?!\*)|`[^`]+`|\[\d+\])/g);
  return parts.filter(Boolean).map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={index}>{part.slice(1, -1)}</em>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code className="answer-code" key={index}>
          {part.slice(1, -1)}
        </code>
      );
    }
    if (/^\[\d+\]$/.test(part)) {
      return (
        <span className="answer-citation" key={index}>
          {part}
        </span>
      );
    }
    return part;
  });
}

export function MarkdownAnswer({ value }: { value: string }) {
  const lines = cleanMarkdown(value).split('\n');
  const blocks: ReactNode[] = [];
  let paragraph: string[] = [];
  let list: string[] = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    blocks.push(<p key={`p-${blocks.length}`}>{inlineContent(paragraph.join(' '))}</p>);
    paragraph = [];
  };

  const flushList = () => {
    if (!list.length) return;
    blocks.push(
      <ul key={`ul-${blocks.length}`}>
        {list.map((item, index) => (
          <li key={index}>{inlineContent(item)}</li>
        ))}
      </ul>,
    );
    list = [];
  };

  for (const line of lines) {
    const item = line.match(/^\s*[-*+]\s+(.+)$/);
    if (item) {
      flushParagraph();
      list.push(item[1]);
    } else if (!line.trim()) {
      flushParagraph();
      flushList();
    } else {
      flushList();
      paragraph.push(line.trim());
    }
  }

  flushParagraph();
  flushList();

  return <div className="markdown-answer">{blocks}</div>;
}
