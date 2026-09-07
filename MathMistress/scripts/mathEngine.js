// Simple math problem generator for MathMistress
// No persistence – everything lives in memory.

import { randomInt } from './utils.js';

export function generateProblem(level = 1) {
  if (level < 4) return basicArithmetic();
  if (level < 7) return mediumArithmetic();
  if (level < 13) return hardArithmetic();
  return fractionsArithmetic();
}

function basicArithmetic() {
  const a = randomInt(1, 10);
  const b = randomInt(1, 10);
  const ops = [
    { symbol: '+', fn: (x, y) => x + y },
    { symbol: '-', fn: (x, y) => x - y },
    { symbol: '\u00d7', fn: (x, y) => x * y },
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
    prompt: `${a} \u00d7 ${b} - ${c} = ?`,
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

// Fractions tier — added 2026-09-07 per BLUEPRINT §4 (deferred in last PR).
// Produces "a/c + b/d = ?" with a reduced-form answer "x/y".
// Two allowlisted forms keep the input predictable and tests deterministic.
function fractionsArithmetic() {
  const forms = [
    () => sameDenominatorAdd(),
    () => likeDenomHalfAdd(),
  ];
  return forms[randomInt(0, forms.length - 1)]();
}

// Form A: identical denominators — easiest, deterministic test path.
function sameDenominatorAdd() {
  const denom = randomInt(2, 8);
  const a = randomInt(1, denom - 1);
  const b = randomInt(1, denom - 1);
  return {
    prompt: `${a}/${denom} + ${b}/${denom} = ?`,
    answer: reduce(a + b, denom),
  };
}

// Form B: halves + quarters (always simplifies cleanly).
function likeDenomHalfAdd() {
  const denom = 4;
  const a = randomInt(1, 3);
  const b = randomInt(1, 3);
  return {
    prompt: `${a}/2 + ${b}/${denom} = ?`,
    answer: reduce(a * 2 + b, denom),
  };
}

// Euclidean gcd — used to reduce fractions.
function gcd(a, b) {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y !== 0) {
    const t = y;
    y = x % y;
    x = t;
  }
  return x || 1;
}

// Reduce n/d to lowest terms; returns "<n>/<d>".
function reduce(n, d) {
  const g = gcd(n, d);
  return `${n / g}/${d / g}`;
}

export function validateAnswer(input, expected) {
  return input === expected;
}
