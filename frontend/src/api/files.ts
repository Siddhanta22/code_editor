import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export const fetchFiles = async (projectId: string) => {
  const res = await axios.get<string[]>(`${API_BASE}/projects/${projectId}/files`)
  return res.data
}

export const fetchFileContent = async (projectId: string, filePath: string) => {
  const res = await axios.get<{ file_path: string; content: string }>(
    `${API_BASE}/projects/${projectId}/file`,
    { params: { file_path: filePath } }
  )
  return res.data
}

