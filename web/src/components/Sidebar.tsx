import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Network,
  GitCompareArrows,
  AlertTriangle,
  History,
  Clapperboard,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import type { SectionId } from '@/types/navigation'

const NAV: { id: SectionId; label: string; icon: typeof LayoutDashboard }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'entity-map', label: 'Entity Map', icon: Network },
  { id: 'persona-compare', label: 'Persona Compare', icon: GitCompareArrows },
  { id: 'conflicts', label: 'Conflicts', icon: AlertTriangle },
  { id: 'timeline', label: 'Timeline', icon: History },
  { id: 'videos', label: 'Videos', icon: Clapperboard },
]

type Props = {
  expanded: boolean
  section: SectionId
  onToggle: () => void
  onSelect: (id: SectionId) => void
}

export function Sidebar({ expanded, section, onToggle, onSelect }: Props) {
  return (
    <motion.aside
      initial={false}
      animate={{ width: expanded ? 240 : 72 }}
      transition={{ type: 'spring', stiffness: 380, damping: 34 }}
      className="glass-panel relative flex shrink-0 flex-col border-y-0 border-l-0 py-4"
    >
      <div className="mb-2 flex justify-end px-2">
        <motion.button
          type="button"
          onClick={onToggle}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/[0.04] text-zinc-300 hover:text-white"
          whileHover={{ scale: 1.05 }}
          aria-expanded={expanded}
          aria-label={expanded ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {expanded ? (
            <ChevronLeft className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </motion.button>
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-2">
        {NAV.map((item) => {
          const active = section === item.id
          const Icon = item.icon
          return (
            <motion.button
              key={item.id}
              type="button"
              onClick={() => onSelect(item.id)}
              className={[
                'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition',
                active
                  ? 'bg-gradient-to-r from-indigo-500/25 to-violet-600/20 text-white shadow-[0_0_24px_-4px_rgba(99,102,241,0.45)]'
                  : 'text-[var(--text-muted)] hover:bg-white/[0.05] hover:text-white',
              ].join(' ')}
              whileHover={{ x: expanded ? 2 : 0 }}
              layout
            >
              <Icon
                className={`h-5 w-5 shrink-0 ${active ? 'text-indigo-300' : 'text-zinc-500 group-hover:text-zinc-300'}`}
              />
              {expanded && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="truncate"
                >
                  {item.label}
                </motion.span>
              )}
              {active && expanded && (
                <motion.span
                  layoutId="nav-pill"
                  className="ml-auto h-1.5 w-1.5 rounded-full bg-indigo-400 shadow-[0_0_8px_2px_rgba(129,140,248,0.8)]"
                />
              )}
            </motion.button>
          )
        })}
      </nav>

      {!expanded && (
        <p className="sr-only">
          Navigation: use expand button to show section labels.
        </p>
      )}
    </motion.aside>
  )
}
