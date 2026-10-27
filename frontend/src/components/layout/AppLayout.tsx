import { useState } from 'react'
import { Sidebar } from './Sidebar'
import { TravelPanel } from '../features/TravelPanel'
import { SlidesPanel } from '../features/SlidesPanel'
import { ResumePanel } from '../features/ResumePanel'
import { SheetPanel } from '../features/SheetPanel'
import { ResearchPanel } from '../features/ResearchPanel'
import type { Feature } from '../../types'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const PANELS: Record<Feature, () => any> = {
  travel: TravelPanel,
  slides: SlidesPanel,
  resume: ResumePanel,
  sheet: SheetPanel,
  research: ResearchPanel,
}

export function AppLayout() {
  const [active, setActive] = useState<Feature>('travel')
  const Panel = PANELS[active]

  return (
    <div className="flex h-screen overflow-hidden bg-[#07111f]">
      {/* Background blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 h-[500px] w-[500px] rounded-full bg-blue-600/10 blur-[120px]" />
        <div className="absolute top-1/3 -right-40 h-[400px] w-[400px] rounded-full bg-purple-600/10 blur-[120px]" />
        <div className="absolute -bottom-40 left-1/3 h-[400px] w-[400px] rounded-full bg-teal-600/8 blur-[120px]" />
      </div>

      <Sidebar active={active} onSelect={setActive} />

      <main className="relative flex-1 overflow-y-auto">
        <Panel />
      </main>
    </div>
  )
}
