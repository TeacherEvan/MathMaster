import { generateProblem, validateAnswer } from './mathEngine.js';
import { Dionysus, Quetzalcoatl, initNPCs } from './npc.js';
import { showNextHint, resetHints } from './help.js';

// DOM elements
const splash = document.getElementById('splash');
const beginBtn = document.getElementById('beginBtn');
const gameSection = document.getElementById('game');
const promptEl = document.getElementById('prompt');
const answerInput = document.getElementById('answerInput');
const submitBtn = document.getElementById('submitBtn');
const helpBtn = document.getElementById('helpBtn');
const feedbackEl = document.getElementById('feedback');
const focusMeter = document.getElementById('focusMeter');
const npcOverlay = document.getElementById('npcOverlay');

let currentProblem = null;
let level = 1;
let focus = 100;
let gameActive = false;

function startGame() {
  splash.classList.add('hidden');
  gameSection.classList.remove('hidden');
  gameActive = true;
  level = 1;
  focus = 100;
  focusMeter.value = focus;
  resetHints();
  nextProblem();
  initNPCs(onNPCDistraction);
}

function nextProblem() {
  currentProblem = generateProblem(level);
  promptEl.textContent = currentProblem.prompt;
  answerInput.value = '';
  feedbackEl.textContent = '';
}

function onSubmit() {
  if (!gameActive) return;
  const userAnswer = answerInput.value.trim();
  if (userAnswer === '') return;
  const isCorrect = validateAnswer(userAnswer, currentProblem.answer);
  if (isCorrect) {
    feedbackEl.textContent = 'Correct!';
    feedbackEl.style.color = 'green';
    level += 1;
    nextProblem();
  } else {
    feedbackEl.textContent = 'Try again';
    feedbackEl.style.color = 'var(--accent)';
    // Drain focus due to error
    drainFocus(5);
  }
}

function onHelp() {
  showNextHint();
  // Using help drains focus slightly
  drainFocus(2);
}

function drainFocus(amount) {
  focus = Math.max(0, focus - amount);
  focusMeter.value = focus;
  if (focus === 0) {
    endGame('Focus lost! Reload to try again.');
  }
}

function onNPCDistraction(message) {
  npcOverlay.textContent = message;
  npcOverlay.classList.add('show');
  setTimeout(() => npcOverlay.classList.remove('show'), 2000);
  drainFocus(10);
}

function endGame(msg) {
  gameActive = false;
  feedbackEl.textContent = msg;
}

beginBtn.addEventListener('click', startGame);
submitBtn.addEventListener('click', onSubmit);
answerInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') onSubmit();
});
helpBtn.addEventListener('click', onHelp);
