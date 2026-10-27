import { useState } from 'react'
import { Table2, Download } from 'lucide-react'
import { buildSheet } from '../../api/client'
import type { SheetResultResponse } from '../../types'
import {
  PanelShell, Card, SubmitButton, ErrorBox, Input, Textarea, MarkdownBlock, CopyButton,
} from './PanelShell'

const THREAD_KEY = 'tf_thread_sheet'

function CsvTable({ csv }: { csv: string }) {
  const rows = csv.trim().split('\n').map((r) => r.split(',').map((c) => c.trim().replace(/^"|"$/g, '')))
  if (rows.length < 2) return <MarkdownBlock content={csv} />
  const [header, ...body] = rows
  return (
    <div className="overflow-x-auto rounded-xl border border-white/10">
      <table className="min-w-full text-xs">
        <thead>
          <tr className="border-b border-white/10 bg-white/5">
            {header.map((h, i) => (
              <th key={i} className="px-3 py-2 text-left font-semibold text-white/70">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {body.map((row, ri) => (
            <tr key={ri} className="border-b border-white/5 odd:bg-white/[0.02]">
              {row.map((cell, ci) => (
                <td key={ci} className="px-3 py-2 text-white/60">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function SheetPanel() {
  const [topic, setTopic] = useState('')
  const [requirements, setRequirements] = useState('')
  const [result, setResult] = useState<SheetResultResponse | null>(null)
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
      const data = await buildSheet(topic.trim(), requirements.trim(), threadId)
      if (data.thread_id) localStorage.setItem(THREAD_KEY, data.thread_id)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to build sheet')
    } finally {
      setLoading(false)
    }
  }

  const downloadCsv = () => {
    if (!result) return
    const blob = new Blob([result.csv_content], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${result.topic.replace(/\s+/g, '_')}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <PanelShell
      title="Sheet Builder"
      subtitle="Describe a dataset — get a structured CSV spreadsheet with real data."
    >
      <Card className="mb-6">
        <form onSubmit={submit} className="space-y-4">
          <Input
            label="Topic"
            value={topic}
            onChange={setTopic}
            placeholder="Monthly household budget tracker"
            required
          />
          <Textarea
            label="Requirements (optional)"
            value={requirements}
            onChange={setRequirements}
            placeholder="Track income, expenses by category, savings goal, variance…"
            rows={3}
          />
          <SubmitButton loading={loading}>
            <Table2 className="h-4 w-4" />
            {loading ? 'Building…' : 'Build Sheet'}
          </SubmitButton>
        </form>
      </Card>

      {error && <ErrorBox message={error} />}

      {result && (
        <div className="space-y-4">
          <Card>
            <h3 className="mb-2 text-sm font-semibold text-white">Summary</h3>
            <p className="text-sm text-white/60">{result.summary}</p>
          </Card>
          <Card>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">{result.topic}</h3>
              <div className="flex gap-2">
                <CopyButton text={result.csv_content} />
                <button
                  onClick={downloadCsv}
                  className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/50 transition hover:bg-white/10 hover:text-white"
                >
                  <Download className="h-3 w-3" /> CSV
                </button>
              </div>
            </div>
            <CsvTable csv={result.csv_content} />
            <p className="mt-3 text-right text-xs text-white/20">Thread: {result.thread_id}</p>
          </Card>
        </div>
      )}
    </PanelShell>
  )
}
