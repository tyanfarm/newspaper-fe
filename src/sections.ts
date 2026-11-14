import cardCungNhauLon from './assets/cover/card-cung-nhau-lon.webp'
import cardLoiNgo from './assets/cover/card-loi-ngo.webp'
import cardLoiTriAn from './assets/cover/card-loi-tri-an.webp'
import cardVungKyUc from './assets/cover/card-vung-ky-uc.webp'
import pageCungNhauLon from './assets/sections/cung-nhau-lon.webp'
import pageLoiNgo from './assets/sections/loi-ngo.webp'
import pageLoiTriAn from './assets/sections/loi-tri-an.webp'
import pageVungKyUc from './assets/sections/vung-ky-uc.webp'
import type { SectionSlug } from './sectionSlugs'

export { sectionIndexFromHash, type SectionSlug } from './sectionSlugs'

export type Section = {
  slug: SectionSlug
  title: string
  /** Full page shown in the popup. */
  page: string
  /** Card shown on the home page. */
  card: string
}

export const sections: readonly Section[] = [
  { slug: 'loi-ngo', title: 'Lời ngỏ', page: pageLoiNgo, card: cardLoiNgo },
  { slug: 'vung-ky-uc', title: 'Vùng ký ức', page: pageVungKyUc, card: cardVungKyUc },
  { slug: 'cung-nhau-lon', title: 'Cùng nhau lớn', page: pageCungNhauLon, card: cardCungNhauLon },
  { slug: 'loi-tri-an', title: 'Lời tri ân', page: pageLoiTriAn, card: cardLoiTriAn },
]
