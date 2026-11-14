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
const src = (name: string) => art[`./assets/cover/${name}.webp`]

// Every piece keeps its box from the design (design/update-v1/homepage-design.webp,
// in its pixels; scripts/build-cover-scene.py). The page hands those numbers to
// CSS as custom properties, and home.css scales and anchors each group (header,
// cards, sea) to suit the screen.
type Box = { x: number; y: number; w: number; h: number }
const vars = (v: Record<string, number | string>) => v as CSSProperties

// Lighthouse and its light sit a little lower than the waves on wide screens
// (home.css: --lh-drop), so they can be drawn larger without meeting the title.
const LIGHTHOUSE_GROUP = new Set(['lighthouse', 'beam', 'sparkle'])
const seaVars = (el: Box) => vars({ '--x': el.x, '--b': scene.height - el.y - el.h, '--w': el.w })

const board = scene.board
const cardBox = Object.fromEntries(scene.cards.map((c) => [c.name, c]))
const pct = (n: number) => `${(n * 100).toFixed(3)}%`

const waveRow = scene.sea.find((el) => el.name === 'waves')!
// Copies of the waves carry the sea on to the right edge of wide screens.
const EXTRA_WAVES = 3
const WAVE_OVERLAP = 300 // design px each copy tucks under the previous one

const LOGO_ALT: Record<string, string> = { 'logo-kdc': 'KDC Education', 'logo-kdi': 'KDI Education' }

export default function Home({ onOpen }: HomeProps) {
  const backCloud = scene.clouds.find((c) => c.name === 'cloud-3')!
  return (
    <main className="home">
      <div className="home__sky" aria-hidden="true">
        {scene.clouds
          .filter((c) => c !== backCloud)
          .map((c) => (
            <img
              key={c.name}
              className={`home__cloud home__cloud--${c.name}`}
              src={src(c.name)}
              alt=""
              style={vars({ '--x': c.x, '--y': c.y, '--w': c.w })}
            />
          ))}
      </div>

      <div className="home__sea" aria-hidden="true">
        <img className="home__sea-el home__sea-el--lighthouse-group home__sea-el--cloud" src={src(backCloud.name)} alt="" style={seaVars(backCloud)} />
        {scene.sea.map((el) => (
          <img
            key={el.name}
            className={`home__sea-el home__sea-el--${el.name}${LIGHTHOUSE_GROUP.has(el.name) ? ' home__sea-el--lighthouse-group' : ''}`}
            src={src(el.name)}
            alt=""
            style={{ ...seaVars(el), zIndex: el.z + 1 }}
          />
        ))}
        <div className="home__waves-more" style={{ ...seaVars({ ...waveRow, x: waveRow.x + waveRow.w - WAVE_OVERLAP }), zIndex: waveRow.z + 1 }}>
          {Array.from({ length: EXTRA_WAVES }, (_, i) => (
            <img key={i} src={waves} alt="" style={{ scale: i % 2 ? '1' : '-1 1' }} />
          ))}
        </div>
      </div>

      <img className="home__bird home__bird--1" src={bird1} alt="" />
      <img className="home__bird home__bird--2" src={bird2} alt="" />
      <img className="home__bird home__bird--3" src={bird3} alt="" />
      <img className="home__bird home__bird--4" src={bird1} alt="" />

      <h1 className="home__heading" style={vars({ '--x': scene.title.x, '--y': scene.title.y, '--w': scene.title.w })}>
        <img className="home__title" src={title} alt="Thắp sáng – Số 2011. Ấn phẩm của L2T NEWS" fetchPriority="high" />
      </h1>

      <div className="home__logos" style={vars({ '--right': scene.width - Math.max(...scene.logos.map((l) => l.x + l.w)) })}>
        {scene.logos.map((l) => (
          <img key={l.name} className={`home__logo home__logo--${l.name}`} src={src(l.name)} alt={LOGO_ALT[l.name]} style={vars({ '--w': l.w })} />
        ))}
      </div>

      <nav className="home__board" aria-label="Các mục" style={vars({ '--x': board.x, '--y': board.y, '--w': board.w, '--h': board.h })}>
        {sections.map((section, i) => {
          const c = cardBox[section.slug]
          return (
            <button
              key={section.slug}
              type="button"
              className="home__card"
              aria-label={section.title}
              data-slug={section.slug}
              style={{ left: pct((c.x - board.x) / board.w), top: pct((c.y - board.y) / board.h), width: pct(c.w / board.w) }}
              onClick={(e) => {
                const r = e.currentTarget.getBoundingClientRect()
                onOpen(i, { x: r.left + r.width / 2, y: r.top + r.height / 2 })
              }}
            >
              <img src={section.card} alt="" />
            </button>
          )
        })}
      </nav>
    </main>
  )
}
