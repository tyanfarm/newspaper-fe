import { useEffect, useRef } from 'react'
import butterfly1 from './assets/effects/butterfly-1.webp'
import butterfly2 from './assets/effects/butterfly-2.webp'
import { planFlights, type Point } from './butterflies'

export type Burst = {
  /** Changes for every new burst, so opening the same section twice replays it. */
  id: number
  /** Viewport point the butterflies fly out from (the card that was clicked). */
  origin: Point
}

const DRAWINGS = [butterfly1, butterfly2]
const COUNT = 12

/**
 * Butterflies fluttering out from `burst.origin` and off screen. Rendered
 * inside the popup <dialog> so they fly over its dark backdrop. Built
 * imperatively: a dozen short-lived nodes, no React re-renders mid-flight.
 */
export default function ButterflyBurst({ burst }: { burst: Burst | null }) {
  const layerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const layer = layerRef.current
    if (!burst || !layer || matchMedia('(prefers-reduced-motion: reduce)').matches) return

    const viewport = { width: window.innerWidth, height: window.innerHeight }
    const animations = planFlights(burst.origin, viewport, COUNT, Math.random).map((flight) => {
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
        { duration: flight.duration, delay: flight.delay, easing: 'ease-in-out', fill: 'both' },
      )
      animation.finished.then(
        () => el.remove(),
        () => el.remove(),
      )
      return animation
    })
    return () => animations.forEach((a) => a.cancel())
  }, [burst])

  return <div ref={layerRef} className="butterflies" aria-hidden="true" />
}
