import { formatTND } from '@/lib/api';

describe('formatTND', () => {
  it('formats integer TND values with thousand separators', () => {
    expect(formatTND(1234567)).toBe('1,234,567 TND');
  });

  it('rounds fractional TND values', () => {
    expect(formatTND(99.999)).toBe('100 TND');
  });

  it('handles zero', () => {
    expect(formatTND(0)).toBe('0 TND');
  });
});
