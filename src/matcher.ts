import { FAQ, MatchResult } from './types.js';

// TODO: implement embedding-based matcher
export async function findBestMatch(userQuestion: string, faqs: FAQ[]): Promise<MatchResult | null> {
  throw new Error('Not implemented');
}
