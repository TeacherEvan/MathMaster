import { showNextHint, resetHints } from '../scripts/help.js';

describe('help', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="feedback"></div>';
    resetHints();
  });

  test('showNextHint writes to feedback element', () => {
    showNextHint();
    const feedback = document.getElementById('feedback');
    expect(feedback.textContent.length).toBeGreaterThan(0);
  });

  test('showNextHint advances through hints', () => {
    showNextHint();
    const first = document.getElementById('feedback').textContent;
    showNextHint();
    const second = document.getElementById('feedback').textContent;
    expect(second).not.toBe(first);
  });

  test('showNextHint eventually returns the exhausted message', () => {
    for (let i = 0; i < 10; i += 1) showNextHint();
    const feedback = document.getElementById('feedback');
    expect(feedback.textContent).toMatch(/No more hints/);
  });

  test('resetHints restarts the sequence', () => {
    showNextHint();
    showNextHint();
    resetHints();
    showNextHint();
    const feedback = document.getElementById('feedback');
    expect(feedback.textContent).toMatch(/Focus on the operator/);
  });
});
