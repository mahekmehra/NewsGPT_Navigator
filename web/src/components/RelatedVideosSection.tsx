import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play } from 'lucide-react'
import type { VideoItem } from '@/types/api'

function openVideoUrl(url: string) {
  const u = url.trim()
  if (!u) return
  window.open(u, '_blank', 'noopener,noreferrer')
}

function padVideos(videos: VideoItem[], count: number): (VideoItem | null)[] {
  const slice = videos.slice(0, count)
  const out: (VideoItem | null)[] = [...slice]
  while (out.length < count) out.push(null)
  return out
}

type Props = {
  videos: VideoItem[]
}

export function RelatedVideosSection({ videos }: Props) {
  const row = padVideos(videos, 3)

  return (
    <motion.section
      id="briefing-section-videos"
      className="scroll-mt-28 lg:col-span-2"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.14 }}
      aria-label="Related videos"
    >
      <h4 className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">
        Related Videos
      </h4>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {row.map((v, i) => (
          <VideoCard key={v?.url ?? `empty-${i}`} video={v} />
        ))}
      </div>
    </motion.section>
  )
}

function VideoCard({ video }: { video: VideoItem | null }) {
  if (!video?.url) {
    return (
      <div className="flex aspect-video items-center justify-center rounded-2xl border border-dashed border-white/10 bg-white/[0.02] text-xs text-[var(--text-muted)]">
        No video
      </div>
    )
  }

  const title = video.title?.trim() || 'Related clip'
  const thumb = video.thumbnail?.trim()

  const [imgError, setImgError] = useState(false)

  return (
    <motion.a
      href={video.url}
      target="_blank"
      rel="noopener noreferrer"
      onClick={(e) => {
        e.preventDefault()
        openVideoUrl(video.url)
      }}
      className="group relative block aspect-video w-full overflow-hidden rounded-2xl border border-white/[0.08] bg-black/40 shadow-lg outline-none ring-0 transition-[box-shadow,transform,border-color] duration-300 focus-visible:ring-2 focus-visible:ring-indigo-400/60"
      whileHover={{ scale: 1.045 }}
      transition={{ type: 'spring', stiffness: 420, damping: 24 }}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        boxShadow: '0 0 0 1px rgba(255,255,255,0.04) inset',
      }}
    >
      <div
        className="pointer-events-none absolute inset-0 z-20 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{
          boxShadow:
            '0 0 0 1px rgba(129, 140, 248, 0.45), 0 0 32px -4px rgba(99, 102, 241, 0.45)',
        }}
      />

      {thumb && !imgError ? (
        <img
          src={thumb}
          alt=""
          onError={() => setImgError(true)}
          className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-[1.08]"
        />
      ) : (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-zinc-800 to-zinc-950">
          <Play className="h-8 w-8 text-white/20" />
        </div>
      )}

      <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent" />

      <div className="absolute inset-0 z-10 flex items-center justify-center opacity-0 transition duration-300 group-hover:opacity-100">
        <div className="flex h-14 w-14 items-center justify-center rounded-full border border-white/25 bg-black/45 text-white shadow-lg backdrop-blur-sm">
          <Play className="h-7 w-7 fill-white pl-1" />
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 z-10 p-3 pt-8">
        <p className="line-clamp-2 text-left text-sm font-medium leading-snug text-white drop-shadow-md">
          {title}
        </p>
      </div>
    </motion.a>
  )
}
