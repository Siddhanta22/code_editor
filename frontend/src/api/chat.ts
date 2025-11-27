import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export interface ChatResponse {
  answer: string
  references: Array<{
    file_path: string
    line_start: number
    line_end: number
    snippet: string
  }>
}

export async function chatWithProject(projectId: number, message: string): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>(`/projects/${projectId}/chat`, {
    message,
  })
  return response.data
}

