import cardCungNhauLon from './assets/cover/card-cung-nhau-lon.webp'
import cardLoiNgo from './assets/cover/card-loi-ngo.webp'
import cardLoiTriAn from './assets/cover/card-loi-tri-an.webp'
import cardVungKyUc from './assets/cover/card-vung-ky-uc.webp'
import { pageLayers, type PageLayers } from './sectionLayers'
import type { SectionSlug } from './sectionSlugs'

export { sectionIndexFromHash, type SectionSlug } from './sectionSlugs'

export type Section = {
  slug: SectionSlug
  title: string
  /** Full page shown in the popup, in layers so its pictures can appear one by one. */
  page: PageLayers
  /** Card shown on the home page. */
  card: string
  /** Embeddable player for the video in the page's video frame (page.video). */
  video?: string
}

export const sections: readonly Section[] = [
  { slug: 'loi-ngo', title: 'Lời ngỏ', page: pageLayers('loi-ngo'), card: cardLoiNgo },
  { slug: 'vung-ky-uc', title: 'Vùng ký ức', page: pageLayers('vung-ky-uc'), card: cardVungKyUc },
  { slug: 'cung-nhau-lon', title: 'Cùng nhau lớn', page: pageLayers('cung-nhau-lon'), card: cardCungNhauLon },
  {
    slug: 'loi-tri-an',
    title: 'Lời tri ân',
    page: pageLayers('loi-tri-an'),
    card: cardLoiTriAn,
    // Google Drive's player (the file is shared with anyone who has the link).
    video: 'https://drive.google.com/file/d/1yMIOFIyrzB10CqOBtbtwl5qKan0Owy_F/preview',
  },
]
