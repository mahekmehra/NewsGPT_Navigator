export interface VideoItem {
  title: string
  url: string
  thumbnail: string
}

export interface PersonaBrief {
  headline: string
  summary: string
  key_points: string[]
  final_assessment: string
  confidence_score: string
  risks: string[]
  next_steps: string[]
  source_quality_summary: string
  insights: string[]
}

export interface Briefing {
  title: string
  summary: string
  persona_brief: PersonaBrief
  angles: Record<string, string>
  follow_up_questions: string[]
  timeline: { date: string; event: string; url?: string; source_title?: string }[]
  prediction: string
  key_entities: string[]
  entities_metadata?: { entity: string; entity_articles?: { title: string; url: string }[] }[]
  sentiment: string
  sources: { title: string; source: string; url: string }[]
  persona: string
  language: string
  videos: VideoItem[]
  audio_url: string | null
  bias_score?: number
  compliance_status?: string
}

export interface EntitySentiment {
  entity: string
  entity_type: string
  sentiment: string
  score: number
  mentions: number
}

export interface ConflictItem {
  conflict_type: string
  claim_a: string
  source_a: string
  claim_b: string
  source_b: string
  entity: string
  severity: string
  explanation: string
}

export interface EmotionalRegister {
  emotion_type: string
  intensity: number
  tone_guidance: string
  crisis_signals?: string[]
  opportunity_signals?: string[]
  uncertainty_signals?: string[]
}

export interface StoryArcTrendPoint {
  period: string
  sentiment: string
  score: number
}

export interface StoryArcEntry {
  entity: string
  entity_type: string
  trend: StoryArcTrendPoint[]
  shift: string
  first_seen: string
  latest_update: string
}
  
export interface UserProfile {
  persona_preset: string
  interests: string[]
  knowledge_level: string
  risk_appetite: string
  jargon_comfort: string
  preferred_depth: string
}

export interface AnalyzeResponse {
  success: boolean
  briefing: Briefing | null
  entity_sentiments: EntitySentiment[]
  angle_clusters: unknown[]
  user_profile: UserProfile | null
  conflicts: ConflictItem[]
  emotional_register: EmotionalRegister | null
  story_arc: StoryArcEntry[]
  audit_trail: unknown[]
  error: string
  pipeline_status: string
  articles_fetched: number
  articles_verified: number
  verified_articles: unknown[]
}

export interface PersonaInfo {
  name: string
  description: string
}

export interface CompareResponse {
  success: boolean
  left: AnalyzeResponse | null
  right: AnalyzeResponse | null
  error: string
}
