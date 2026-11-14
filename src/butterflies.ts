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

// Dense keyframes: the motion between them is linear. Up to BURST, each
// butterfly pops out to its spot on screen; after it, it drifts off.
const BURST = 0.25
const OFFSETS = [0, 0.04, 0.09, 0.16, BURST, 0.37, 0.5, 0.62, 0.74, 0.87, 1]

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

/** How many butterflies burst out: more on a bigger screen, so they fill it. */
export function burstSize(viewport: Size): number {
  return Math.round(Math.min(56, Math.max(26, (viewport.width * viewport.height) / 26000)))
}

/**
 * `count` butterflies bursting out of `origin` (the middle of the screen) all
 * the way round, like a firework: a quick pop out to spots all over the
 * screen, near the middle and near the edges, then each flutters side to
 * side and drifts on, slowly at first, until it is off screen.
 */
export function planFlights(origin: Point, viewport: Size, count: number, rand: () => number): Flight[] {
  const short = Math.min(viewport.width, viewport.height)
  const turn = rand() * 360 // so the flock is not the same shape every time
  const flights: Flight[] = []
  for (let i = 0; i < count; i++) {
    // Even spread round the circle, jittered within each butterfly's slice.
    const angle = ((turn + (360 * (i + 0.2 + rand() * 0.6)) / count) * Math.PI) / 180
    const dir = { x: Math.cos(angle), y: Math.sin(angle) }
    const perp = { x: -dir.y, y: dir.x }
    const size = Math.round(Math.min(130, Math.max(36, short * (0.08 + rand() * 0.09))))
    const toEdge = exitDistance(origin, dir, viewport, 0)
    const distance = exitDistance(origin, dir, viewport, size * 1.5)
    // Where the burst leaves it: anywhere from near the middle to near the edge.
    const spot = toEdge * (0.3 + 0.6 * ((i * 0.618034) % 1)) // golden-ratio steps: an even mix
    const sway = short * (0.015 + rand() * 0.03)
    const phase = rand() * Math.PI * 2
    const waves = 1 + rand() * 1.2
    const tilt = dir.x * 30 // lean into the direction of travel

    const path = OFFSETS.map((offset, k): PathPoint => {
      const along =
        offset <= BURST
          ? spot * (1 - (1 - offset / BURST) ** 2.5) // pop
          : spot + (distance - spot) * ((offset - BURST) / (1 - BURST)) ** 1.8 // drift off, gathering speed
      const side = offset === 0 ? 0 : sway * Math.sin(phase + offset * waves * Math.PI * 2) * Math.min(1, offset * 5)
      return {
        offset,
        x: k === 0 ? origin.x : Math.round((origin.x + dir.x * along + perp.x * side) * 10) / 10,
        y: k === 0 ? origin.y : Math.round((origin.y + dir.y * along + perp.y * side) * 10) / 10,
        rotate: Math.round(tilt + (k === 0 ? 0 : Math.sin(phase + k * 0.8) * 14)),
        scale: k === 0 ? 0.2 : Math.min(1, 0.45 + offset * 4),
        opacity: k === 0 ? 0 : k === OFFSETS.length - 1 ? 0.6 : 1,
      }
    })

    flights.push({
      path,
      duration: Math.round(2400 + rand() * 1000),
      delay: Math.round(rand() * 160),
      size,
      variant: (i % 2) as 0 | 1,
      flap: Math.round(110 + rand() * 70),
    })
  }
  return flights
}
