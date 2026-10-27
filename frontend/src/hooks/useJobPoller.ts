import { useState, useEffect, useRef } from 'react'
import { getJob } from '../api/client'
import type { JobStatus, JobStatusResponse } from '../types'

interface UseJobPollerResult {
  status: JobStatus | null
  result: Record<string, unknown> | null
  error: string | null
  isPolling: boolean
  startPolling: (jobId: string) => void
  reset: () => void
}

const POLL_INTERVAL_MS = 2500

export function useJobPoller(): UseJobPollerResult {
  const [jobId, setJobId] = useState<string | null>(null)
  const [job, setJob] = useState<JobStatusResponse | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPolling = () => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  useEffect(() => {
    if (!jobId) return

    const poll = async () => {
      try {
        const data = await getJob(jobId)
        setJob(data)
        if (data.status === 'completed' || data.status === 'failed') {
          stopPolling()
        }
      } catch {
        stopPolling()
      }
    }

    poll()
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS)

    return stopPolling
  }, [jobId])

  const startPolling = (id: string) => {
    setJob(null)
    setJobId(id)
  }

  const reset = () => {
    stopPolling()
    setJobId(null)
    setJob(null)
  }

  return {
    status: job?.status ?? null,
    result: job?.result ?? null,
    error: job?.error ?? null,
    isPolling: !!jobId && job?.status !== 'completed' && job?.status !== 'failed',
    startPolling,
    reset,
  }
}
