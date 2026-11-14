import { useEffect, useRef, useState, type CSSProperties } from 'react'
import type { Section } from './sections'

type SectionPageProps = {
  section: Section
  /** True while this page is the one on screen; each time it becomes so, its pictures appear again. */
  active: boolean
}

const pct = (v: number) => `${v * 100}%`

/**
 * A section page rebuilt in layers: paper, then each picture in its exact
 * place on the slide, then the text on top. When the page comes on screen
 * the pictures fade in one after another, top to bottom.
 */
export default function SectionPage({ section, active }: SectionPageProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [ready, setReady] = useState(false)
  const { page } = section

  useEffect(() => {
    const root = ref.current
    if (!active || !root) return
    let cancelled = false
    // Start only once every layer can be painted, or pictures would pop in as they download.
    const images = [...root.querySelectorAll('img')]
    Promise.all(images.map((img) => img.decode().catch(() => undefined))).then(() => {
      if (!cancelled) setReady(true)
    })
    return () => {
      cancelled = true
      setReady(false) // replay next time this page is shown
    }
  }, [active])

  return (
    <div
      ref={ref}
      className={`section-page swiper-zoom-target${active && ready ? ' is-revealed' : ''}`}
      style={{ '--ratio': page.width / page.height } as CSSProperties}
    >
      <img className="section-page__base" src={page.base} alt="" loading="lazy" decoding="async" />
      {page.elements.map((el) => (
        <img
          key={el.url}
          className="section-page__el"
          src={el.url}
          alt=""
          loading="lazy"
          decoding="async"
          style={{ left: pct(el.x), top: pct(el.y), width: pct(el.w), height: pct(el.h), '--reveal': el.reveal } as CSSProperties}
        />
      ))}
      <img className="section-page__top" src={page.top} alt={section.title} loading="lazy" decoding="async" />
    </div>
  )
}
