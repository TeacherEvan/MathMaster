import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const PROJECT_ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const GAME_FILE = path.join(PROJECT_ROOT, 'assets', 'web', 'game.js');

describe('Project sanity checks', () => {
  test('game.js has valid JavaScript syntax', () => {
    // `node --check` exits with a non-zero code on syntax errors.
    expect(() => execSync(`node --check ${GAME_FILE}`)).not.toThrow();
  });

  test('game.js has no leftover merge-conflict markers', () => {
    const content = fs.readFileSync(GAME_FILE, 'utf8');
    // Typical Git conflict markers
    const conflictMarkerRegex = /<<<<<<<|=======|>>>>>>>/;
    expect(conflictMarkerRegex.test(content)).toBe(false);

    // Any accidental branch/commit label artifacts that previously caused issues
    expect(content.includes('cursor/fix-memory-leak-in-resize-event-listener')).toBe(false);
  });
});
