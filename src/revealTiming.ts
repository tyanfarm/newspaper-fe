// When each part of a section page appears after the popup opens (seconds).
// Pure, so it can be unit-tested in plain Node; SectionPage.tsx applies it.

/** Pause before the first picture, while the butterflies set off. */
export const ELEMENT_LEAD = 0.35
/** Gap between one picture starting to appear and the next. */
export const ELEMENT_STEP = 0.12
/** How long a picture takes to fade in (its settle movement runs a little longer). */
export const ELEMENT_FADE = 0.7

/** The longest the text may take to write itself out, however many lines. */
export const TEXT_TOTAL_MAX = 6
/** Seconds to write a full-width line at natural speed. */
const FULL_LINE = 0.6
/** Shortest time for any line (a title, a one-word line). */
const MIN_LINE = 0.25
/** The next line starts when the current one is this far along. */
const HANDOFF = 0.7

export function elementDelay(reveal: number): number {
  return ELEMENT_LEAD + reveal * ELEMENT_STEP
}

/** When the last of `count` pictures has finished fading in. */
export function elementsDone(count: number): number {
  return count === 0 ? ELEMENT_LEAD : elementDelay(count - 1) + ELEMENT_FADE
}

/**
 * Start and duration for each line of text, in reading order, given each
 * line's width as a fraction (0–1) of the page width. Lines are written left
 * to right, one after another, starting once every picture is in place;
 * long pages are sped up to finish within TEXT_TOTAL_MAX.
 */
export function textSchedule(lineWidths: number[], elementCount: number): { start: number; duration: number }[] {
  if (lineWidths.length === 0) return []
  const durations = lineWidths.map((w) => Math.max(MIN_LINE, FULL_LINE * w))
  const offsets: number[] = []
  let t = 0
  for (const d of durations) {
    offsets.push(t)
    t += d * HANDOFF
  }
  const natural = offsets.at(-1)! + durations.at(-1)!
  const speed = Math.max(1, natural / TEXT_TOTAL_MAX)
  const begin = elementsDone(elementCount)
  return durations.map((d, i) => ({ start: begin + offsets[i] / speed, duration: d / speed }))
}

/** When the last line of text has been written (pages with a video show it then). */
export function textDone(lineWidths: number[], elementCount: number): number {
  const lines = textSchedule(lineWidths, elementCount)
  return lines.length ? Math.max(...lines.map((l) => l.start + l.duration)) : elementsDone(elementCount)
}
