import { motion } from 'framer-motion'
import { Settings, Sparkles } from 'lucide-react'

type Props = {
  agentsOnline: boolean
  onOpenSettings: () => void
}

export function TopBar({ agentsOnline, onOpenSettings }: Props) {
  return (
    <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center justify-between gap-4 border-b border-white/[0.08] bg-[#07070f]/95 px-4 backdrop-blur-xl md:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <motion.div
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/30 to-violet-600/30 ring-1 ring-indigo-400/30"
          whileHover={{ scale: 1.05 }}
          transition={{ type: 'spring', stiffness: 400, damping: 22 }}
        >
          <Sparkles className="h-5 w-5 text-indigo-200" aria-hidden />
        </motion.div>
        <div className="min-w-0">
          <h1 className="truncate text-lg font-bold tracking-tight text-white md:text-xl">
            NewsGPT Navigator
          </h1>
          <p className="hidden text-[11px] font-medium uppercase tracking-[0.2em] text-[var(--text-muted)] sm:block">
            Intelligence OS
          </p>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-2 md:gap-4">
        <motion.div
          className="hidden items-center gap-2 rounded-full border border-emerald-500/25 bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-200/90 sm:flex"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <span className="text-base leading-none" aria-hidden>
            {agentsOnline ? '🟢' : '🟡'}
          </span>
          <span>{agentsOnline ? 'Agents Online' : 'Connecting…'}</span>
        </motion.div>

        <motion.button
          type="button"
          onClick={onOpenSettings}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-zinc-300 transition hover:border-indigo-400/40 hover:text-white"
          whileHover={{ scale: 1.06 }}
          whileTap={{ scale: 0.96 }}
          aria-label="Settings"
        >
          <Settings className="h-5 w-5" />
        </motion.button>
      </div>
    </header>
  )
}
