import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export interface ExplainRequest {
  code: string
  file_path?: string
  language?: string
}

export interface ExplainResponse {
  explanation: string
  complexity?: string
  issues?: string[]
}

export async function explainCode(request: ExplainRequest): Promise<ExplainResponse> {
  const response = await api.post<ExplainResponse>('/explain', request)
  return response.data
}

