// Shared helpers for MathMistress modules.
// Centralised so we don't duplicate utilities across engine and NPC.

export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
