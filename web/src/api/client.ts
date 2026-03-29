import type { AnalyzeResponse } from '@/types/api'

export async function fetchHealth(): Promise<{ status: string; agents: string[] }> {
  const r = await fetch('/health')
  if (!r.ok) throw new Error('Health check failed')
  return r.json()
}

export async function fetchPersonas(): Promise<{
  personas: { name: string; description: string }[]
  custom_persona_supported: boolean
}> {
  const r = await fetch('/personas')
  if (!r.ok) throw new Error('Failed to load personas')
  return r.json()
}

export async function fetchLanguages(): Promise<{
  languages: { code: string; name: string }[]
}> {
  const r = await fetch('/languages')
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
  const r = await fetch('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail ?? r.statusText)
  }
  return r.json()
}
