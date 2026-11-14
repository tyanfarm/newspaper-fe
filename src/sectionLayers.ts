import type { SectionSlug } from './sectionSlugs'

// Each section page is rebuilt from its Canva elements in layers
// (scripts/build-section-layers.py writes the files under assets/sections/<slug>/):
//   base.webp   – what lies under the elements (plain letter paper)
//   el-NN.webp  – each element at its exact place on the slide
//   top.webp    – the slide without its text, with holes where the elements
//                 show through (keeps everything drawn over an element)
//   text.webp   – the slide's text alone, written out line by line
//   video-poster.webp – (pages with a video) the still in the video frame

type LayersFile = {
  width: number
  height: number
  elements: { src: string; x: number; y: number; w: number; h: number; reveal: number }[]
  lines: Box[]
  video?: Box
}

/** A box as fractions (0–1) of the page. */
export type Box = { x: number; y: number; w: number; h: number }

export type PageElement = {
  url: string
  /** Box as fractions (0–1) of the page. */
  x: number
  y: number
  w: number
  h: number
  /** Order in which elements appear: top to bottom. */
  reveal: number
}

export type PageLayers = {
  width: number
  height: number
  base: string
  top: string
  /** In paint order (later ones are drawn over earlier ones). */
  elements: PageElement[]
  text: string
  /** Each line of text, in reading order. */
  lines: Box[]
  /** Where the page plays a video (under the elements), with its still. */
  video?: Box & { poster: string }
}

const files = import.meta.glob<LayersFile>('./assets/sections/*/layers.json', { eager: true, import: 'default' })
const urls = import.meta.glob<string>('./assets/sections/*/*.webp', { eager: true, import: 'default' })

function url(slug: SectionSlug, file: string): string {
  const found = urls[`./assets/sections/${slug}/${file}`]
  if (!found) throw new Error(`Missing section asset ${slug}/${file}`)
  return found
}

export function pageLayers(slug: SectionSlug): PageLayers {
  const file = files[`./assets/sections/${slug}/layers.json`]
  if (!file) throw new Error(`Missing layers for ${slug}`)
  return {
    width: file.width,
    height: file.height,
    base: url(slug, 'base.webp'),
    top: url(slug, 'top.webp'),
    elements: file.elements.map(({ src, ...box }) => ({ url: url(slug, src), ...box })),
    text: url(slug, 'text.webp'),
    lines: file.lines,
    video: file.video && { ...file.video, poster: url(slug, 'video-poster.webp') },
  }
}
