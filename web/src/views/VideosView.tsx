import { motion } from 'framer-motion'
import { ExternalLink, Play } from 'lucide-react'
import { GlassCard } from '@/components/GlassCard'
import type { VideoItem } from '@/types/api'

type Props = {
  videos: VideoItem[]
}

export function VideosView({ videos }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Related Videos</h2>
        <p className="mt-2 text-[var(--text-muted)]">
          Curated video surfaces from the video intelligence layer.
        </p>
      </div>

      {videos.length === 0 ? (
        <GlassCard className="border-dashed border-white/15">
          <p className="text-center text-sm text-[var(--text-muted)]">
            Video links attach to briefings when the pipeline finds relevant clips.
          </p>
        </GlassCard>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {videos.map((v, i) => (
            <motion.a
              key={v.url || i}
              href={v.url}
              target="_blank"
              rel="noreferrer"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="group block"
            >
              <GlassCard className="h-full overflow-hidden !p-0">
                <div className="relative aspect-video bg-black/50">
                  {v.thumbnail ? (
                    <img
                      src={v.thumbnail}
                      alt=""
                      className="h-full w-full object-cover opacity-90 transition group-hover:opacity-100"
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center text-[var(--text-muted)]">
                      <Play className="h-12 w-12" />
                    </div>
                  )}
                  <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 transition group-hover:opacity-100">
                    <ExternalLink className="h-8 w-8 text-white" />
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="line-clamp-2 font-medium text-white">{v.title}</h3>
                </div>
              </GlassCard>
            </motion.a>
          ))}
        </div>
      )}
    </div>
  )
}
