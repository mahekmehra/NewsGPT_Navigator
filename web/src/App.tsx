import { useCallback, useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { TopBar } from '@/components/TopBar'
import { Sidebar } from '@/components/Sidebar'
import { SettingsPanel } from '@/components/SettingsPanel'
import { PIPELINE_STEP_COUNT } from '@/config/pipeline'
import { DashboardView } from '@/views/DashboardView'
import { EntityMapView } from '@/views/EntityMapView'
import { PersonaCompareView } from '@/views/PersonaCompareView'
import { ConflictsView } from '@/views/ConflictsView'
import { TimelineView } from '@/views/TimelineView'
import { VideosView } from '@/views/VideosView'
import { analyzeTopic, fetchHealth, fetchLanguages, fetchPersonas } from '@/api/client'
import type { AnalyzeResponse } from '@/types/api'
import type { SectionId } from '@/types/navigation'

export default function App() {
  const [section, setSection] = useState<SectionId>('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [settingsOpen, setSettingsOpen] = useState(false)

  const [agentsOnline, setAgentsOnline] = useState(false)
  const [personas, setPersonas] = useState<{ name: string; description: string }[]>([
    { name: 'General', description: '' },
  ])
  const [languages, setLanguages] = useState<{ code: string; name: string }[]>([
    { code: 'en', name: 'English' },
  ])

  const [persona, setPersona] = useState('General')
  const [language, setLanguage] = useState('en')

  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [pipelineStep, setPipelineStep] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AnalyzeResponse | null>(null)

  const [personaA, setPersonaA] = useState('Investor')
  const [personaB, setPersonaB] = useState('Student')
  const [compareLoading, setCompareLoading] = useState(false)
  const [compareError, setCompareError] = useState<string | null>(null)
  const [compareLeft, setCompareLeft] = useState<AnalyzeResponse | null>(null)
  const [compareRight, setCompareRight] = useState<AnalyzeResponse | null>(null)

  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    fetchHealth()
      .then((h) => setAgentsOnline(h.status === 'ok'))
      .catch(() => setAgentsOnline(false))

    fetchPersonas()
      .then((p) => {
        if (p.personas?.length) setPersonas(p.personas)
      })
      .catch(() => {})

    fetchLanguages()
      .then((l) => {
        if (l.languages?.length) setLanguages(l.languages)
      })
      .catch(() => {})
  }, [])

  const clearPipelineTimer = () => {
    if (tickRef.current) {
      clearInterval(tickRef.current)
      tickRef.current = null
    }
  }

  const startPipelineAnimation = useCallback(() => {
    clearPipelineTimer()
    setPipelineStep(0)
    tickRef.current = setInterval(() => {
      setPipelineStep((s) => {
        if (s >= PIPELINE_STEP_COUNT - 1) return s
        return s + 1
      })
    }, 1500)
  }, [])

  useEffect(() => {
    return () => clearPipelineTimer()
  }, [])

  const handleAnalyze = async () => {
    setError(null)
    setResult(null)
    setLoading(true)
    startPipelineAnimation()
    try {
      const data = await analyzeTopic({
        topic: topic.trim(),
        persona,
        language,
      })
      setResult(data)
      setPipelineStep(PIPELINE_STEP_COUNT - 1)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Analysis failed')
      setResult(null)
    } finally {
      clearPipelineTimer()
      setLoading(false)
    }
  }

  const handleCompare = async () => {
    setCompareError(null)
    setCompareLoading(true)
    setCompareLeft(null)
    setCompareRight(null)
    try {
      const left = await analyzeTopic({
        topic: topic.trim(),
        persona: personaA,
        language,
      })
      setCompareLeft(left)
      const right = await analyzeTopic({
        topic: topic.trim(),
        persona: personaB,
        language,
      })
      setCompareRight(right)
    } catch (e) {
      setCompareError(e instanceof Error ? e.message : 'Compare failed')
    } finally {
      setCompareLoading(false)
    }
  }

  const briefing = result?.briefing

  return (
    <div className="mesh-bg flex min-h-screen flex-col">
      <TopBar agentsOnline={agentsOnline} onOpenSettings={() => setSettingsOpen(true)} />

      <div className="flex min-h-0 flex-1">
        <Sidebar
          expanded={sidebarOpen}
          section={section}
          onToggle={() => setSidebarOpen((v) => !v)}
          onSelect={setSection}
        />

        <motion.main
          className="scroll-thin min-h-0 flex-1 overflow-y-auto p-4 md:p-8 lg:p-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.35 }}
        >
          <AnimatePresence mode="wait">
            {section === 'dashboard' && (
              <motion.div
                key="dash"
                initial={{ opacity: 0, y: 24, filter: 'blur(10px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                exit={{ opacity: 0, y: -16, filter: 'blur(8px)' }}
                transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
              >
                <DashboardView
                  topic={topic}
                  onTopicChange={setTopic}
                  personas={personas}
                  persona={persona}
                  onPersonaChange={setPersona}
                  languages={languages}
                  language={language}
                  onLanguageChange={setLanguage}
                  onAnalyze={handleAnalyze}
                  loading={loading}
                  pipelineStep={pipelineStep}
                  error={error}
                  data={result}
                />
              </motion.div>
            )}

            {section === 'entity-map' && (
              <motion.div
                key="entity"
                initial={{ opacity: 0, y: 24, filter: 'blur(10px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                exit={{ opacity: 0, y: -16, filter: 'blur(8px)' }}
                transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
              >
                <EntityMapView entities={result?.entity_sentiments ?? []} />
              </motion.div>
            )}

            {section === 'persona-compare' && (
              <motion.div
                key="compare"
                initial={{ opacity: 0, y: 24, filter: 'blur(10px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                exit={{ opacity: 0, y: -16, filter: 'blur(8px)' }}
                transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
              >
                <PersonaCompareView
                  personas={personas}
                  topic={topic}
                  personaA={personaA}
                  personaB={personaB}
                  onPersonaA={setPersonaA}
                  onPersonaB={setPersonaB}
                  onCompare={handleCompare}
                  loading={compareLoading}
                  left={compareLeft}
                  right={compareRight}
                  error={compareError}
                />
              </motion.div>
            )}

            {section === 'conflicts' && (
              <motion.div
                key="conf"
                initial={{ opacity: 0, y: 24, filter: 'blur(10px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                exit={{ opacity: 0, y: -16, filter: 'blur(8px)' }}
                transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
              >
                <ConflictsView conflicts={result?.conflicts ?? []} />
              </motion.div>
            )}

            {section === 'timeline' && (
              <motion.div
                key="time"
                initial={{ opacity: 0, y: 24, filter: 'blur(10px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                exit={{ opacity: 0, y: -16, filter: 'blur(8px)' }}
                transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
              >
                <TimelineView events={briefing?.timeline ?? []} />
              </motion.div>
            )}

            {section === 'videos' && (
              <motion.div
                key="vid"
                initial={{ opacity: 0, y: 24, filter: 'blur(10px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                exit={{ opacity: 0, y: -16, filter: 'blur(8px)' }}
                transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
              >
                <VideosView videos={briefing?.videos ?? []} />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.main>
      </div>

      <SettingsPanel
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        languages={languages}
        language={language}
        onLanguageChange={setLanguage}
      />
    </div>
  )
}
