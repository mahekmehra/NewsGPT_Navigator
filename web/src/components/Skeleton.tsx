import { motion } from 'framer-motion'

function ShimmerBlock({ className = '' }: { className?: string }) {
  return (
    <div
      className={`skeleton-shimmer relative overflow-hidden rounded-md bg-white/[0.07] ${className}`}
    />
  )
}

export function CardSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`glass-panel overflow-hidden rounded-2xl p-5 ${className}`}>
      <ShimmerBlock className="h-4 w-1/3" />
      <ShimmerBlock className="mt-4 h-3 w-full" />
      <ShimmerBlock className="mt-2 h-3 w-5/6" />
    </div>
  )
}

export function GridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  )
}

/** Horizontal pipeline step placeholders */
export function PipelineSkeleton() {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 pt-1 md:gap-3">
      {Array.from({ length: 9 }).map((_, i) => (
        <div
          key={i}
          className="flex min-w-[120px] shrink-0 flex-col gap-3 rounded-2xl border border-white/[0.06] bg-black/30 p-4 sm:min-w-[136px]"
        >
          <ShimmerBlock className="h-9 w-9 rounded-xl" />
          <ShimmerBlock className="h-3 w-16" />
          <ShimmerBlock className="h-2 w-full rounded-full" />
        </div>
      ))}
    </div>
  )
}

export function PreviewCardsSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="glass-panel rounded-2xl p-5">
          <ShimmerBlock className="h-4 w-24" />
          <ShimmerBlock className="mt-4 h-3 w-full" />
          <ShimmerBlock className="mt-2 h-3 w-4/5" />
          <ShimmerBlock className="mt-4 h-3 w-20" />
        </div>
      ))}
    </div>
  )
}

/** Shown below preview while analysis runs — briefing + analytics placeholders */
export function DashboardAnalyzeSkeleton() {
  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.35 }}
    >
      <div className="glass-panel rounded-2xl p-6 md:p-8">
        <ShimmerBlock className="h-6 w-1/2 max-w-md" />
        <ShimmerBlock className="mt-6 h-4 w-full" />
        <ShimmerBlock className="mt-3 h-4 w-full" />
        <ShimmerBlock className="mt-3 h-4 w-4/5" />
        <div className="mt-8 grid gap-3 sm:grid-cols-2">
          <ShimmerBlock className="h-28 rounded-xl" />
          <ShimmerBlock className="h-28 rounded-xl" />
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <ShimmerBlock className="h-48 rounded-2xl" />
        <ShimmerBlock className="h-48 rounded-2xl" />
      </div>
    </motion.div>
  )
}
