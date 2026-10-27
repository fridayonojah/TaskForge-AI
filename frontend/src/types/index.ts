export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed'

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface RegisterResponse {
  id: string
  email: string
}

export interface JobEnqueuedResponse {
  job_id: string
  status: string
  message: string
}

export interface JobStatusResponse {
  job_id: string
  job_type: string
  status: JobStatus
  result: Record<string, unknown> | null
  error: string | null
}

export interface TravelPlanResult {
  success: boolean
  thread_id: string
  answer: string
  flight_results: string
  hotel_results: string
  itinerary: string
  llm_calls: number
}

export interface SlidesDeckResponse {
  success: boolean
  topic: string
  slides_markdown: string
  thread_id: string
}

export interface ResumeResultResponse {
  success: boolean
  polished: string
  improvements: string[]
  thread_id: string
}

export interface SheetResultResponse {
  success: boolean
  topic: string
  csv_content: string
  summary: string
  thread_id: string
}

export interface ResearchResultData {
  industry: string
  summary: string
  trends: string
  key_players: string
  thread_id: string
}

export type Feature = 'travel' | 'slides' | 'resume' | 'sheet' | 'research'
