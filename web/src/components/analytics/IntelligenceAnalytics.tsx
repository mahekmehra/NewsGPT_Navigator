import { motion } from 'framer-motion'
import type { ComponentType } from 'react'
import {
  Activity,
  AlertTriangle,
  BarChart3,
  GitBranch,
  Radar,
  ShieldAlert,
  Sparkles,
  Target,
} from 'lucide-react'
import { ScrollReveal } from '@/components/ScrollReveal'
import type { AnalyzeResponse, ConflictItem, EmotionalRegister, EntitySentiment, StoryArcEntry } from '@/types/api'

// ─── Sentiment styling ─────────────────────────────────────────────

export function sentimentBadgeClass(sentiment: string): string {
  const x = sentiment.toLowerCase()
  if (x.includes('pos'))
    return 'border-emerald-500/40 bg-emerald-500/15 text-emerald-200 shadow-[0_0_16px_-4px_rgba(52,211,153,0.35)]'
  if (x.includes('neg'))
    return 'border-rose-500/40 bg-rose-500/15 text-rose-200 shadow-[0_0_16px_-4px_rgba(244,63,94,0.25)]'
  return 'border-zinc-500/35 bg-zinc-500/10 text-zinc-300'
}

export function scoreBarGradient(sentiment: string): string {
  const x = sentiment.toLowerCase()
  if (x.includes('pos')) return 'from-emerald-500 to-teal-400'
  if (x.includes('neg')) return 'from-rose-500 to-orange-500'
  return 'from-zinc-500 to-zinc-400'
}

function normalizeScore(score: number): number {
  if (!Number.isFinite(score)) return 50
  const s = score <= 1 ? score * 100 : Math.min(100, score)
  return Math.max(0, Math.min(100, s))
}

// ─── Entity map ────────────────────────────────────────────────────

type EntityMapProps = {
  entities: EntitySentiment[]
}

export function EntityMapSection({ entities }: EntityMapProps) {
  return (
    <section className="space-y-4" aria-label="Entity map">
      <div className="flex items-center gap-2">
        <Target className="h-5 w-5 text-indigo-400" />
        <h3 className="text-lg font-semibold tracking-tight text-white md:text-xl">Entity map</h3>
        <span className="ml-auto rounded-md border border-white/10 bg-white/[0.04] px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-[var(--text-muted)]">
          NER · Sentiment
        </span>
      </div>
      {entities.length === 0 ? (
        <EmptyPanel message="No entities extracted for this run." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {entities.map((e, i) => (
            <EntityCard key={`${e.entity}-${i}`} entity={e} index={i} />
          ))}
        </div>
      )}
    </section>
  )
}

function EntityCard({ entity: e, index }: { entity: EntitySentiment; index: number }) {
  const pct = normalizeScore(e.score)
  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, type: 'spring', stiffness: 380, damping: 28 }}
      whileHover={{
        y: -4,
        scale: 1.02,
        boxShadow:
          '0 0 0 1px rgba(129, 140, 248, 0.18), 0 16px 40px -12px rgba(0,0,0,0.45)',
      }}
      className="glass-panel relative overflow-hidden rounded-2xl border border-white/[0.07] p-5"
    >
      <div className="absolute right-3 top-3 h-16 w-16 rounded-full bg-indigo-500/5 blur-2xl" />
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <h4 className="truncate text-lg font-semibold text-white">{e.entity}</h4>
          <p className="text-[11px] uppercase tracking-wider text-[var(--text-muted)]">
            {e.entity_type || 'Entity'}
          </p>
        </div>
        <span
          className={`shrink-0 rounded-lg border px-2.5 py-1 text-xs font-semibold capitalize ${sentimentBadgeClass(e.sentiment)}`}
        >
          {e.sentiment}
        </span>
      </div>
      <div className="mt-4">
        <div className="mb-1.5 flex justify-between text-[11px] text-[var(--text-muted)]">
          <span>Sentiment score</span>
          <span className="font-mono tabular-nums text-zinc-300">{pct.toFixed(0)}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-black/40 ring-1 ring-white/[0.06]">
          <motion.div
            className={`h-full rounded-full bg-gradient-to-r ${scoreBarGradient(e.sentiment)}`}
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1], delay: 0.05 * index }}
          />
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between border-t border-white/[0.06] pt-3 text-xs text-[var(--text-muted)]">
        <span>Mentions</span>
        <span className="font-mono text-indigo-200">{e.mentions}</span>
      </div>
    </motion.article>
  )
}

// ─── Conflicts ─────────────────────────────────────────────────────

type ConflictProps = { conflicts: ConflictItem[] }

export function ConflictDetectionSection({ conflicts }: ConflictProps) {
  return (
    <section className="space-y-4" aria-label="Conflict detection">
      <div className="flex items-center gap-2">
        <ShieldAlert className="h-5 w-5 text-amber-400" />
        <h3 className="text-lg font-semibold tracking-tight text-white md:text-xl">
          Conflict detection
        </h3>
      </div>
      {conflicts.length === 0 ? (
        <EmptyPanel message="No narrative conflicts flagged for this topic." />
      ) : (
        <div className="space-y-4">
          {conflicts.map((c, i) => (
            <ConflictCard key={i} c={c} index={i} />
          ))}
        </div>
      )}
    </section>
  )
}

function severityStyles(sev: string): string {
  const x = sev.toLowerCase()
  if (x.includes('high') || x.includes('critical'))
    return 'border-rose-500/45 bg-rose-500/15 text-rose-100'
  if (x.includes('low') || x.includes('minor'))
    return 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200'
  return 'border-amber-500/40 bg-amber-500/12 text-amber-100'
}

function ConflictCard({ c, index }: { c: ConflictItem; index: number }) {
  const sev = c.severity || 'medium'
  return (
    <motion.article
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{
        y: -3,
        scale: 1.01,
        boxShadow:
          '0 0 0 1px rgba(167, 139, 250, 0.15), 0 14px 36px -12px rgba(0,0,0,0.4)',
      }}
      className="glass-panel rounded-2xl border border-white/[0.07] p-5 md:p-6"
    >
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <span className="rounded-lg border border-violet-500/30 bg-violet-500/10 px-2.5 py-1 text-xs font-medium text-violet-200">
          {c.conflict_type || 'Conflict'}
        </span>
        <span
          className={`rounded-lg border px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${severityStyles(sev)}`}
        >
          {sev}
        </span>
        {c.entity && (
          <span className="text-xs text-[var(--text-muted)]">Entity: {c.entity}</span>
        )}
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-rose-500/15 bg-gradient-to-br from-rose-500/[0.07] to-transparent p-4">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-rose-200/80">
            Claim A
          </p>
          <p className="mt-1 text-xs text-[var(--text-muted)]">{c.source_a || 'Source A'}</p>
          <p className="mt-2 text-sm leading-relaxed text-zinc-100">{c.claim_a || '—'}</p>
        </div>
        <div className="rounded-xl border border-emerald-500/15 bg-gradient-to-br from-emerald-500/[0.07] to-transparent p-4">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-emerald-200/80">
            Claim B
          </p>
          <p className="mt-1 text-xs text-[var(--text-muted)]">{c.source_b || 'Source B'}</p>
          <p className="mt-2 text-sm leading-relaxed text-zinc-100">{c.claim_b || '—'}</p>
        </div>
      </div>
      {c.explanation && (
        <p className="mt-4 border-t border-white/[0.06] pt-4 text-sm leading-relaxed text-[var(--text-muted)]">
          {c.explanation}
        </p>
      )}
    </motion.article>
  )
}

// ─── Emotional register ────────────────────────────────────────────

function registerWeights(emotion_type: string, intensity: number): {
  opportunity: number
  risk: number
  neutral: number
} {
  const i = Math.max(0, Math.min(1, intensity))
  const r = (emotion_type || 'neutral').toLowerCase()
  let opportunity = 0.25
  let risk = 0.25
  let neutral = 0.35
  if (r.includes('opportunity')) {
    opportunity = 0.45 + i * 0.4
    risk = 0.1
    neutral = 0.2
  } else if (r.includes('crisis')) {
    risk = 0.45 + i * 0.4
    opportunity = 0.1
    neutral = 0.2
  } else if (r.includes('uncertainty')) {
    neutral = 0.35 + i * 0.35
    opportunity = 0.18
    risk = 0.18
  } else {
    neutral = 0.45 + i * 0.25
    opportunity = 0.15
    risk = 0.15
  }
  const sum = opportunity + risk + neutral
  return {
    opportunity: opportunity / sum,
    risk: risk / sum,
    neutral: neutral / sum,
  }
}

type EmotionalProps = { emotional: EmotionalRegister | null }

export function EmotionalRegisterSection({ emotional }: EmotionalProps) {
  if (!emotional || Object.keys(emotional).length === 0) {
    return (
      <section className="space-y-4" aria-label="Emotional register">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-cyan-400" />
          <h3 className="text-lg font-semibold tracking-tight text-white md:text-xl">
            Emotional register
          </h3>
        </div>
        <EmptyPanel message="Emotional calibration not available for this run." />
      </section>
    )
  }

  const w = registerWeights(emotional.emotion_type, emotional.intensity)
  const opp = emotional.opportunity_signals ?? []
  const unc = emotional.uncertainty_signals ?? []
  const crisis = emotional.crisis_signals ?? []

  return (
    <section className="space-y-4" aria-label="Emotional register">
      <div className="flex items-center gap-2">
        <Activity className="h-5 w-5 text-cyan-400" />
        <h3 className="text-lg font-semibold tracking-tight text-white md:text-xl">
          Emotional register
        </h3>
        <span className="ml-auto rounded-md border border-cyan-500/25 bg-cyan-500/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-cyan-200/90">
          {emotional.emotion_type || 'neutral'}
        </span>
      </div>

      <div className="glass-panel rounded-2xl border border-white/[0.07] p-5 md:p-6">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-[11px] font-medium uppercase tracking-wider text-[var(--text-muted)]">
              Intensity
            </p>
            <p className="font-mono text-3xl font-semibold tabular-nums text-white">
              {(emotional.intensity * 100).toFixed(0)}
              <span className="text-lg text-[var(--text-muted)]">%</span>
            </p>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-black/30 px-3 py-1.5 text-xs text-[var(--text-muted)]">
            <Radar className="h-4 w-4 text-cyan-400" />
            Opportunity / Risk / Neutral
          </div>
        </div>

        <div className="space-y-3">
          <RegisterBar label="Opportunity" value={w.opportunity} color="from-emerald-500 to-teal-400" />
          <RegisterBar label="Risk" value={w.risk} color="from-rose-500 to-orange-500" />
          <RegisterBar label="Neutral" value={w.neutral} color="from-zinc-500 to-zinc-400" />
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <SignalList title="Opportunity signals" items={opp} icon={Sparkles} tone="text-emerald-300/90" />
          <SignalList title="Uncertainty signals" items={unc} icon={AlertTriangle} tone="text-amber-200/90" />
          <SignalList title="Risk signals" items={crisis} icon={ShieldAlert} tone="text-rose-300/90" />
        </div>

        {emotional.tone_guidance && (
          <p className="mt-6 border-t border-white/[0.06] pt-4 text-sm leading-relaxed text-zinc-400">
            <span className="text-[var(--text-muted)]">Tone guidance: </span>
            {emotional.tone_guidance}
          </p>
        )}
      </div>
    </section>
  )
}

function RegisterBar({
  label,
  value,
  color,
}: {
  label: string
  value: number
  color: string
}) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs">
        <span className="text-[var(--text-muted)]">{label}</span>
        <span className="font-mono tabular-nums text-zinc-300">{(value * 100).toFixed(0)}%</span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-black/45 ring-1 ring-white/[0.06]">
        <motion.div
          className={`h-full rounded-full bg-gradient-to-r ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${value * 100}%` }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        />
      </div>
    </div>
  )
}

function SignalList({
  title,
  items,
  icon: Icon,
  tone,
}: {
  title: string
  items: string[]
  icon: ComponentType<{ className?: string }>
  tone: string
}) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-black/20 p-4">
      <div className={`mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider ${tone}`}>
        <Icon className="h-3.5 w-3.5" />
        {title}
      </div>
      {items.length === 0 ? (
        <p className="text-xs text-[var(--text-muted)]">None listed</p>
      ) : (
        <ul className="space-y-1.5">
          {items.map((s, i) => (
            <li key={i} className="text-sm leading-snug text-zinc-300">
              · {s}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

// ─── Story arc chart ───────────────────────────────────────────────

function StoryArcLineChart({ entry }: { entry: StoryArcEntry }) {
  const trend = entry.trend ?? []
  const w = 100
  const h = 56
  const pad = 4

  if (trend.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center text-xs text-[var(--text-muted)]">
        No trend points
      </div>
    )
  }

  const scores = trend.map((t) => normalizeScore(t.score) / 100)
  const n = Math.max(1, scores.length - 1)
  const points = scores.map((sc, i) => ({
    x: pad + (i / n) * (w - pad * 2),
    y: pad + (1 - sc) * (h - pad * 2),
  }))

  const pathD = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`)
    .join(' ')

  const areaD =
    points.length > 0
      ? `${pathD} L ${points[points.length - 1].x.toFixed(2)} ${h - pad} L ${points[0].x.toFixed(2)} ${h - pad} Z`
      : ''

  const gid = `arc-${entry.entity.replace(/\W/g, '').slice(0, 24) || 'e'}-${entry.latest_update?.slice(0, 8) || '0'}`

  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      className="h-32 w-full text-indigo-400"
      preserveAspectRatio="none"
      aria-hidden
    >
      <defs>
        <linearGradient id={`${gid}-fill`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="rgb(99, 102, 241)" stopOpacity="0.35" />
          <stop offset="100%" stopColor="rgb(99, 102, 241)" stopOpacity="0" />
        </linearGradient>
        <linearGradient id={`${gid}-line`} x1="0" x2="1" y1="0" y2="0">
          <stop offset="0%" stopColor="rgb(129, 140, 248)" />
          <stop offset="100%" stopColor="rgb(168, 85, 247)" />
        </linearGradient>
      </defs>
      {areaD && <path d={areaD} fill={`url(#${gid}-fill)`} />}
      <path
        d={pathD}
        fill="none"
        stroke={`url(#${gid}-line)`}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
      {points.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="2.2" className="fill-white" opacity="0.9" />
      ))}
    </svg>
  )
}

type StoryArcProps = { entries: StoryArcEntry[] }

export function StoryArcSection({ entries }: StoryArcProps) {
  return (
    <section className="space-y-4" aria-label="Story arc">
      <div className="flex items-center gap-2">
        <GitBranch className="h-5 w-5 text-violet-400" />
        <h3 className="text-lg font-semibold tracking-tight text-white md:text-xl">Story arc</h3>
        <span className="ml-auto text-[10px] font-medium uppercase tracking-wider text-[var(--text-muted)]">
          Sentiment vs time
        </span>
      </div>
      {entries.length === 0 ? (
        <EmptyPanel message="No temporal entity trends yet. Story arc builds across sessions in the knowledge store." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {entries.map((entry, i) => (
            <motion.article
              key={`${entry.entity}-${i}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-panel overflow-hidden rounded-2xl border border-white/[0.07]"
            >
              <div className="border-b border-white/[0.06] px-5 py-4">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="font-semibold text-white">{entry.entity}</h4>
                    <p className="text-[11px] text-[var(--text-muted)]">{entry.entity_type}</p>
                  </div>
                  <span className="rounded-md border border-violet-500/30 bg-violet-500/10 px-2 py-1 font-mono text-[10px] text-violet-200">
                    {entry.shift}
                  </span>
                </div>
              </div>
              <div className="bg-black/20 px-2 pt-2">
                <StoryArcLineChart entry={entry} />
              </div>
              <div className="flex flex-wrap gap-3 border-t border-white/[0.06] px-5 py-3 text-[11px] text-[var(--text-muted)]">
                {entry.trend.map((t, j) => (
                  <span key={j} className="rounded bg-white/[0.04] px-2 py-0.5 font-mono text-zinc-400">
                    {t.period?.slice(0, 16) || '—'} · {t.sentiment} · {normalizeScore(t.score).toFixed(0)}%
                  </span>
                ))}
              </div>
            </motion.article>
          ))}
        </div>
      )}
    </section>
  )
}

function EmptyPanel({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-white/12 bg-white/[0.02] px-6 py-10 text-center text-sm text-[var(--text-muted)]">
      {message}
    </div>
  )
}

// ─── Combined dashboard ────────────────────────────────────────────

type Props = {
  data: AnalyzeResponse
}

export function IntelligenceAnalytics({ data }: Props) {
  const entities = data.entity_sentiments ?? []
  const conflicts = data.conflicts ?? []
  const emotional = data.emotional_register ?? null
  const storyRaw = data.story_arc
  const story: StoryArcEntry[] = Array.isArray(storyRaw)
    ? storyRaw.filter(
        (x): x is StoryArcEntry =>
          x != null &&
          typeof x === 'object' &&
          'entity' in x &&
          Array.isArray((x as StoryArcEntry).trend),
      )
    : []

  return (
    <div className="space-y-12 border-t border-white/[0.06] pt-12">
      <ScrollReveal>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-indigo-500/30 bg-indigo-500/10">
              <BarChart3 className="h-6 w-6 text-indigo-300" />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-white md:text-3xl">
                Agent analytics
              </h2>
              <p className="mt-1 text-sm text-[var(--text-muted)]">
                Entity map, conflict detection, emotional register, and story arc — live from the pipeline.
              </p>
            </div>
          </div>
        </div>
      </ScrollReveal>

      <ScrollReveal delay={0.04}>
        <EntityMapSection entities={entities} />
      </ScrollReveal>
      <ScrollReveal delay={0.08}>
        <ConflictDetectionSection conflicts={conflicts} />
      </ScrollReveal>
      <ScrollReveal delay={0.1}>
        <EmotionalRegisterSection emotional={emotional} />
      </ScrollReveal>
      <ScrollReveal delay={0.12}>
        <StoryArcSection entries={story} />
      </ScrollReveal>
    </div>
  )
}
