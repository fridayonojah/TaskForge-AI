import { useState } from 'react'
import { FileText, CheckCircle2 } from 'lucide-react'
import { polishResume } from '../../api/client'
import type { ResumeResultResponse } from '../../types'
import {
  PanelShell, Card, SubmitButton, ErrorBox, Textarea, MarkdownBlock, CopyButton,
} from './PanelShell'

const THREAD_KEY = 'tf_thread_resume'

export function ResumePanel() {
  const [resumeText, setResumeText] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [result, setResult] = useState<ResumeResultResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const threadId = localStorage.getItem(THREAD_KEY) ?? undefined

  const submit = async (e: { preventDefault(): void }) => {
    e.preventDefault()
    if (!resumeText.trim()) return
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const data = await polishResume(resumeText.trim(), jobDescription.trim() || undefined, threadId)
      if (data.thread_id) localStorage.setItem(THREAD_KEY, data.thread_id)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to polish resume')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PanelShell
      title="Resume Polish"
      subtitle="Paste your resume and an optional job description — get a rewritten version with improvements."
    >
      <Card className="mb-6">
        <form onSubmit={submit} className="space-y-4">
          <Textarea
            label="Your Resume"
            value={resumeText}
            onChange={setResumeText}
            placeholder="Paste your resume text here…"
            rows={8}
            required
          />
          <Textarea
            label="Job Description (optional)"
            value={jobDescription}
            onChange={setJobDescription}
            placeholder="Paste the job description to tailor your resume…"
            rows={4}
          />
          <SubmitButton loading={loading}>
            <FileText className="h-4 w-4" />
            {loading ? 'Polishing…' : 'Polish Resume'}
          </SubmitButton>
        </form>
      </Card>

      {error && <ErrorBox message={error} />}

      {result && (
        <div className="space-y-4">
          {result.improvements.length > 0 && (
            <Card>
              <h3 className="mb-3 text-sm font-semibold text-white">Improvements Made</h3>
              <ul className="space-y-2">
                {result.improvements.map((imp, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-400" />
                    {imp}
                  </li>
                ))}
              </ul>
            </Card>
          )}
          <Card>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Polished Resume</h3>
              <CopyButton text={result.polished} />
            </div>
            <MarkdownBlock content={result.polished} />
            <p className="mt-3 text-right text-xs text-white/20">Thread: {result.thread_id}</p>
          </Card>
        </div>
      )}
    </PanelShell>
  )
}
