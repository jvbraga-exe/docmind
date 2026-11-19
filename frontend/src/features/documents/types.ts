export type Document = {
  id: string;
  name: string;
  chunks: number;
  created_at: string;
};

export type Source = {
  number: number;
  document: string;
  page: number;
  text: string;
  score?: number;
};

export type Answer = {
  answer: string;
  sources: Source[];
};
