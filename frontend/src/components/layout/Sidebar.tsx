import { type ElementType } from 'react'
import { Plane, Presentation, FileText, Table2, Search, LogOut, Cpu } from 'lucide-react'
import { cn } from '../../lib/utils'
import { useAuth } from '../../hooks/useAuth'
import type { Feature } from '../../types'

const NAV_ITEMS: { id: Feature; label: string; icon: ElementType; description: string }[] = [
  { id: 'travel', label: 'Trip Planner', icon: Plane, description: 'Flights + hotels + itinerary' },
  { id: 'slides', label: 'Slide Creator', icon: Presentation, description: 'AI-generated slide decks' },
  { id: 'resume', label: 'Resume Polish', icon: FileText, description: 'Rewrite & improve your resume' },
  { id: 'sheet', label: 'Sheet Builder', icon: Table2, description: 'Generate CSV spreadsheets' },
  { id: 'research', label: 'Industry Research', icon: Search, description: 'Deep industry analysis' },
]

interface SidebarProps {
  active: Feature
  onSelect: (f: Feature) => void
}

export function Sidebar({ active, onSelect }: SidebarProps) {
  const { email, logout } = useAuth()

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-white/10 bg-[#07111f]/80 backdrop-blur-xl">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-6 border-b border-white/10">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/25">
          <Cpu className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="text-sm font-bold text-white">TaskForge AI</p>
          <p className="text-[11px] text-white/40">Multi-Agent Platform</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {NAV_ITEMS.map(({ id, label, icon: Icon, description }) => (
          <button
            key={id}
            onClick={() => onSelect(id)}
            className={cn(
              'group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-all duration-150',
              active === id
                ? 'bg-white/10 text-white shadow-inner'
                : 'text-white/50 hover:bg-white/5 hover:text-white/80',
            )}
          >
            <div className={cn(
              'flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-all',
              active === id
                ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-md shadow-blue-500/30'
                : 'bg-white/5 text-white/40 group-hover:bg-white/10 group-hover:text-white/70',
            )}>
              <Icon className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-medium leading-none">{label}</p>
              <p className={cn(
                'mt-0.5 truncate text-[11px] transition-colors',
                active === id ? 'text-white/50' : 'text-white/30 group-hover:text-white/40',
              )}>{description}</p>
            </div>
          </button>
        ))}
      </nav>

      {/* User / logout */}
      <div className="border-t border-white/10 px-3 py-3">
        <div className="flex items-center gap-3 rounded-xl px-3 py-2">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-xs font-bold text-white uppercase">
            {email?.[0] ?? '?'}
          </div>
          <p className="flex-1 truncate text-xs text-white/50">{email}</p>
          <button
            onClick={logout}
            title="Logout"
            className="text-white/30 hover:text-red-400 transition-colors"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
