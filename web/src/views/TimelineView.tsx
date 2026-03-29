import { motion } from 'framer-motion'
import { ExternalLink } from 'lucide-react'
import { GlassCard } from '@/components/GlassCard'

type Event = { date: string; event: string; url?: string; source_title?: string }

type Props = {
  events: Event[]
}

export function TimelineView({ events }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Timeline</h2>
        <p className="mt-2 text-[var(--text-muted)]">
          Chronological spine synthesized from the briefing.
        </p>
      </div>

      {events.length === 0 ? (
        <GlassCard className="border-dashed border-white/15">
          <p className="text-center text-sm text-[var(--text-muted)]">
            Timeline events appear after you run an analysis with timeline data.
          </p>
        </GlassCard>
      ) : (
        <div className="relative pl-6">
          <div className="absolute bottom-0 left-[11px] top-0 w-px bg-gradient-to-b from-indigo-500/50 via-violet-500/30 to-transparent" />
          <ul className="space-y-6">
            {events.map((ev, i) => (
              <motion.li
                key={`${ev.date}-${i}`}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                className="relative"
              >
                <span className="absolute -left-6 top-1.5 h-3 w-3 rounded-full border-2 border-indigo-400 bg-[var(--bg-base)] shadow-[0_0_12px_2px_rgba(129,140,248,0.6)]" />
                <GlassCard className="!p-4">
                  <p className="font-mono text-xs text-indigo-300">{ev.date || '—'}</p>
                  <p className="mt-2 text-sm text-zinc-200">{ev.event}</p>
                  {ev.url && (
                    <a
                      href={ev.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 inline-flex items-center gap-1 text-[11px] font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
                    >
                      <ExternalLink className="h-3 w-3" />
                      {ev.source_title ? `Source: ${ev.source_title}` : 'Read More'}
                    </a>
                  )}
                </GlassCard>
              </motion.li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
