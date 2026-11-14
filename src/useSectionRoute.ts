import { useCallback, useEffect, useRef, useState } from 'react'
import { sectionIndexFromHash, sections } from './sections'

const indexFromHash = (hash: string) => {
  const i = sectionIndexFromHash(hash)
  return i === -1 ? null : i
}

/**
 * Which section popup is open, mirrored in the URL hash (#loi-ngo …) so a
 * section can be linked to and the phone's Back button closes the popup.
 */
export function useSectionRoute() {
  const [openIndex, setOpenIndex] = useState<number | null>(() => indexFromHash(location.hash))
  // True when the current #section entry was pushed by this page. Only then is
  // history.back() safe for closing; after a deep link it would leave the site.
  const pushed = useRef(false)

  useEffect(() => {
    const onPopState = () => {
      pushed.current = false
      setOpenIndex(indexFromHash(location.hash))
    }
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  const open = useCallback((i: number) => {
    history.pushState(null, '', `#${sections[i].slug}`)
    pushed.current = true
    setOpenIndex(i)
  }, [])

  const change = useCallback((i: number) => {
    history.replaceState(null, '', `#${sections[i].slug}`)
    setOpenIndex(i)
  }, [])

  const close = useCallback(() => {
    if (pushed.current) {
      pushed.current = false
      history.back() // popstate clears openIndex
    } else {
      history.replaceState(null, '', location.pathname + location.search)
      setOpenIndex(null)
    }
  }, [])

  return { openIndex, open, close, change }
}
