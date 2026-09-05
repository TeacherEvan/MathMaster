import { generateProblem, validateAnswer } from '../scripts/mathEngine.js';

describe('mathEngine', () => {
  test('generateProblem returns prompt and answer strings', () => {
    const problem = generateProblem(1);
    expect(typeof problem.prompt).toBe('string');
    expect(typeof problem.answer).toBe('string');
    expect(problem.answer.length).toBeGreaterThan(0);
  });

  test('validateAnswer accepts correct answer', () => {
    const { answer } = generateProblem(1);
    expect(validateAnswer(answer, answer)).toBe(true);
  });

  test('validateAnswer rejects incorrect answer', () => {
    const { answer } = generateProblem(1);
    const wrong = (parseInt(answer, 10) + 1).toString();
    if (wrong === answer) {
      // Edge case (e.g. answer="-1" → wrong="0"); force a different wrong answer
      expect(validateAnswer('999999', answer)).toBe(false);
    } else {
      expect(validateAnswer(wrong, answer)).toBe(false);
    }
  });

  test('validateAnswer rejects empty string', () => {
    expect(validateAnswer('', '5')).toBe(false);
  });

  test('basic level produces expected prompt shape', () => {
    for (let i = 0; i < 20; i += 1) {
      const p = generateProblem(1);
      expect(p.prompt).toMatch(/^\d+ [+-×] \d+ = \?$/);
    }
  });

  test('medium level formula is a*b - c', () => {
    for (let i = 0; i < 30; i += 1) {
      const p = generateProblem(5);
      const m = p.prompt.match(/^(\d+) × (\d+) - (\d+) = \?$/);
      expect(m).not.toBeNull();
      if (m) {
        const a = parseInt(m[1], 10);
        const b = parseInt(m[2], 10);
        const c = parseInt(m[3], 10);
        expect(p.answer).toBe((a * b - c).toString());
      }
    }
  });

  test('hard level exponent is base^exp + add', () => {
    for (let i = 0; i < 20; i += 1) {
      const p = generateProblem(10);
      const m = p.prompt.match(/^(\d+)\^(\d+) \+ (\d+) = \?$/);
      expect(m).not.toBeNull();
      if (m) {
        const base = parseInt(m[1], 10);
        const exp = parseInt(m[2], 10);
        const add = parseInt(m[3], 10);
        expect(p.answer).toBe((base ** exp + add).toString());
      }
    }
  });

  test('medium level c is always positive (1-5)', () => {
    for (let i = 0; i < 30; i += 1) {
      const p = generateProblem(5);
      const m = p.prompt.match(/^(\d+) × (\d+) - (\d+) = \?$/);
      if (m) {
        const c = parseInt(m[3], 10);
        expect(c).toBeGreaterThanOrEqual(1);
        expect(c).toBeLessThanOrEqual(5);
      }
    }
  });
});
