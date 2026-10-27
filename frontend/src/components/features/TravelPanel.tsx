import { useState } from 'react'
import { Plane } from 'lucide-react'
import { planTravel } from '../../api/client'
import { useJobPoller } from '../../hooks/useJobPoller'
import type { TravelPlanResult } from '../../types'
import {
  PanelShell, Card, SubmitButton, ErrorBox, StatusPill,
  Textarea, MarkdownBlock, CopyButton,
} from './PanelShell'

const QUICK_PROMPTS = [
  'Plan a 7-day Japan trip from Lagos under $3000',
  'Plan a 5-day Dubai trip from London with flights and hotels',
  'Plan a 10-day Thailand backpacker trip on a budget',
  'Find the cheapest flights from New York to Paris in December',
]

const THREAD_KEY = 'tf_thread_travel'

export function TravelPanel() {
  const [message, setMessage] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { status, result, error: pollError, isPolling, startPolling, reset } = useJobPoller()

  const threadId = localStorage.getItem(THREAD_KEY) ?? undefined

  const submit = async (e: { preventDefault(): void }) => {
    e.preventDefault()
    if (!message.trim()) return
    setError(null)
    reset()
    setLoading(true)
    try {
      const { job_id } = await planTravel(message.trim(), threadId)
      startPolling(job_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to queue job')
    } finally {
      setLoading(false)
    }
  }

  const plan = result as TravelPlanResult | null
  if (plan?.thread_id) localStorage.setItem(THREAD_KEY, plan.thread_id)

  const displayError = error ?? pollError

  return (
    <PanelShell
      title="Trip Planner"
      subtitle="Describe your trip — get real flights, hotels, and a day-by-day itinerary."
    >
      <Card className="mb-6">
        <form onSubmit={submit} className="space-y-4">
          <Textarea
            label="Where do you want to go?"
            value={message}
            onChange={setMessage}
            placeholder="Plan a 7-day trip to Japan from Lagos..."
            rows={3}
            required
          />

          {/* Quick prompts */}
          <div className="flex flex-wrap gap-2">
            {QUICK_PROMPTS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setMessage(p)}
                className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/50 transition hover:bg-white/10 hover:text-white"
              >
                {p}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <SubmitButton loading={loading || isPolling}>
              <Plane className="h-4 w-4" />
              {isPolling ? 'Planning…' : 'Generate Plan'}
            </SubmitButton>
            {status && <StatusPill status={status} />}
          </div>
        </form>
      </Card>

      {displayError && <ErrorBox message={displayError} />}

      {plan && (
        <div className="space-y-4">
          {plan.answer && (
            <Card>
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white">Overview</h3>
                <CopyButton text={plan.answer} />
              </div>
              <MarkdownBlock content={plan.answer} />
            </Card>
          )}
          {plan.flight_results && (
            <Card>
              <h3 className="mb-3 text-sm font-semibold text-white">Flights</h3>
              <MarkdownBlock content={plan.flight_results} />
            </Card>
          )}
          {plan.hotel_results && (
            <Card>
              <h3 className="mb-3 text-sm font-semibold text-white">Hotels</h3>
              <MarkdownBlock content={plan.hotel_results} />
            </Card>
          )}
          {plan.itinerary && (
            <Card>
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white">Day-by-Day Itinerary</h3>
                <CopyButton text={plan.itinerary} />
              </div>
              <MarkdownBlock content={plan.itinerary} />
            </Card>
          )}
          <p className="text-right text-xs text-white/20">
            Thread: {plan.thread_id} · {plan.llm_calls} LLM calls
          </p>
        </div>
      )}
    </PanelShell>
  )
}
