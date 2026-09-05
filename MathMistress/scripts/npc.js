// NPC logic for MathMistress
// Provides timed distractions to drain focus.

import { randomInt } from './utils.js';

class NPC {
  constructor(name, phrases, intervalRange, spritePath = null) {
    this.name = name;
    this.phrases = phrases;
    this.intervalRange = intervalRange; // [min, max] ms
    this.spritePath = spritePath;
    this.timerId = null;
  }

  start(callback) {
    const schedule = () => {
      const delay = randomInt(this.intervalRange[0], this.intervalRange[1]);
      this.timerId = setTimeout(() => {
        const phrase = this.randomPhrase();
        callback(this.name, phrase, this.spritePath);
        schedule();
      }, delay);
    };
    schedule();
  }

  stop() {
    clearTimeout(this.timerId);
  }

  randomPhrase() {
    return this.phrases[randomInt(0, this.phrases.length - 1)];
  }
}

export const Dionysus = new NPC('Dionysus', [
  'Wine break?',
  'Dance with satyrs!',
  'Logic is overrated!',
], [5000, 12000], 'assets/img/dionysus.svg');

export const Quetzalcoatl = new NPC('Quetzalcoatl', [
  'Feathered wisdom...',
  'Cycles of time whisper.',
  'Seek the golden ratio.',
], [7000, 15000], 'assets/img/quetzalcoatl.svg');

const npcs = [Dionysus, Quetzalcoatl];

export function initNPCs(callback) {
  npcs.forEach((npc) => npc.start(callback));
}
