// Progressive hint system for MathMistress

let hintPointer = 0;

const hintFunctions = [
  () => showHint('Focus on the operator first.'),
  () => showHint('Rearrange terms if it helps.'),
  () => showHint('Estimate before calculating.'),
  () => showHint('Double-check your arithmetic.'),
];

function hintArea() {
  return document.getElementById('feedback');
}

function showHint(text) {
  const area = hintArea();
  if (area) {
    area.textContent = text;
    area.style.color = 'var(--ink)';
  }
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
