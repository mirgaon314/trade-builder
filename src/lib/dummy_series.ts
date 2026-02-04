export type LinePoint = { time: number; value: number };

export function makeDummySeries(days = 200, base = 100): LinePoint[] {
  const now = Math.floor(Date.now() / 1000);
  const out: LinePoint[] = [];
  let price = base;
  for (let i = days - 1; i >= 0; i--) {
    const t = now - i * 86400;           // one point per day
    const drift = 0.05;                  // gentle up-trend
    const noise = Math.sin(i / 7) * 0.6; // wiggle
    price = price + drift + noise;
    out.push({ time: t, value: Number(price.toFixed(2)) });
  }
  return out;
}