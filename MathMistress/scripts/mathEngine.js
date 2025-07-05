// Simple math problem generator for MathMistress
// No persistence – everything lives in memory.

export function generateProblem(level = 1) {
  // Increase difficulty by level: 1-3 basic, 4-6 medium, 7+ hard
  if (level < 4) return basicArithmetic();
  if (level < 7) return mediumArithmetic();
  return hardArithmetic();
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
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
    answer: (Math.pow(base, exp) + add).toString(),
  };
}

export function validateAnswer(input, expected) {
  return input === expected;
}