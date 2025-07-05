import { generateProblem } from '../scripts/mathEngine.js';

describe('Performance', () => {
  test('generateProblem 1000 iterations under 50ms', () => {
    const start = performance.now();
    for (let i = 0; i < 1000; i += 1) {
      generateProblem(5);
    }
    const duration = performance.now() - start;
    expect(duration).toBeLessThan(50);
  });
});