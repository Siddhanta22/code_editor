import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export interface Project {
  id: number
  name: string
  description: string | null
  created_at: string
  file_count: number
}

export interface CreateProjectRequest {
  name: string
  description?: string
}

export async function getProjects(): Promise<Project[]> {
  const response = await api.get<Project[]>('/projects')
  return response.data
}

export async function createProject(request: CreateProjectRequest): Promise<Project> {
  const response = await api.post<Project>('/projects', request)
  return response.data
}

export async function uploadProject(projectId: number, file: File): Promise<void> {
  const formData = new FormData()
  formData.append('file', file)
  await api.post(`/projects/${projectId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export const uploadProjectZip = async (projectId: string, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post(
    `/projects/${projectId}/upload`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  )
  return res.data
}

