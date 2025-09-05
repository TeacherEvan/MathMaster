import { generateProblem, validateAnswer } from '../scripts/mathEngine.js';

describe('mathEngine', () => {
  test('generateProblem returns prompt and answer strings', () => {
    const problem = generateProblem(1);
    expect(typeof problem.prompt).toBe('string');
    expect(typeof problem.answer).toBe('string');
  });

  test('validateAnswer accepts correct answer', () => {
    const { answer } = generateProblem(1);
    expect(validateAnswer(answer, answer)).toBe(true);
  });

  test('validateAnswer rejects incorrect answer', () => {
    const { answer } = generateProblem(1);
    // Ensure different answer
    const wrong = (parseInt(answer, 10) + 1).toString();
    expect(validateAnswer(wrong, answer)).toBe(false);
  });
});
