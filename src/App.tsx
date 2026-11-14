import Home from './Home'
import SectionDialog from './SectionDialog'
import { useSectionRoute } from './useSectionRoute'

export default function App() {
  const route = useSectionRoute()

  return (
    <>
      <Home onOpen={route.open} />
      <SectionDialog index={route.openIndex} onClose={route.close} onChange={route.change} />
    </>
  )
}
