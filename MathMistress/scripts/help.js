// Progressive hint system for MathMistress

let hintPointer = 0;
const hintArea = document.getElementById('feedback');
// Basic generic hints; could be expanded per-level.
const hintFunctions = [
  () => showHint('Focus on the operator first.'),
  () => showHint('Rearrange terms if it helps.'),
  () => showHint('Estimate before calculating.'),
  () => showHint('Double-check your arithmetic.'),
];

function showHint(text) {
  hintArea.textContent = text;
  hintArea.style.color = 'var(--ink)';
}

export function showNextHint() {
  if (hintPointer < hintFunctions.length) {
    hintFunctions[hintPointer++]();
  } else {
    showHint('No more hints. Trust in your inner philosopher.');
  }
}

export function resetHints() {
  hintPointer = 0;
}