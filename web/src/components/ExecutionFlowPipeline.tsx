import { motion } from 'framer-motion'
import {
  Activity,
  AlertTriangle,
  Brain,
  Check,
  ChevronRight,
  Download,
  Heart,
  Send,
  ShieldCheck,
  Split,
  Users,
  Video,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { Fragment, useEffect, useRef } from 'react'
import type { AnalyzeResponse } from '@/types/api'

const STEPS: { id: string; label: string; Icon: LucideIcon }[] = [
  { id: 'fetch', label: 'Fetch', Icon: Download },
  { id: 'entity', label: 'Entity', Icon: Users },
  { id: 'angle', label: 'Angle', Icon: Split },
  { id: 'analysis', label: 'Analysis', Icon: Brain },
  { id: 'compliance', label: 'Compliance', Icon: ShieldCheck },
  { id: 'personalization', label: 'Personalization', Icon: Heart },
  { id: 'conflict', label: 'Conflict', Icon: AlertTriangle },
  { id: 'emotion', label: 'Emotion', Icon: Activity },
  { id: 'video', label: 'Video', Icon: Video },
  { id: 'delivery', label: 'Delivery', Icon: Send },
]

function metricForStep(index: number, data: AnalyzeResponse | null): string {
  if (!data) return '—'
  const b = data.briefing
  switch (index) {
    case 0:
      return `${data.articles_fetched} sources`
    case 1:
      return `${data.entity_sentiments?.length ?? 0} entities`
    case 2:
      return `${data.angle_clusters?.length ?? 0} angles`
    case 3:
      return `${data.articles_verified} verified`
    case 4:
      return b?.compliance_status === 'Passed' ? 'SEC Compliant' : 'Warning'
    case 5:
      return data.user_profile?.persona_preset || 'User persona'
    case 6:
      return `${data.conflicts?.length ?? 0} conflicts`
    case 7:
      return data.emotional_register?.emotion_type || 'neutral'
    case 8:
      return `${b?.videos?.length ?? 0} clips`
    case 9:
      return b?.audio_url ? 'audio ready' : 'brief ready'
    default:
      return '—'
  }
}

type StepPhase = 'pending' | 'loading' | 'completed' | 'failed'

function stepPhase(
  index: number,
  activeIndex: number,
  loading: boolean,
  success: boolean,
  failed: boolean,
): StepPhase {
  if (failed && loading === false && !success) {
    if (index < activeIndex) return 'completed'
    if (index === activeIndex) return 'failed'
    return 'pending'
  }
  if (!loading && success) return 'completed'
  if (loading) {
    if (index < activeIndex) return 'completed'
    if (index === activeIndex) return 'loading'
    return 'pending'
  }
  return 'pending'
}

type Props = {
  activeIndex: number
  loading: boolean
  data: AnalyzeResponse | null
  analyzeFailed: boolean
}

export function ExecutionFlowPipeline({ activeIndex, loading, data, analyzeFailed }: Props) {
  const success = Boolean(data?.success && data?.briefing)
  const failed = analyzeFailed && !success
  const progressPct =
    loading || success
      ? success
        ? 100
        : ((activeIndex + 1) / STEPS.length) * 100
      : failed
      ? Math.max(0, (activeIndex / STEPS.length) * 100)
      : 0

  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (loading && activeIndex >= 0 && scrollRef.current) {
      const container = scrollRef.current
      const activeEl = container.querySelector(`[data-step-index="${activeIndex}"]`)
      if (activeEl) {
        activeEl.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'center',
        })
      }
    }
  }, [activeIndex, loading])

  return (
    <div className="relative w-full">
      <div className="relative mb-4 h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06] ring-1 ring-white/[0.04]">
        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-400 shadow-[0_0_14px_-2px_rgba(99,102,241,0.55)]"
          initial={false}
          animate={{ width: `${progressPct}%` }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
        />
      </div>
      <div
        ref={scrollRef}
        className="scroll-thin flex items-stretch gap-1 overflow-x-auto pb-2 pt-1 md:gap-2 md:pb-3"
      >
        {STEPS.map((step, i) => {
          const Icon = step.Icon
          const phase = stepPhase(i, activeIndex, loading, success, failed)
          const isActive = phase === 'loading'
          const isDone = phase === 'completed'
          const isFailed = phase === 'failed'
          const metricResolved =
            success && data
              ? metricForStep(i, data)
              : isActive
                ? '…'
                : isDone && loading
                  ? '…'
                  : '—'

          const statusLabel =
            phase === 'loading'
              ? 'Loading'
              : phase === 'completed'
                ? 'Completed'
                : phase === 'failed'
                  ? 'Stopped'
                  : 'Pending'

          return (
            <Fragment key={step.id}>
              <motion.div
                initial={false}
                animate={{
                  scale: isActive ? 1.05 : isDone ? 1.01 : 1,
                }}
                transition={{ type: 'spring', stiffness: 440, damping: 26 }}
                className="relative z-10 min-w-[132px] shrink-0 sm:min-w-[148px]"
                data-step-index={i}
              >
                <div
                  className={[
                    'relative flex h-full min-h-[168px] flex-col rounded-2xl border p-3 transition-shadow duration-300 sm:min-h-[176px] sm:p-4',
                    isActive
                      ? 'glow-ring border-indigo-400/55 bg-gradient-to-b from-indigo-500/20 to-violet-950/30 shadow-[0_0_32px_-4px_rgba(99,102,241,0.55)]'
                      : isDone
                        ? 'border-emerald-500/35 bg-emerald-500/[0.07] shadow-[0_0_20px_-8px_rgba(52,211,153,0.2)]'
                        : isFailed
                          ? 'border-rose-500/45 bg-rose-500/10'
                          : 'border-white/[0.08] bg-black/25 opacity-[0.72]',
                  ].join(' ')}
                >
                  {isActive && (
                    <motion.span
                      className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-r from-indigo-500/0 via-indigo-400/25 to-violet-500/0"
                      animate={{ opacity: [0.25, 0.95, 0.25], x: ['-30%', '30%', '-30%'] }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                    />
                  )}

                  <div className="relative z-10 flex items-start justify-between gap-2">
                    <motion.div
                      className={[
                        'flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border sm:h-10 sm:w-10',
                        isActive
                          ? 'border-indigo-400/50 bg-indigo-500/25 text-indigo-100 shadow-[0_0_20px_-2px_rgba(99,102,241,0.7)]'
                          : isDone
                            ? 'border-emerald-500/35 bg-emerald-500/15 text-emerald-200'
                            : isFailed
                              ? 'border-rose-400/40 bg-rose-500/15 text-rose-200'
                              : 'border-white/10 bg-white/[0.04] text-zinc-500',
                      ].join(' ')}
                      animate={
                        isActive
                          ? { filter: ['brightness(1)', 'brightness(1.4)', 'brightness(1)'] }
                          : {}
                      }
                      transition={
                        isActive ? { duration: 1.25, repeat: Infinity, ease: 'easeInOut' } : {}
                      }
                    >
                      <Icon className="h-4 w-4 sm:h-[18px] sm:w-[18px]" strokeWidth={1.75} />
                    </motion.div>
                    <div className="flex h-6 w-6 shrink-0 items-center justify-center">
                      {isDone && (
                        <motion.span
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ type: 'spring', stiffness: 500, damping: 24 }}
                          className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/25 text-emerald-300 ring-1 ring-emerald-400/40"
                        >
                          <Check className="h-3.5 w-3.5" strokeWidth={3} />
                        </motion.span>
                      )}
                      {isFailed && (
                        <span className="text-xs font-bold text-rose-300">!</span>
                      )}
                    </div>
                  </div>

                  <p className="relative z-10 mt-3 text-sm font-semibold tracking-tight text-white">
                    {step.label}
                  </p>
                  <p
                    className={[
                      'relative z-10 mt-1 text-[10px] font-medium uppercase tracking-wider sm:text-[11px]',
                      isActive ? 'text-indigo-200' : isDone ? 'text-emerald-200/90' : 'text-[var(--text-muted)]',
                    ].join(' ')}
                  >
                    {statusLabel}
                  </p>
                  <p className="relative z-10 mt-2 truncate font-mono text-[10px] text-zinc-400 sm:text-xs">
                    {metricResolved}
                  </p>
                </div>
              </motion.div>

              {i < STEPS.length - 1 && (
                <motion.div
                  className={[
                    'flex shrink-0 items-center self-center px-0.5 md:px-1',
                    i < activeIndex || success
                      ? 'text-emerald-400/75'
                      : activeIndex === i
                        ? 'text-indigo-400'
                        : 'text-indigo-500/30',
                  ].join(' ')}
                  animate={{
                    scale: activeIndex === i && loading ? [1, 1.2, 1] : 1,
                    opacity: activeIndex === i && loading ? [0.7, 1, 0.7] : 1,
                  }}
                  transition={{
                    duration: 1,
                    repeat: activeIndex === i && loading ? Infinity : 0,
                    ease: 'easeInOut',
                  }}
                >
                  <ChevronRight className="h-4 w-4 md:h-5 md:w-5" />
                </motion.div>
              )}
            </Fragment>
          )
        })}
      </div>
    </div>
  )
}
