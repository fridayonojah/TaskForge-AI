import { useState } from 'react'
import { Presentation } from 'lucide-react'
import { createSlides } from '../../api/client'
import type { SlidesDeckResponse } from '../../types'
import {
  PanelShell, Card, SubmitButton, ErrorBox, Input, MarkdownBlock, CopyButton,
} from './PanelShell'

const THREAD_KEY = 'tf_thread_slides'

export function SlidesPanel() {
  const [topic, setTopic] = useState('')
  const [numSlides, setNumSlides] = useState(8)
  const [result, setResult] = useState<SlidesDeckResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const threadId = localStorage.getItem(THREAD_KEY) ?? undefined

  const submit = async (e: { preventDefault(): void }) => {
    e.preventDefault()
    if (!topic.trim()) return
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const data = await createSlides(topic.trim(), numSlides, threadId)
      if (data.thread_id) localStorage.setItem(THREAD_KEY, data.thread_id)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate slides')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PanelShell
      title="Slide Creator"
      subtitle="Enter a topic and get a fully structured slide deck in Markdown."
    >
      <Card className="mb-6">
        <form onSubmit={submit} className="space-y-4">
          <Input
            label="Topic"
            value={topic}
            onChange={setTopic}
            placeholder="The Future of AI in Healthcare"
            required
          />

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-white/50">
              Number of slides: <span className="text-white">{numSlides}</span>
            </label>
            <input
              type="range"
              min={4}
              max={20}
              value={numSlides}
              onChange={(e) => setNumSlides(Number(e.target.value))}
              className="w-full accent-blue-500"
            />
            <div className="flex justify-between text-[10px] text-white/20">
              <span>4</span><span>20</span>
            </div>
          </div>

          <SubmitButton loading={loading}>
            <Presentation className="h-4 w-4" />
            {loading ? 'Generating…' : 'Create Slides'}
          </SubmitButton>
        </form>
      </Card>

      {error && <ErrorBox message={error} />}

      {result && (
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">{result.topic}</h3>
            <CopyButton text={result.slides_markdown} />
          </div>
          <MarkdownBlock content={result.slides_markdown} />
          <p className="mt-3 text-right text-xs text-white/20">Thread: {result.thread_id}</p>
        </Card>
      )}
    </PanelShell>
  )
}
