import type { AnalyzeResponse } from '@/types/api'

const API_ORIGIN = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') ?? ''
const API_BASE = `${API_ORIGIN}/api`

export async function fetchHealth(): Promise<{ status: string; agents: string[] }> {
  const r = await fetch(`${API_BASE}/health`)
  if (!r.ok) throw new Error('Health check failed')
  return r.json()
}

export async function fetchPersonas(): Promise<{
  personas: { name: string; description: string }[]
  custom_persona_supported: boolean
}> {
  const r = await fetch(`${API_BASE}/personas`)
  if (!r.ok) throw new Error('Failed to load personas')
  return r.json()
}

export async function fetchLanguages(): Promise<{
  languages: { code: string; name: string }[]
}> {
  const r = await fetch(`${API_BASE}/languages`)
  if (!r.ok) throw new Error('Failed to load languages')
  return r.json()
}

export async function analyzeTopic(body: {
  topic: string
  persona: string
  language: string
  knowledge_session_id?: string
  custom_persona?: string
}): Promise<AnalyzeResponse> {
  // Step 1: enqueue job
  const enqueue = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!enqueue.ok) {
    const err = await enqueue.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail ?? enqueue.statusText)
  }

  const { job_id } = (await enqueue.json()) as { job_id: string }

  // Step 2: poll for result with simple backoff
  const maxAttempts = 60 // up to ~60s
  let attempt = 0

  // Small initial delay so backend can start work
  await new Promise((res) => setTimeout(res, 500))

  while (attempt < maxAttempts) {
    attempt += 1
    const r = await fetch(`${API_BASE}/analyze/${job_id}`)
    if (!r.ok) {
      const err = await r.json().catch(() => ({}))
      throw new Error((err as { detail?: string }).detail ?? r.statusText)
    }

    const data = (await r.json()) as AnalyzeResponse

    if (data.pipeline_status === 'completed') return data
    if (data.pipeline_status === 'failed') {
      throw new Error(data.error || 'Analysis failed')
    }

    // Still running — wait a bit longer each time, capped to 2s
    const delay = Math.min(2000, 250 + attempt * 100)
    await new Promise((res) => setTimeout(res, delay))
  }

  throw new Error('Analysis is taking longer than expected. Please try again.')
}
