import { Dionysus, Quetzalcoatl, initNPCs } from '../scripts/npc.js';

describe('npc', () => {
  test('Dionysus has name, phrases, sprite', () => {
    expect(Dionysus.name).toBe('Dionysus');
    expect(Array.isArray(Dionysus.phrases)).toBe(true);
    expect(Dionysus.phrases.length).toBeGreaterThan(0);
    expect(typeof Dionysus.spritePath).toBe('string');
    expect(Dionysus.spritePath).toMatch(/dionysus\.svg$/);
  });

  test('Quetzalcoatl has name, phrases, sprite', () => {
    expect(Quetzalcoatl.name).toBe('Quetzalcoatl');
    expect(Quetzalcoatl.spritePath).toMatch(/quetzalcoatl\.svg$/);
  });

  test('NPC.randomPhrase returns a member of phrases', () => {
    const phrase = Dionysus.randomPhrase();
    expect(Dionysus.phrases).toContain(phrase);
  });

  test('initNPCs calls start on every NPC without throwing', () => {
    const cb = () => {};
    expect(() => initNPCs(cb)).not.toThrow();
    Dionysus.stop();
    Quetzalcoatl.stop();
  });

  test('NPC.start callback receives name, phrase, spritePath', (done) => {
    const orig = Dionysus.intervalRange;
    Dionysus.intervalRange = [0, 1];
    Dionysus.start((name, phrase, spritePath) => {
      try {
        expect(name).toBe('Dionysus');
        expect(Dionysus.phrases).toContain(phrase);
        expect(spritePath).toMatch(/dionysus\.svg$/);
      } finally {
        Dionysus.stop();
        Dionysus.intervalRange = orig;
        done();
      }
    });
  });
});
