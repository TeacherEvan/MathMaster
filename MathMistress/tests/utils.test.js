import { randomInt } from '../scripts/utils.js';

describe('utils', () => {
  test('randomInt is integer', () => {
    for (let i = 0; i < 50; i += 1) {
      const v = randomInt(1, 5);
      expect(Number.isInteger(v)).toBe(true);
    }
  });

  test('randomInt respects bounds (inclusive)', () => {
    for (let i = 0; i < 100; i += 1) {
      const v = randomInt(3, 7);
      expect(v).toBeGreaterThanOrEqual(3);
      expect(v).toBeLessThanOrEqual(7);
    }
  });

  test('randomInt same min/max returns that value', () => {
    expect(randomInt(5, 5)).toBe(5);
  });
});
