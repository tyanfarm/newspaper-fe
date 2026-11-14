// Flight plans for the butterflies that burst out when a section opens.
// Pure (no DOM) so it can be unit-tested in plain Node.

export type Point = { x: number; y: number }
export type Size = { width: number; height: number }

export type PathPoint = Point & {
  /** 0 → 1 along the flight (a Web Animations keyframe offset). */
  offset: number
  rotate: number
  scale: number
  opacity: number
}

export type Flight = {
  path: PathPoint[]
  /** ms */
  duration: number
  /** ms before this butterfly sets off */
  delay: number
  /** px, the drawn width */
  size: number
  /** which of the two butterfly drawings */
  variant: 0 | 1
  /** ms for one wing beat */
  flap: number
}

const OFFSETS = [0, 0.12, 0.28, 0.44, 0.6, 0.78, 1]

/** Deterministic 0–1 random numbers (mulberry32), for repeatable flocks. */
export function seededRandom(seed: number): () => number {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/** Distance from p along unit vector d until it is `margin` past the viewport edge. */
function exitDistance(p: Point, d: Point, viewport: Size, margin: number): number {
  const tx = d.x > 0 ? (viewport.width + margin - p.x) / d.x : d.x < 0 ? (-margin - p.x) / d.x : Infinity
  const ty = d.y > 0 ? (viewport.height + margin - p.y) / d.y : d.y < 0 ? (-margin - p.y) / d.y : Infinity
  return Math.min(tx, ty)
}

/**
 * `count` butterflies leaving `origin`, fanned over the upper half-circle
 * (a little below horizontal at each end), each fluttering side to side
 * and flying until it is off screen.
 */
export function planFlights(origin: Point, viewport: Size, count: number, rand: () => number): Flight[] {
  const short = Math.min(viewport.width, viewport.height)
  const flights: Flight[] = []
  for (let i = 0; i < count; i++) {
    // Even fan from 200° to 340° (screen y points down, so this is upward), jittered.
    const fan = 200 + (140 * (i + 0.5)) / count + (rand() - 0.5) * (120 / count)
    const angle = (fan * Math.PI) / 180
    const dir = { x: Math.cos(angle), y: Math.sin(angle) }
    const perp = { x: -dir.y, y: dir.x }
    const size = Math.round(Math.min(120, Math.max(36, short * (0.08 + rand() * 0.06))))
    const distance = exitDistance(origin, dir, viewport, size * 1.5)
    const sway = short * (0.03 + rand() * 0.05)
    const phase = rand() * Math.PI * 2
    const waves = 1.2 + rand() * 1.3
    const tilt = dir.x * 25 // lean into the direction of travel

    const path = OFFSETS.map((offset, k): PathPoint => {
      // Ease out: quick launch, then a lazier drift off screen.
      const along = distance * (1 - (1 - offset) ** 1.6)
      const side = offset === 0 ? 0 : sway * Math.sin(phase + offset * waves * Math.PI * 2) * Math.min(1, offset * 4)
      return {
        offset,
        x: k === 0 ? origin.x : Math.round((origin.x + dir.x * along + perp.x * side) * 10) / 10,
        y: k === 0 ? origin.y : Math.round((origin.y + dir.y * along + perp.y * side) * 10) / 10,
        rotate: Math.round(tilt + (k === 0 ? 0 : Math.sin(phase + k) * 14)),
        scale: k === 0 ? 0.35 : 1,
        opacity: k === 0 ? 0 : k === OFFSETS.length - 1 ? 0.6 : 1,
      }
    })

    flights.push({
      path,
      duration: Math.round(1900 + rand() * 900),
      delay: Math.round(rand() * 260),
      size,
      variant: (i % 2) as 0 | 1,
      flap: Math.round(110 + rand() * 70),
    })
  }
  return flights
}
