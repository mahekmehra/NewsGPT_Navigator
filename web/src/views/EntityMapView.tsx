import { EntityMapSection } from '@/components/analytics/IntelligenceAnalytics'
import type { EntitySentiment } from '@/types/api'

type Props = {
  entities: EntitySentiment[]
}

export function EntityMapView({ entities }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Entity map</h2>
        <p className="mt-2 text-[var(--text-muted)]">
          Named entities and sentiment signals extracted across sources.
        </p>
      </div>
      <EntityMapSection entities={entities} />
    </div>
  )
}
