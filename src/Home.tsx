import type { CSSProperties } from 'react'
import bird1 from './assets/cover/bird-1.webp'
import bird2 from './assets/cover/bird-2.webp'
import bird3 from './assets/cover/bird-3.webp'
import title from './assets/cover/title.webp'
import waves from './assets/cover/waves.webp'
import type { Point } from './butterflies'
import scene from './coverScene.json'
import './home.css'
import { sections } from './sections'

type HomeProps = {
  /** `origin`: centre of the clicked card, where the butterflies fly out from. */
  onOpen: (index: number, origin: Point) => void
}

const art = import.meta.glob<string>('./assets/cover/*.webp', { eager: true, import: 'default' })

// The sea scene keeps slide 1's arrangement: every piece is placed in slide-1
// pixels (scripts/build-cover-scene.py), scaled by --k, with the slide's bottom
// edge on the page's bottom edge. The logos keep their distance from the
// slide's right edge, so they stay in the bottom-right corner on wide screens.
const RIGHT_ANCHORED: Record<string, string> = { 'logo-kdi': 'KDI Education', 'logo-kdc': 'KDC Education' }
const k = (px: number) => `calc(${px} * var(--k))`
const kLogo = (px: number) => `calc(${px} * var(--k-logo))` // logos may be drawn larger on phones

const waveRow = scene.elements.find((el) => el.name === 'waves')!
// Copies of the right-hand waves carry the sea on to the right edge of wide screens.
const EXTRA_WAVES = 3
const WAVE_OVERLAP = 300 // slide px each copy tucks under the previous one

export default function Home({ onOpen }: HomeProps) {
  return (
    <main className="home">
      <img className="home__deco home__bird home__bird--1" src={bird1} alt="" />
      <img className="home__deco home__bird home__bird--2" src={bird2} alt="" />
      <img className="home__deco home__bird home__bird--3" src={bird3} alt="" />

      <div className="home__scene">
        {scene.elements.map((el) => {
          const label = RIGHT_ANCHORED[el.name]
          const scale = label ? kLogo : k
          const style: CSSProperties = {
            [label ? 'right' : 'left']: scale(label ? scene.width - el.x - el.w : el.x),
            bottom: scale(scene.height - el.y - el.h),
            width: scale(el.w),
            zIndex: el.z,
          }
          return (
            <img
              key={el.name}
              className={`home__scene-el home__scene-el--${el.name}`}
              src={art[`./assets/cover/${el.name}.webp`]}
              alt={label ?? ''}
              style={style}
            />
          )
        })}
        <div
          className="home__waves-more"
          aria-hidden="true"
          style={{
            left: k(waveRow.x + waveRow.w - WAVE_OVERLAP),
            bottom: k(scene.height - waveRow.y - waveRow.h),
            zIndex: waveRow.z,
          }}
        >
          {Array.from({ length: EXTRA_WAVES }, (_, i) => (
            <img
              key={i}
              src={waves}
              alt=""
              style={{ width: k(waveRow.w), marginLeft: i ? k(-WAVE_OVERLAP) : 0, scale: i % 2 ? '1' : '-1 1' }}
            />
          ))}
        </div>
      </div>

      <div className="home__center">
        <h1 className="home__heading">
          <img className="home__title" src={title} alt="Thắp sáng – Số 2011" fetchPriority="high" />
          <span className="home__subtitle">
            Ấn phẩm của <span className="n">L</span>
            <span className="r">2</span>
            <span className="n">T</span> <span className="r">N</span>
            <span className="n">E</span>
            <span className="r">W</span>
            <span className="n">S</span>
          </span>
        </h1>

        <nav className="home__cards" aria-label="Các mục">
          {sections.map((section, i) => (
            <button
              key={section.slug}
              type="button"
              className="home__card"
              aria-label={section.title}
              data-slug={section.slug}
              onClick={(e) => {
                const r = e.currentTarget.getBoundingClientRect()
                onOpen(i, { x: r.left + r.width / 2, y: r.top + r.height / 2 })
              }}
            >
              <img src={section.card} alt="" />
            </button>
          ))}
        </nav>
      </div>
    </main>
  )
}
