// Simple math problem generator for MathMistress
// No persistence – everything lives in memory.

import { randomInt } from './utils.js';

export function generateProblem(level = 1) {
  if (level < 4) return basicArithmetic();
  if (level < 7) return mediumArithmetic();
  return hardArithmetic();
}

function basicArithmetic() {
  const a = randomInt(1, 10);
  const b = randomInt(1, 10);
  const ops = [
    { symbol: '+', fn: (x, y) => x + y },
    { symbol: '-', fn: (x, y) => x - y },
    { symbol: '×', fn: (x, y) => x * y },
  ];
  const op = ops[randomInt(0, ops.length - 1)];
  return {
    prompt: `${a} ${op.symbol} ${b} = ?`,
    answer: op.fn(a, b).toString(),
  };
}

function mediumArithmetic() {
  const a = randomInt(2, 12);
  const b = randomInt(2, 9);
  const c = randomInt(1, 5);
  return {
    prompt: `${a} × ${b} - ${c} = ?`,
    answer: (a * b - c).toString(),
  };
}

function hardArithmetic() {
  const base = randomInt(2, 5);
  const exp = randomInt(2, 3);
  const add = randomInt(1, 15);
  return {
    prompt: `${base}^${exp} + ${add} = ?`,
    answer: (base ** exp + add).toString(),
  };
}

export function validateAnswer(input, expected) {
  return input === expected;
}
