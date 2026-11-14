import bird from './assets/cover/bird.webp'
import lighthouse from './assets/cover/lighthouse.webp'
import logos from './assets/cover/logos.webp'
import ship from './assets/cover/ship.webp'
import title from './assets/cover/title.webp'
import './home.css'
import { sections } from './sections'

type HomeProps = {
  onOpen: (index: number) => void
}

export default function Home({ onOpen }: HomeProps) {
  return (
    <main className="home">
      <img className="home__deco home__bird home__bird--1" src={bird} alt="" />
      <img className="home__deco home__bird home__bird--2" src={bird} alt="" />
      <img className="home__deco home__bird home__bird--3" src={bird} alt="" />
      <img className="home__deco home__lighthouse" src={lighthouse} alt="" />
      <div className="home__sea" aria-hidden="true" />
      <img className="home__deco home__ship" src={ship} alt="" />
      <div className="home__logos">
        <img src={logos} alt="KDI Education và KDC Education" />
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
              onClick={() => onOpen(i)}
            >
              <img src={section.card} alt="" />
            </button>
          ))}
        </nav>
      </div>
    </main>
  )
}
