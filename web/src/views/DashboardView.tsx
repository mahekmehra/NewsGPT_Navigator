import { motion } from 'framer-motion'
import { Clock, Sparkles, Telescope } from 'lucide-react'
import { BriefingAudioPlayer } from '@/components/BriefingAudioPlayer'
import { BriefingOutput } from '@/components/BriefingOutput'
import { IntelligenceAnalytics } from '@/components/analytics/IntelligenceAnalytics'
import { ExecutionFlowPipeline } from '@/components/ExecutionFlowPipeline'
import { RippleButton } from '@/components/RippleButton'
import { ScrollReveal } from '@/components/ScrollReveal'
import { DashboardAnalyzeSkeleton, PreviewCardsSkeleton } from '@/components/Skeleton'
import type { AnalyzeResponse } from '@/types/api'

type Props = {
  topic: string
  onTopicChange: (t: string) => void
  personas: { name: string; description: string }[]
  persona: string
  onPersonaChange: (p: string) => void
  languages: { code: string; name: string }[]
  language: string
  onLanguageChange: (c: string) => void
  onAnalyze: () => void
  loading: boolean
  pipelineStep: number
  error: string | null
  data: AnalyzeResponse | null
}

function scrollToId(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function getGreeting() {
  // Use IST (GMT +5:30)
  const now = new Date()
  const utcOffset = now.getTimezoneOffset() // in minutes
  const istTime = new Date(now.getTime() + (utcOffset + 330) * 60000)
  const hour = istTime.getHours()

  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

export function DashboardView({
  topic,
  onTopicChange,
  personas,
  persona,
  onPersonaChange,
  languages,
  language,
  onLanguageChange,
  onAnalyze,
  loading,
  pipelineStep,
  error,
  data,
}: Props) {
  const briefing = data?.briefing
  const analyzeFailed = Boolean(error && !loading)

  const summaryRaw = briefing?.summary
  const summaryPreview = typeof summaryRaw === 'string' ? summaryRaw.slice(0, 220) : ''
  const timelineCount = Array.isArray(briefing?.timeline) ? briefing.timeline.length : 0
  const predictionRaw = briefing?.prediction
  const predictionPreview = typeof predictionRaw === 'string' ? predictionRaw.slice(0, 180) : ''

  return (
    <div className="space-y-10">
      {/* Top: input bar */}
      <section className="space-y-4">
        <div>
          <motion.h2
            className="text-3xl font-bold tracking-tight text-white md:text-4xl"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {getGreeting()}
          </motion.h2>
          <p className="mt-2 max-w-2xl text-[var(--text-muted)]">
            Configure the run, then watch the multi-agent system execute left to right.
          </p>
        </div>

        <div className="glass-panel rounded-2xl p-4 md:p-6">
          <div className="grid gap-4 lg:grid-cols-[1fr_160px_160px_auto] lg:items-end">
            <div>
              <label
                htmlFor="dash-topic"
                className="mb-2 block text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]"
              >
                Topic
              </label>
              <input
                id="dash-topic"
                value={topic}
                onChange={(e) => onTopicChange(e.target.value)}
                placeholder="What should the agents analyze?"
                className="w-full rounded-xl border border-white/10 bg-black/35 px-4 py-3 text-base text-white outline-none ring-indigo-500/30 placeholder:text-zinc-600 focus:ring-2"
              />
            </div>
            <div>
              <label
                htmlFor="dash-persona"
                className="mb-2 block text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]"
              >
                Persona
              </label>
              <select
                id="dash-persona"
                value={persona}
                onChange={(e) => onPersonaChange(e.target.value)}
                className="w-full cursor-pointer rounded-xl border border-white/10 bg-black/35 py-3 pl-3 pr-8 text-sm font-medium text-white outline-none ring-indigo-500/30 focus:ring-2"
              >
                {personas.map((p) => (
                  <option key={p.name} value={p.name}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label
                htmlFor="dash-language"
                className="mb-2 block text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]"
              >
                Language
              </label>
              <select
                id="dash-language"
                value={language}
                onChange={(e) => onLanguageChange(e.target.value)}
                className="w-full cursor-pointer rounded-xl border border-white/10 bg-black/35 py-3 pl-3 pr-8 text-sm font-medium text-white outline-none ring-indigo-500/30 focus:ring-2"
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex lg:justify-end">
              <RippleButton
                type="button"
                onClick={onAnalyze}
                disabled={loading || topic.trim().length < 2}
                className="analyze-glow relative flex w-full items-center justify-center gap-2 overflow-hidden rounded-xl bg-gradient-to-r from-indigo-600 via-violet-600 to-indigo-600 px-8 py-3 text-sm font-semibold text-white bg-[length:200%_100%] disabled:cursor-not-allowed disabled:opacity-40 lg:mt-6 lg:w-auto"
              >
                <motion.span
                  className="pointer-events-none absolute inset-0 z-0 opacity-40"
                  animate={{
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                  }}
                  transition={{ duration: 3.5, repeat: Infinity, ease: 'linear' }}
                  style={{
                    backgroundImage:
                      'linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.35) 45%, transparent 90%)',
                  }}
                />
                <Sparkles className="relative z-[6] h-4 w-4" />
                <span className="relative z-[6]">Analyze</span>
              </RippleButton>
            </div>
          </div>

          {/* Status */}
          <div className="mt-5 flex min-h-[28px] items-center gap-2">
            {loading && topic.trim().length >= 2 && (
              <motion.div
                className="flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1.5 text-sm text-indigo-100"
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-60" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-indigo-400" />
                </span>
                <span>
                  Analyzing: <span className="font-semibold text-white">{topic.trim()}</span>
                </span>
              </motion.div>
            )}
            {!loading && briefing && (
              <p className="text-sm text-emerald-200/90">Run complete — output synced below.</p>
            )}
          </div>

          {error && (
            <motion.p
              className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {error}
            </motion.p>
          )}
        </div>
      </section>

      {/* System execution flow */}
      <ScrollReveal>
        <section className="space-y-4">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <h3 className="text-lg font-semibold tracking-tight text-white md:text-xl">
              System Execution Flow
            </h3>
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-[var(--text-muted)]">
              Live orchestration
            </p>
          </div>
          <div className="glass-panel rounded-2xl p-4 md:p-6">
            <ExecutionFlowPipeline
              activeIndex={pipelineStep}
              loading={loading}
              data={data}
              analyzeFailed={analyzeFailed}
            />
          </div>
        </section>
      </ScrollReveal>

      {!loading && briefing?.audio_url && (
        <ScrollReveal delay={0.1}>
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold tracking-tight text-white md:text-xl">
                Audio Briefing
              </h3>
              <span className="text-[10px] font-medium uppercase tracking-wider text-[var(--text-muted)]">
                Vernacular synthesis
              </span>
            </div>
            <BriefingAudioPlayer audioUrl={briefing.audio_url} />
          </section>
        </ScrollReveal>
      )}

      {/* Synthesized output preview */}
      <ScrollReveal delay={0.06}>
        <section className="space-y-4">
          <h3 className="text-lg font-semibold tracking-tight text-white md:text-xl">
            Synthesized Output Preview
          </h3>
          {loading && !briefing ? (
            <PreviewCardsSkeleton />
          ) : (
        <div className="grid gap-4 md:grid-cols-3">
          <motion.button
            type="button"
            onClick={() => scrollToId('briefing-section-summary')}
            className="group text-left"
            whileTap={{ scale: 0.99 }}
            transition={{ type: 'spring', stiffness: 420, damping: 28 }}
          >
            <div className="glass-panel h-full cursor-pointer rounded-2xl border border-white/[0.06] p-5 transition duration-300 ease-out group-hover:-translate-y-1 group-hover:scale-[1.02] group-hover:border-indigo-500/40 group-hover:shadow-[0_0_36px_-10px_rgba(99,102,241,0.35)]">
              <div className="mb-3 flex items-center gap-2 text-indigo-300">
                <Sparkles className="h-4 w-4 shrink-0" />
                <span className="text-xs font-semibold uppercase tracking-wider">Summary</span>
              </div>
              <p className="line-clamp-5 text-sm leading-relaxed text-[var(--text-muted)]">
                {briefing?.summary
                  ? summaryPreview + (briefing.summary.length > 220 ? '…' : '')
                  : 'Run an analysis to generate a persona-aware executive summary.'}
              </p>
              <p className="mt-3 text-[11px] font-medium text-indigo-400/80">Click to expand ↓</p>
            </div>
          </motion.button>

          <motion.button
            type="button"
            onClick={() => scrollToId('briefing-section-timeline')}
            className="group text-left"
            whileTap={{ scale: 0.99 }}
            transition={{ type: 'spring', stiffness: 420, damping: 28 }}
          >
            <div className="glass-panel h-full cursor-pointer rounded-2xl border border-white/[0.06] p-5 transition duration-300 ease-out group-hover:-translate-y-1 group-hover:scale-[1.02] group-hover:border-indigo-500/40 group-hover:shadow-[0_0_36px_-10px_rgba(99,102,241,0.35)]">
              <div className="mb-3 flex items-center gap-2 text-violet-300">
                <Clock className="h-4 w-4 shrink-0" />
                <span className="text-xs font-semibold uppercase tracking-wider">Timeline</span>
              </div>
              <p className="text-sm text-[var(--text-muted)]">
                {timelineCount > 0
                  ? `${timelineCount} events synthesized in the full timeline.`
                  : 'Chronological events appear here after a successful run.'}
              </p>
              <p className="mt-3 text-[11px] font-medium text-indigo-400/80">Click to expand ↓</p>
            </div>
          </motion.button>

          <motion.button
            type="button"
            onClick={() => scrollToId('briefing-section-prediction')}
            className="group text-left"
            whileTap={{ scale: 0.99 }}
            transition={{ type: 'spring', stiffness: 420, damping: 28 }}
          >
            <div className="glass-panel h-full cursor-pointer rounded-2xl border border-white/[0.06] p-5 transition duration-300 ease-out group-hover:-translate-y-1 group-hover:scale-[1.02] group-hover:border-indigo-500/40 group-hover:shadow-[0_0_36px_-10px_rgba(99,102,241,0.35)]">
              <div className="mb-3 flex items-center gap-2 text-cyan-300">
                <Telescope className="h-4 w-4 shrink-0" />
                <span className="text-xs font-semibold uppercase tracking-wider">Prediction</span>
              </div>
              <p className="line-clamp-5 text-sm leading-relaxed text-[var(--text-muted)]">
                {briefing?.prediction
                  ? predictionPreview + (briefing.prediction.length > 180 ? '…' : '')
                  : 'Forward-looking implications and scenarios will surface here.'}
              </p>
              <p className="mt-3 text-[11px] font-medium text-indigo-400/80">Click to expand ↓</p>
            </div>
          </motion.button>
        </div>
          )}
        </section>
      </ScrollReveal>

      {/* Main briefing output (grid) */}
      {loading && !briefing ? (
        <DashboardAnalyzeSkeleton />
      ) : briefing ? (
        <ScrollReveal delay={0.08}>
          <BriefingOutput briefing={briefing} />
        </ScrollReveal>
      ) : (
        <section className="glass-panel rounded-2xl p-8 text-center md:p-12">
          <p className="text-sm text-[var(--text-muted)]">
            Run <span className="text-white">Analyze</span> to generate a structured briefing: summary,
            timeline, prediction, four angles, and a persona-specific brief.
          </p>
        </section>
      )}

      {!loading && data?.success && data && (
        <ScrollReveal delay={0.05}>
          <IntelligenceAnalytics data={data} />
        </ScrollReveal>
      )}
    </div>
  )
}
