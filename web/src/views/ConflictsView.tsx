import { ConflictDetectionSection } from '@/components/analytics/IntelligenceAnalytics'
import type { ConflictItem } from '@/types/api'

type Props = {
  conflicts: ConflictItem[]
}

export function ConflictsView({ conflicts }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Conflicts</h2>
        <p className="mt-2 text-[var(--text-muted)]">
          Contradictions and tension between narratives — surfaced by the conflict agent.
        </p>
      </div>
      <ConflictDetectionSection conflicts={conflicts} />
    </div>
  )
}
