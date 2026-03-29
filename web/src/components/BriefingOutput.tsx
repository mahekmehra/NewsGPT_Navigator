import { motion } from 'framer-motion'
import {
  AlertTriangle,
  Brain,
  CheckCircle2,
  ExternalLink,
  Lightbulb,
  Sparkles,
  TrendingUp,
  UserCircle2,
} from 'lucide-react'
import type { Briefing } from '@/types/api'

type Props = {
  briefing: Briefing
}

const ANGLE_CONFIG = [
  {
    key: 'market_impact' as const,
    label: 'Market Impact',
    Icon: TrendingUp,
    accent: 'from-emerald-500/20 to-teal-500/5 border-emerald-500/25 text-emerald-200',
  },
  {
    key: 'risks' as const,
    label: 'Risks',
    Icon: AlertTriangle,
    accent: 'from-amber-500/15 to-orange-500/5 border-amber-500/25 text-amber-200',
  },
  {
    key: 'opportunities' as const,
    label: 'Opportunities',
    Icon: Sparkles,
    accent: 'from-indigo-500/20 to-violet-500/5 border-indigo-500/30 text-indigo-200',
  },
  {
    key: 'expert_opinion' as const,
    label: 'Expert Opinion',
    Icon: Brain,
    accent: 'from-sky-500/15 to-blue-500/5 border-sky-500/25 text-sky-200',
  },
]

function confidencePercent(b: Briefing): number {
  const bias = typeof b.bias_score === 'number' ? b.bias_score : 0.35
  const base = Math.round(100 - Math.min(45, bias * 120))
  const adj =
    b.compliance_status === 'Passed' ? 5 : b.compliance_status === 'Caution' ? -8 : 0
  return Math.max(58, Math.min(96, base + adj))
}

export function BriefingOutput({ briefing }: Props) {
  const pb = briefing.persona_brief || {}
  const personaLabel = briefing.persona || 'General'
  const headline = `Intelligence Synthesis (${personaLabel})`
  const conf = confidencePercent(briefing)

  return (
    <section className="space-y-5 pb-4" aria-label="Intelligence briefing output">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <h3 className="text-xl font-semibold tracking-tight text-white md:text-2xl">
          Briefing output
        </h3>
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-[var(--text-muted)]">
          Structured intelligence
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* 1. Summary */}
        <motion.article
          id="briefing-section-summary"
          className="glass-panel scroll-mt-28 rounded-2xl p-6 md:p-7"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="flex items-start justify-between gap-4">
            <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">
              Summary
            </h4>
            <div
              className="flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-100"
              title="Model synthesis confidence"
            >
              <span className="text-[var(--text-muted)]">Confidence</span>
              <span className="font-mono text-sm font-semibold tabular-nums text-white">
                {conf}%
              </span>
            </div>
          </div>
          <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500"
              initial={{ width: 0 }}
              animate={{ width: `${conf}%` }}
              transition={{ duration: 1, ease: [0.22, 1, 0.36, 1], delay: 0.15 }}
            />
          </div>
          <p className="mt-5 text-[15px] leading-relaxed text-zinc-200">
            {briefing.summary || 'No summary returned for this run.'}
          </p>
          {briefing.title && (
            <p className="mt-4 text-xs font-medium text-[var(--text-muted)]">{briefing.title}</p>
          )}
        </motion.article>

        {/* 2. Timeline */}
        <motion.article
          id="briefing-section-timeline"
          className="glass-panel scroll-mt-28 rounded-2xl p-6 md:p-7"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.05 }}
        >
          <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">
            Timeline
          </h4>
          {Array.isArray(briefing.timeline) && briefing.timeline.length > 0 ? (
            <div className="relative mt-6 pl-2">
              <div className="absolute bottom-2 left-[7px] top-2 w-px bg-gradient-to-b from-indigo-500/50 via-violet-500/30 to-transparent" />
              <ul className="space-y-6">
                {briefing.timeline.map((ev, i) => (
                  <motion.li
                    key={`${ev.date}-${i}`}
                    className="relative flex gap-4 pl-6"
                    initial={{ opacity: 0, x: -6 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.08 * i, duration: 0.35 }}
                  >
                    <span className="absolute left-0 top-1.5 flex h-4 w-4 items-center justify-center">
                      <motion.span
                        className="absolute h-4 w-4 rounded-full bg-indigo-500/30"
                        animate={{ scale: [1, 1.35, 1], opacity: [0.6, 0.2, 0.6] }}
                        transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut', delay: i * 0.25 }}
                      />
                      <span className="relative z-10 h-2.5 w-2.5 rounded-full border-2 border-indigo-300 bg-[var(--bg-base)] shadow-[0_0_12px_2_rgba(129,140,248,0.7)]" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="font-mono text-xs text-indigo-300/90">{ev.date || '—'}</p>
                      <p className="mt-1 text-sm leading-relaxed text-zinc-200">{ev.event}</p>
                    </div>
                  </motion.li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="mt-6 text-sm text-[var(--text-muted)]">
              No dated events in this briefing. Try a topic with clearer chronology.
            </p>
          )}
        </motion.article>

        {/* 3. Prediction / Final Assessment */}
        <motion.article
          id="briefing-section-prediction"
          className="relative scroll-mt-28 overflow-hidden rounded-2xl border border-cyan-500/20 bg-gradient-to-br from-cyan-950/40 via-[var(--bg-elevated)] to-transparent lg:col-span-2"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.08 }}
        >
          <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-2xl">
            <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(8,8,20,0.2)_0%,transparent_45%,rgba(99,102,241,0.08)_100%)]" />
            <motion.div
              className="absolute inset-0 bg-[repeating-linear-gradient(90deg,transparent,transparent_31px,rgba(99,102,241,0.06)_31px,rgba(99,102,241,0.06)_32px)]"
              animate={{ x: [0, 32] }}
              transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
            />
          </div>
          <div className="relative z-10 p-6 md:p-8">
            <div className="mb-3 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-cyan-300" />
                <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-200/90">
                  Final Assessment
                </h4>
              </div>
              {pb.confidence_score && (
                <span className="text-xs font-semibold text-cyan-200/70 border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 rounded uppercase">
                  Confidence: {pb.confidence_score}
                </span>
              )}
            </div>
            <p className="max-w-4xl text-lg font-medium leading-relaxed text-white md:text-xl">
              {pb.final_assessment || briefing.prediction ||
                'Forward-looking synthesis will appear here when the analysis pipeline returns a prediction.'}
            </p>
            <p className="mt-4 text-xs text-cyan-200/50">Scenario-weighted outlook · not financial advice</p>
          </div>
        </motion.article>

        {/* 4. Angles */}
        <motion.article
          id="briefing-section-angles"
          className="glass-panel scroll-mt-28 rounded-2xl p-6 md:p-7 lg:col-span-2"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="mb-5 flex flex-wrap items-center justify-between gap-2">
            <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">
              Angles
            </h4>
            <span className="text-[11px] font-medium uppercase tracking-wider text-indigo-400/80">
              Four-lens decomposition
            </span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {ANGLE_CONFIG.map(({ key, label, Icon, accent }, i) => {
              const textRaw = briefing.angles?.[key]
              const text = typeof textRaw === 'string' ? textRaw.trim() : ''
              return (
                <motion.div
                  key={key}
                  className={`rounded-xl border bg-gradient-to-br p-4 ${accent}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.06 * i, duration: 0.35 }}
                  whileHover={{ scale: 1.01 }}
                >
                  <div className="mb-2 flex items-center gap-2">
                    <Icon className="h-4 w-4 shrink-0 opacity-90" />
                    <span className="text-xs font-semibold uppercase tracking-wider text-white/90">
                      {label}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed text-zinc-300/95">
                    {text || '—'}
                  </p>
                </motion.div>
              )
            })}
          </div>
        </motion.article>

        {/* 5. Persona brief */}
        <motion.article
          id="briefing-section-persona"
          className="glass-panel scroll-mt-28 rounded-2xl p-6 md:p-8 lg:col-span-2"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.12 }}
        >
          <div className="flex flex-wrap items-start gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-violet-500/30 bg-violet-500/10 text-violet-200">
              <UserCircle2 className="h-6 w-6" />
            </div>
            <div className="min-w-0 flex-1">
              <h4 className="text-lg font-semibold text-white md:text-xl">{headline}</h4>
              <p className="mt-1 text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
                Persona · {personaLabel}
              </p>
            </div>
          </div>

          <div className="mt-5 space-y-6">
            {/* Entity Chips with Links */}
            <div className="flex flex-wrap gap-2">
              {Array.isArray(briefing.entities_metadata) && briefing.entities_metadata.map((meta, i) => {
                const url = meta.entity_articles?.[0]?.url
                if (url) {
                  return (
                    <motion.a
                      key={`${meta.entity}-${i}`}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-500/20 bg-indigo-500/10 px-3 py-1.5 text-xs font-medium text-indigo-100 transition-all hover:border-indigo-500/40 hover:bg-indigo-500/20"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.05 * i }}
                    >
                      <span>{meta.entity}</span>
                      <ExternalLink className="h-3 w-3 opacity-60" />
                    </motion.a>
                  )
                }
                return (
                  <motion.div
                    key={`${meta.entity}-${i}`}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-zinc-300"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.05 * i }}
                  >
                    <span>{meta.entity}</span>
                  </motion.div>
                )
              })}
            </div>

            {/* Main Specific Summary */}
            {typeof pb.summary === 'string' && pb.summary.trim() && (
              <p className="text-[15px] leading-relaxed text-zinc-300">{pb.summary}</p>
            )}

            {/* Source Quality Context (Telemetry) */}
            {pb.source_quality_summary && (
              <div className="flex items-center gap-2 rounded-lg border border-zinc-700/50 bg-zinc-800/30 px-3 py-2 text-xs text-zinc-400">
                <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                <span>{pb.source_quality_summary}</span>
              </div>
            )}

            <div className="grid gap-4 sm:grid-cols-2">
              {/* Risks */}
              {Array.isArray(pb.risks) && pb.risks.length > 0 && (
                <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
                  <div className="mb-3 flex items-center gap-2 text-amber-300">
                    <AlertTriangle className="h-4 w-4" />
                    <span className="text-xs font-semibold uppercase tracking-wider">Identified Risks</span>
                  </div>
                  <ul className="space-y-2">
                    {pb.risks.map((risk, i) => (
                      <li key={i} className="flex gap-2 text-sm text-amber-50/90">
                        <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500/60" />
                        <span>{risk}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Next Steps */}
              {Array.isArray(pb.next_steps) && pb.next_steps.length > 0 && (
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
                  <div className="mb-3 flex items-center gap-2 text-emerald-300">
                    <TrendingUp className="h-4 w-4" />
                    <span className="text-xs font-semibold uppercase tracking-wider">Next Steps</span>
                  </div>
                  <ul className="space-y-2">
                    {pb.next_steps.map((step, i) => (
                      <li key={i} className="flex gap-2 text-sm text-emerald-50/90">
                        <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500/60" />
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Key Reasoning/Insights List */}
            {Array.isArray(pb.insights) && pb.insights.length > 0 && (
              <div className="pt-2">
                <h5 className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">Core Insights</h5>
                <ul className="space-y-3">
                  {pb.insights.map((line, i) => (
                    <motion.li
                      key={`${line}-${i}`}
                      className="flex gap-3 text-sm text-zinc-200"
                      initial={{ opacity: 0, x: -4 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.04 * i }}
                    >
                      <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-violet-400" />
                      <span className="leading-relaxed">{line}</span>
                    </motion.li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </motion.article>
      </div>

    </section>
  )
}
