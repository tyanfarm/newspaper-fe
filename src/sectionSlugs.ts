// Kept free of asset imports so it can be unit-tested in plain Node.
export const SECTION_SLUGS = ['loi-ngo', 'vung-ky-uc', 'cung-nhau-lon', 'loi-tri-an'] as const

export type SectionSlug = (typeof SECTION_SLUGS)[number]

/** Index of the section named by a location hash (`#loi-ngo` → 0), or -1. */
export function sectionIndexFromHash(hash: string): number {
  let slug: string
  try {
    slug = decodeURIComponent(hash.replace(/^#/, ''))
  } catch {
    return -1
  }
  return SECTION_SLUGS.indexOf(slug as SectionSlug)
}
