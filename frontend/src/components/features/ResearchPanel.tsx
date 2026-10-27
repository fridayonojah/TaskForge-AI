import { useState } from 'react'
import { Search } from 'lucide-react'
import { researchIndustry } from '../../api/client'
import { useJobPoller } from '../../hooks/useJobPoller'
import type { ResearchResultData } from '../../types'
import {
  PanelShell, Card, SubmitButton, ErrorBox, Input, StatusPill, MarkdownBlock, CopyButton,
} from './PanelShell'

const THREAD_KEY = 'tf_thread_research'

const QUICK_INDUSTRIES = ['Fintech', 'Healthcare AI', 'Electric Vehicles', 'E-commerce', 'Cybersecurity']

export function ResearchPanel() {
  const [industry, setIndustry] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { status, result, error: pollError, isPolling, startPolling, reset } = useJobPoller()

  const threadId = localStorage.getItem(THREAD_KEY) ?? undefined

  const submit = async (e: { preventDefault(): void }) => {
    e.preventDefault()
    if (!industry.trim()) return
    setError(null)
    reset()
    setLoading(true)
    try {
      const { job_id } = await researchIndustry(industry.trim(), threadId)
      startPolling(job_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start research')
    } finally {
      setLoading(false)
    }
  }

  const data = result as ResearchResultData | null
  if (data?.thread_id) localStorage.setItem(THREAD_KEY, data.thread_id)

  const displayError = error ?? pollError

  return (
    <PanelShell
      title="Industry Research"
      subtitle="Enter an industry and get a deep analysis: trends, key players, and strategic insights."
    >
      <Card className="mb-6">
        <form onSubmit={submit} className="space-y-4">
          <Input
            label="Industry"
            value={industry}
            onChange={setIndustry}
            placeholder="Fintech, Healthcare AI, Electric Vehicles…"
            required
          />

          <div className="flex flex-wrap gap-2">
            {QUICK_INDUSTRIES.map((ind) => (
              <button
                key={ind}
                type="button"
                onClick={() => setIndustry(ind)}
                className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/50 transition hover:bg-white/10 hover:text-white"
              >
                {ind}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <SubmitButton loading={loading || isPolling}>
              <Search className="h-4 w-4" />
              {isPolling ? 'Researching…' : 'Research'}
            </SubmitButton>
            {status && <StatusPill status={status} />}
          </div>
        </form>
      </Card>

      {displayError && <ErrorBox message={displayError} />}

      {data && (
        <div className="space-y-4">
          {data.summary && (
            <Card>
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white">Summary</h3>
                <CopyButton text={data.summary} />
              </div>
              <MarkdownBlock content={data.summary} />
            </Card>
          )}
          {data.trends && (
            <Card>
              <h3 className="mb-3 text-sm font-semibold text-white">Trends</h3>
              <MarkdownBlock content={data.trends} />
            </Card>
          )}
          {data.key_players && (
            <Card>
              <h3 className="mb-3 text-sm font-semibold text-white">Key Players</h3>
              <MarkdownBlock content={data.key_players} />
            </Card>
          )}
          <p className="text-right text-xs text-white/20">Thread: {data.thread_id}</p>
        </div>
      )}
    </PanelShell>
  )
}
