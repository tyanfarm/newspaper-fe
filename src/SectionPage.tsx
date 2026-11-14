import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from 'react'
import { elementDelay, textDone, textSchedule } from './revealTiming'
import type { Box } from './sectionLayers'
import type { Section } from './sections'
import { playerFit, type Fit } from './videoFit'

type SectionPageProps = {
  section: Section
  /** True while this page is the one on screen; each time it becomes so, it plays its entrance again. */
  active: boolean
}

const pct = (v: number) => `${v * 100}%`
const place = (b: Box) => ({ left: pct(b.x), top: pct(b.y), width: pct(b.w), height: pct(b.h) })

/**
 * The Drive player, filling its frame. Drive's player crops its picture when
 * it is small, so on small screens it is laid out larger, in the frame's
 * proportions, and shrunk to fit (videoFit.ts).
 */
function Player({ src, title }: { src: string; title: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const [fit, setFit] = useState<Fit | null>(null)

  useLayoutEffect(() => {
    const box = ref.current
    if (!box) return
    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect // layout size: unaffected by pinch-zoom
      setFit(playerFit({ width, height }))
    })
    observer.observe(box)
    return () => observer.disconnect()
  }, [])

  return (
    <div ref={ref} className="section-page__player">
      {fit && fit.width > 0 && (
        <iframe
          src={src}
          title={title}
          allow="autoplay; encrypted-media; fullscreen; picture-in-picture"
          allowFullScreen
          style={{ width: fit.width, height: fit.height, transform: `scale(${fit.scale})` }}
        />
      )}
    </div>
  )
}

/**
 * A section page rebuilt in layers: paper, then each picture in its exact
 * place on the slide, then the rest of the slide, then the text. When the page
 * comes on screen the pictures fade in one after another, top to bottom;
 * once they are all in place the text writes itself out line by line, and
 * then the video (if the page has one) appears in its frame.
 */
export default function SectionPage({ section, active }: SectionPageProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [ready, setReady] = useState(false)
  const { page } = section
  const widths = page.lines.map((l) => l.w)
  const schedule = textSchedule(widths, page.elements.length)

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
      {page.video && (
        // Appears once the text has been written out.
        <div
          className="section-page__video"
          style={{ ...place(page.video), '--delay': `${textDone(widths, page.elements.length).toFixed(3)}s` } as CSSProperties}
        >
          <img src={page.video.poster} alt="" loading="lazy" decoding="async" />
          {/* Mounted only while on screen: leaving the page stops the video. */}
          {active && section.video && <Player src={section.video} title={`Video – ${section.title}`} />}
        </div>
      )}
      {page.elements.map((el) => (
        <img
          key={el.url}
          className="section-page__el"
          src={el.url}
          alt=""
          loading="lazy"
          decoding="async"
          style={{ ...place(el), '--delay': `${elementDelay(el.reveal)}s` } as CSSProperties}
        />
      ))}
      <img className="section-page__top" src={page.top} alt={section.title} loading="lazy" decoding="async" />
      {page.lines.map((line, i) => (
        <div
          key={i}
          className="section-page__line"
          style={
            {
              ...place(line),
              '--line-start': `${schedule[i].start.toFixed(3)}s`,
              '--line-dur': `${schedule[i].duration.toFixed(3)}s`,
            } as CSSProperties
          }
        >
          {/* The whole text layer, shifted so this line's box shows through. */}
          <img
            src={page.text}
            alt=""
            loading="lazy"
            decoding="async"
            style={{ left: pct(-line.x / line.w), top: pct(-line.y / line.h), width: pct(1 / line.w), height: pct(1 / line.h) }}
          />
        </div>
      ))}
    </div>
  )
}
