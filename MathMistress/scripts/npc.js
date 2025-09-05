// NPC logic for MathMistress
// Provides timed distractions to drain focus.

class NPC {
  constructor(name, phrases, intervalRange) {
    this.name = name;
    this.phrases = phrases;
    this.intervalRange = intervalRange; // [min, max] ms
    this.timerId = null;
  }

  start(callback) {
    // callback receives phrase string
    const schedule = () => {
      const delay = randomInt(this.intervalRange[0], this.intervalRange[1]);
      this.timerId = setTimeout(() => {
        const phrase = this.randomPhrase();
        callback(`${this.name}: ${phrase}`);
        schedule(); // schedule next one
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

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export const Dionysus = new NPC('Dionysus', [
  'Wine break?',
  'Dance with satyrs!',
  'Logic is overrated!',
], [5000, 12000]);

export const Quetzalcoatl = new NPC('Quetzalcoatl', [
  'Feathered wisdom...',
  'Cycles of time whisper.',
  'Seek the golden ratio.',
], [7000, 15000]);

const npcs = [Dionysus, Quetzalcoatl];

export function initNPCs(callback) {
  npcs.forEach((npc) => npc.start(callback));
}
