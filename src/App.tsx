import { useState } from 'react'
import type { Burst } from './ButterflyBurst'
import type { Point } from './butterflies'
import Home from './Home'
import SectionDialog from './SectionDialog'
import { useSectionRoute } from './useSectionRoute'

const screenCentre = (): Point => ({ x: window.innerWidth / 2, y: window.innerHeight / 2 })

export default function App() {
  const route = useSectionRoute()
  // Butterflies burst out of the middle of the screen whenever a section opens.
  const [burst, setBurst] = useState<Burst | null>(() =>
    route.openIndex === null ? null : { id: 0, origin: screenCentre() },
  )

  const open = (index: number) => {
    setBurst((prev) => ({ id: (prev?.id ?? 0) + 1, origin: screenCentre() }))
    route.open(index)
  }

  return (
    <>
      <Home onOpen={open} />
      <SectionDialog index={route.openIndex} onClose={route.close} onChange={route.change} burst={burst} />
    </>
  )
}
