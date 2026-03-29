import { motion } from 'framer-motion'
import { GitCompareArrows } from 'lucide-react'
import { GlassCard } from '@/components/GlassCard'
import { RippleButton } from '@/components/RippleButton'
import type { AnalyzeResponse } from '@/types/api'

type Props = {
  personas: { name: string; description: string }[]
  topic: string
  personaA: string
  personaB: string
  onPersonaA: (v: string) => void
  onPersonaB: (v: string) => void
  onCompare: () => void
  loading: boolean
  left: AnalyzeResponse | null
  right: AnalyzeResponse | null
  error: string | null
}

export function PersonaCompareView({
  personas,
  topic,
  personaA,
  personaB,
  onPersonaA,
  onPersonaB,
  onCompare,
  loading,
  left,
  right,
  error,
}: Props) {
  const personaHeadline = (d: AnalyzeResponse | null) => d?.briefing?.persona_brief?.headline ?? '—'
  const personaSummary = (d: AnalyzeResponse | null) => d?.briefing?.persona_brief?.summary ?? ''
  const finalAssessment = (d: AnalyzeResponse | null) => d?.briefing?.persona_brief?.final_assessment ?? ''

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Persona compare</h2>
        <p className="mt-2 text-[var(--text-muted)]">
          Run the same topic through two intelligence presets and compare synthesized briefs.
        </p>
      </div>

      <GlassCard>
        <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr] md:items-end">
          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
              Persona A
            </label>
            <select
              value={personaA}
              onChange={(e) => onPersonaA(e.target.value)}
              className="w-full cursor-pointer rounded-xl border border-white/10 bg-black/35 py-2.5 pl-3 pr-8 text-sm text-white outline-none ring-indigo-500/30 focus:ring-2"
            >
              {personas.map((p) => (
                <option key={p.name} value={p.name}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-center pb-2 md:pb-0">
            <motion.div
              animate={{ rotate: [0, 6, -6, 0] }}
              transition={{ repeat: Infinity, duration: 4, ease: 'easeInOut' }}
              className="rounded-full border border-indigo-500/30 bg-indigo-500/10 p-3 text-indigo-200"
            >
              <GitCompareArrows className="h-6 w-6" />
            </motion.div>
          </div>
          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
              Persona B
            </label>
            <select
              value={personaB}
              onChange={(e) => onPersonaB(e.target.value)}
              className="w-full cursor-pointer rounded-xl border border-white/10 bg-black/35 py-2.5 pl-3 pr-8 text-sm text-white outline-none ring-indigo-500/30 focus:ring-2"
            >
              {personas.map((p) => (
                <option key={p.name} value={p.name}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <RippleButton
          type="button"
          onClick={onCompare}
          disabled={loading || topic.trim().length < 2 || personaA === personaB}
          className="mt-6 w-full rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? 'Running dual analysis…' : 'Compare personas'}
        </RippleButton>

        {error && (
          <p className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {error}
          </p>
        )}
      </GlassCard>

      <div className="grid gap-4 lg:grid-cols-2">
        <GlassCard>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-indigo-300">
            {personaA}
          </h3>
          <p className="mt-2 text-lg font-semibold text-white">{personaHeadline(left)}</p>
          <div className="mt-4 space-y-4">
            <p className="text-sm leading-relaxed text-[var(--text-muted)]">
              {left ? personaSummary(left) : 'Awaiting run.'}
            </p>
            {left?.briefing?.persona_brief?.final_assessment && (
              <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/5 p-4">
                <p className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">Final Assessment</p>
                <p className="mt-1 text-xs italic text-indigo-100/90">{finalAssessment(left)}</p>
              </div>
            )}
          </div>
        </GlassCard>

        <GlassCard>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-violet-300">
            {personaB}
          </h3>
          <p className="mt-2 text-lg font-semibold text-white">{personaHeadline(right)}</p>
          <div className="mt-4 space-y-4">
            <p className="text-sm leading-relaxed text-[var(--text-muted)]">
              {right ? personaSummary(right) : 'Awaiting run.'}
            </p>
            {right?.briefing?.persona_brief?.final_assessment && (
              <div className="rounded-xl border border-violet-500/20 bg-violet-500/5 p-4">
                <p className="text-[10px] font-bold uppercase tracking-widest text-violet-400">Final Assessment</p>
                <p className="mt-1 text-xs italic text-violet-100/90">{finalAssessment(right)}</p>
              </div>
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
