import { AnimatePresence, motion } from 'framer-motion'
import { X } from 'lucide-react'

type Props = {
  open: boolean
  onClose: () => void
  languages: { code: string; name: string }[]
  language: string
  onLanguageChange: (code: string) => void
}

export function SettingsPanel({
  open,
  onClose,
  languages,
  language,
  onLanguageChange,
}: Props) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="settings-title"
            className="glass-panel glow-ring max-w-md rounded-2xl p-6"
            initial={{ scale: 0.94, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 420, damping: 32 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-6 flex items-center justify-between">
              <h2 id="settings-title" className="text-lg font-semibold text-white">
                Settings
              </h2>
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg p-2 text-zinc-400 hover:bg-white/10 hover:text-white"
                aria-label="Close"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
              Output language
            </label>
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="w-full cursor-pointer rounded-xl border border-white/10 bg-black/40 py-2.5 pl-3 pr-8 text-sm text-white outline-none ring-indigo-500/40 focus:ring-2"
            >
              {languages.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>

            <p className="mt-4 text-xs leading-relaxed text-[var(--text-muted)]">
              API base is proxied to the FastAPI backend in dev. Run{' '}
              <code className="rounded bg-white/10 px-1 py-0.5">uvicorn api.main:app --reload</code>{' '}
              on port 8000.
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
