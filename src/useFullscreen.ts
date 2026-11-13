import { useCallback, useSyncExternalStore } from 'react'

function subscribe(onChange: () => void) {
  document.addEventListener('fullscreenchange', onChange)
  return () => document.removeEventListener('fullscreenchange', onChange)
}

const isFullscreenNow = () => document.fullscreenElement !== null

export function useFullscreen() {
  const isFullscreen = useSyncExternalStore(subscribe, isFullscreenNow, () => false)

  const toggle = useCallback(() => {
    const request = document.fullscreenElement
      ? document.exitFullscreen()
      : document.documentElement.requestFullscreen()
    // Browsers reject when fullscreen is blocked; nothing useful to do then.
    request.catch(() => {})
  }, [])

  // iPhone Safari has no element fullscreen, so the button is hidden there.
  return { supported: document.fullscreenEnabled, isFullscreen, toggle }
}
