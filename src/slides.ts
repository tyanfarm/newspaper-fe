export type Slide = {
  src: string
  name: string
}

// Every image dropped into src/slides/ becomes a slide, ordered by file name
// with numeric sorting (1, 2, …, 10 rather than 1, 10, 2).
const modules = import.meta.glob<string>('./slides/*.{png,jpg,jpeg,webp,avif}', {
  eager: true,
  query: '?url',
  import: 'default',
})

export const slides: Slide[] = Object.entries(modules)
  .sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }))
  .map(([path, src]) => ({
    src,
    name: path.replace(/^.*\//, '').replace(/\.[^.]+$/, ''),
  }))
