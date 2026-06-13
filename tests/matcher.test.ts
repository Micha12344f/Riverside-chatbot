import { describe, it, expect } from 'vitest';
import { findBestMatch } from '../src/matcher.js';
import faqs from '../faqs.json' assert { type: 'json' };

describe('matcher', () => {
  it('should be implemented', () => {
    expect(findBestMatch).toBeDefined();
  });
});
