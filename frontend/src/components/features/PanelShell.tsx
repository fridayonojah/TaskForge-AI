import type { ReactNode } from 'react'
import { Loader2, AlertCircle } from 'lucide-react'
import { cn } from '../../lib/utils'

interface PanelShellProps {
  title: string
  subtitle: string
  children: ReactNode
}

export function PanelShell({ title, subtitle, children }: PanelShellProps) {
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <div className="mb-8">
        <h2 className="bg-gradient-to-r from-white via-sky-200 to-purple-300 bg-clip-text text-2xl font-bold text-transparent">
          {title}
        </h2>
        <p className="mt-1 text-sm text-white/40">{subtitle}</p>
      </div>
      {children}
    </div>
  )
}

interface CardProps {
  children: ReactNode
  className?: string
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn('rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl', className)}>
      {children}
    </div>
  )
}

export function SubmitButton({ loading, children }: { loading: boolean; children: ReactNode }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition hover:opacity-90 disabled:opacity-60"
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin" />}
      {children}
    </button>
  )
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
      {message}
    </div>
  )
}

export function StatusPill({ status }: { status: string }) {
  const styles: Record<string, string> = {
    queued: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/20',
    processing: 'bg-blue-500/15 text-blue-400 border-blue-500/20',
    completed: 'bg-green-500/15 text-green-400 border-green-500/20',
    failed: 'bg-red-500/15 text-red-400 border-red-500/20',
  }
  return (
    <span className={cn('inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium', styles[status] ?? 'bg-white/10 text-white/50 border-white/10')}>
      {status === 'processing' && <Loader2 className="h-3 w-3 animate-spin" />}
      {status}
    </span>
  )
}

export function Textarea({
  label,
  value,
  onChange,
  placeholder,
  rows = 4,
  required,
}: {
  label: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
  rows?: number
  required?: boolean
}) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-white/50">{label}</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
        required={required}
        className="w-full resize-none rounded-xl border border-white/10 bg-white/5 px-3.5 py-2.5 text-sm text-white placeholder-white/20 outline-none transition focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30"
      />
    </div>
  )
}

export function Input({
  label,
  value,
  onChange,
  placeholder,
  required,
  type = 'text',
}: {
  label: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
  required?: boolean
  type?: string
}) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-white/50">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="w-full rounded-xl border border-white/10 bg-white/5 px-3.5 py-2.5 text-sm text-white placeholder-white/20 outline-none transition focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30"
      />
    </div>
  )
}

export function MarkdownBlock({ content }: { content: string }) {
  return (
    <pre className="overflow-x-auto whitespace-pre-wrap break-words rounded-xl border border-white/10 bg-black/30 p-4 font-mono text-xs leading-relaxed text-white/80">
      {content}
    </pre>
  )
}

export function CopyButton({ text }: { text: string }) {
  const copy = () => navigator.clipboard.writeText(text)
  return (
    <button
      onClick={copy}
      className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/50 transition hover:bg-white/10 hover:text-white"
    >
      Copy
    </button>
  )
}
