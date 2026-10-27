import type {
  TokenResponse,
  RegisterResponse,
  JobEnqueuedResponse,
  JobStatusResponse,
  SlidesDeckResponse,
  ResumeResultResponse,
  SheetResultResponse,
} from '../types'

const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function authHeader(): Record<string, string> {
  const token = localStorage.getItem('tf_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(),
      ...(init.headers as Record<string, string> | undefined),
    },
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail ?? res.statusText)
  }
  return res.json() as Promise<T>
}

// ── Auth ─────────────────────────────────────────────────────────────────────

export function register(email: string, password: string) {
  return request<RegisterResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function login(email: string, password: string) {
  const body = new URLSearchParams({ username: email, password })
  return fetch(`${BASE}/api/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  }).then(async (res) => {
    if (!res.ok) {
      const data = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(data.detail ?? res.statusText)
    }
    return res.json() as Promise<TokenResponse>
  })
}

// ── Jobs ─────────────────────────────────────────────────────────────────────

export function getJob(jobId: string) {
  return request<JobStatusResponse>(`/api/jobs/${jobId}`)
}

// ── Travel ───────────────────────────────────────────────────────────────────

export function planTravel(message: string, threadId?: string) {
  return request<JobEnqueuedResponse>('/api/travel', {
    method: 'POST',
    body: JSON.stringify({ message, thread_id: threadId }),
  })
}

// ── Slides ───────────────────────────────────────────────────────────────────

export function createSlides(topic: string, numSlides: number, threadId?: string) {
  return request<SlidesDeckResponse>('/api/slides', {
    method: 'POST',
    body: JSON.stringify({ topic, num_slides: numSlides, thread_id: threadId }),
  })
}

// ── Resume ───────────────────────────────────────────────────────────────────

export function polishResume(resumeText: string, jobDescription?: string, threadId?: string) {
  return request<ResumeResultResponse>('/api/resume/polish', {
    method: 'POST',
    body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription, thread_id: threadId }),
  })
}

// ── Sheet ────────────────────────────────────────────────────────────────────

export function buildSheet(topic: string, requirements: string, threadId?: string) {
  return request<SheetResultResponse>('/api/sheet', {
    method: 'POST',
    body: JSON.stringify({ topic, requirements, thread_id: threadId }),
  })
}

// ── Research ─────────────────────────────────────────────────────────────────

export function researchIndustry(industry: string, threadId?: string) {
  return request<JobEnqueuedResponse>('/api/research', {
    method: 'POST',
    body: JSON.stringify({ industry, thread_id: threadId }),
  })
}
