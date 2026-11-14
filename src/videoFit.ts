// Fitting the Google Drive player into a page's video frame.
// Pure, so it can be unit-tested in plain Node; SectionPage.tsx applies it.

/**
 * Narrower than this (CSS px), Drive's player no longer fits its own video
 * and controls: it crops the picture and pushes the controls off the bottom.
 * (Measured with the "Lời tri ân" video: fine at 426×284, cropped at 400×225.)
 */
export const PLAYER_MIN_WIDTH = 480

export type Fit = {
  /** CSS px the player is laid out at, in the frame's proportions. */
  width: number
  height: number
  /** Shrink applied on top (transform), so it fills the frame exactly. */
  scale: number
}

/** Lay the player out at least PLAYER_MIN_WIDTH wide, then shrink it into `box`. */
export function playerFit(box: { width: number; height: number }): Fit {
  if (box.width <= 0 || box.height <= 0) return { width: 0, height: 0, scale: 1 }
  if (box.width >= PLAYER_MIN_WIDTH) return { width: box.width, height: box.height, scale: 1 }
  const scale = box.width / PLAYER_MIN_WIDTH
  return { width: PLAYER_MIN_WIDTH, height: box.height / scale, scale }
}
