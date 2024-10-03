export function getRandomNumber(min: number, max: number): number {
  // Generates a random number between min (inclusive) and max (exclusive)
    return Math.floor(Math.random() * (max - min) ) + min;
  }