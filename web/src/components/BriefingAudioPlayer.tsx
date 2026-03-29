import { useCallback, useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Pause, Play } from 'lucide-react'

function resolveAudioSrc(url: string): string {
  const u = url.trim()
  if (!u) return ''
  if (u.startsWith('http://') || u.startsWith('https://')) return u
  return u.startsWith('/') ? u : `/${u}`
}

function formatTime(sec: number): string {
  if (!Number.isFinite(sec) || sec < 0) return '0:00'
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

type Props = {
  audioUrl: string | null | undefined
}

export function BriefingAudioPlayer({ audioUrl }: Props) {
  const src = audioUrl ? resolveAudioSrc(audioUrl) : ''
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const barRef = useRef<HTMLDivElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [duration, setDuration] = useState(0)
  const [current, setCurrent] = useState(0)

  const toggle = useCallback(() => {
    const el = audioRef.current
    if (!el || !src) return
    if (el.paused) {
      void el.play().catch(() => {})
    } else {
      el.pause()
    }
  }, [src])

  useEffect(() => {
    const el = audioRef.current
    if (!el) return

    const onPlay = () => setIsPlaying(true)
    const onPause = () => setIsPlaying(false)
    const onEnded = () => setIsPlaying(false)
    const onTime = () => setCurrent(el.currentTime)
    const onMeta = () => setDuration(el.duration || 0)

    el.addEventListener('play', onPlay)
    el.addEventListener('pause', onPause)
    el.addEventListener('ended', onEnded)
    el.addEventListener('timeupdate', onTime)
    el.addEventListener('loadedmetadata', onMeta)

    return () => {
      el.removeEventListener('play', onPlay)
      el.removeEventListener('pause', onPause)
      el.removeEventListener('ended', onEnded)
      el.removeEventListener('timeupdate', onTime)
      el.removeEventListener('loadedmetadata', onMeta)
    }
  }, [src])

  const seek = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const el = audioRef.current
      const bar = barRef.current
      if (!el || !bar || !duration) return
      const rect = bar.getBoundingClientRect()
      const x = Math.min(Math.max(0, e.clientX - rect.left), rect.width)
      el.currentTime = (x / rect.width) * duration
    },
    [duration],
  )

  if (!src) return null

  const progress = duration > 0 ? (current / duration) * 100 : 0

  return (
    <motion.section
      id="briefing-section-audio"
      className="scroll-mt-28 lg:col-span-2"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.16 }}
      aria-label="Briefing audio"
    >
      <audio ref={audioRef} src={src} preload="metadata" />

      <div className="glass-panel rounded-2xl border border-white/[0.06] p-5 md:p-6">
        <div className="flex flex-col gap-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-4">
            <motion.button
              type="button"
              onClick={toggle}
              aria-pressed={isPlaying}
              className="flex shrink-0 items-center justify-center gap-2.5 rounded-xl border border-indigo-500/40 bg-gradient-to-r from-indigo-600/45 to-violet-600/35 px-6 py-3 text-sm font-semibold text-white shadow-[0_0_28px_-8px_rgba(99,102,241,0.5)] transition hover:border-indigo-400/55 hover:shadow-[0_0_36px_-6px_rgba(129,140,248,0.45)]"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isPlaying ? (
                <>
                  <Pause className="h-5 w-5 shrink-0" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="h-5 w-5 shrink-0 pl-0.5" />
                  Listen to Briefing
                </>
              )}
            </motion.button>

            <div className="min-w-0 flex-1">
              <div
                ref={barRef}
                role="slider"
                tabIndex={0}
                aria-valuenow={Math.round(current)}
                aria-valuemin={0}
                aria-valuemax={Math.round(duration)}
                className="group relative h-2 cursor-pointer rounded-full bg-white/[0.08]"
                onClick={seek}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    toggle()
                  }
                }}
              >
                <div
                  className="absolute left-0 top-0 h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-[width] duration-100 ease-linear"
                  style={{ width: `${progress}%` }}
                />
                <div
                  className="pointer-events-none absolute top-1/2 h-3.5 w-3.5 -translate-y-1/2 rounded-full border-2 border-white bg-indigo-400 opacity-0 shadow-md transition group-hover:opacity-100"
                  style={{ left: `calc(${progress}% - 7px)` }}
                />
              </div>
              <div className="mt-1.5 flex justify-between font-mono text-[11px] tabular-nums text-[var(--text-muted)]">
                <span>{formatTime(current)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>

            <Waveform active={isPlaying} />
          </div>
        </div>
      </div>
    </motion.section>
  )
}

function Waveform({ active }: { active: boolean }) {
  const bars = 16
  const pattern = [
    0.2, 0.95, 0.45, 1, 0.55, 0.88, 0.32, 0.92, 0.5, 0.78, 0.38, 0.85, 0.62, 0.72, 0.28, 0.98,
  ]
  return (
    <div
      className="flex h-11 shrink-0 items-end justify-center gap-[2px] sm:w-[128px] sm:justify-end"
      aria-hidden
    >
      {Array.from({ length: bars }).map((_, i) => (
        <motion.div
          key={i}
          className="w-[3px] origin-bottom rounded-full bg-gradient-to-t from-indigo-600/90 to-violet-400/90"
          style={{ height: 32 }}
          animate={active ? { scaleY: pattern[i % pattern.length] } : { scaleY: 0.1 }}
          transition={
            active
              ? {
                  duration: 0.28 + (i % 5) * 0.04,
                  repeat: Infinity,
                  repeatType: 'reverse',
                  ease: [0.45, 0, 0.55, 1],
                  delay: i * 0.022,
                }
              : { duration: 0.25 }
          }
        />
      ))}
    </div>
  )
}
