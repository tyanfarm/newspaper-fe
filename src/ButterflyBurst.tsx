import { useEffect, useRef } from 'react'
import butterfly1 from './assets/effects/butterfly-1.webp'
import butterfly2 from './assets/effects/butterfly-2.webp'
import { burstSize, planFlights, type Point } from './butterflies'

export type Burst = {
  /** Changes for every new burst, so opening the same section twice replays it. */
  id: number
  /** Viewport point the butterflies burst out of (the middle of the screen). */
  origin: Point
}

const DRAWINGS = [butterfly1, butterfly2]

/**
 * A flock of butterflies bursting out of `burst.origin`, with a soft flash
 * of light, and fluttering off screen all round. Rendered inside the popup
 * <dialog> so they fly over its dark backdrop. Built imperatively: a few
 * dozen short-lived nodes, no React re-renders mid-flight.
 */
export default function ButterflyBurst({ burst }: { burst: Burst | null }) {
  const layerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const layer = layerRef.current
    if (!burst || !layer || matchMedia('(prefers-reduced-motion: reduce)').matches) return

    const viewport = { width: window.innerWidth, height: window.innerHeight }
    const glow = document.createElement('div')
    glow.className = 'butterflies__glow'
    glow.style.left = `${burst.origin.x}px`
    glow.style.top = `${burst.origin.y}px`
    layer.append(glow)
    const flash = glow.animate(
      [
        { opacity: 0, transform: 'translate(-50%, -50%) scale(0.2)' },
        { opacity: 1, transform: 'translate(-50%, -50%) scale(0.8)', offset: 0.25 },
        { opacity: 0, transform: 'translate(-50%, -50%) scale(1.6)' },
      ],
      { duration: 900, easing: 'ease-out', fill: 'both' },
    )
    flash.finished.then(
      () => glow.remove(),
      () => glow.remove(),
    )

    const flights = planFlights(burst.origin, viewport, burstSize(viewport), Math.random)
    const animations = flights.map((flight) => {
      const el = document.createElement('div')
      el.className = 'butterfly'
      el.style.width = `${flight.size}px`
      el.style.setProperty('--flap', `${flight.flap}ms`)
      const img = document.createElement('img')
      img.src = DRAWINGS[flight.variant]
      img.alt = ''
      el.append(img)
      layer.append(el)

      const half = flight.size / 2
      const animation = el.animate(
        flight.path.map((p) => ({
          offset: p.offset,
          opacity: p.opacity,
          transform: `translate(${p.x - half}px, ${p.y - half}px) rotate(${p.rotate}deg) scale(${p.scale})`,
        })),
        { duration: flight.duration, delay: flight.delay, fill: 'both' }, // the path itself eases out
      )
      animation.finished.then(
        () => el.remove(),
        () => el.remove(),
      )
      return animation
    })
    return () => [flash, ...animations].forEach((a) => a.cancel())
  }, [burst])

  return <div ref={layerRef} className="butterflies" aria-hidden="true" />
}
