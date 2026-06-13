export interface FAQ {
  id: number;
  question: string;
  answer: string;
}

export interface MatchResult {
  faq: FAQ;
  score: number;
}
