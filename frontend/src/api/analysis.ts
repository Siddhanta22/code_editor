import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export const fetchUsage = async (projectId: string, symbolName: string, filePath: string) => {
  const res = await axios.get(`${API_BASE}/projects/${projectId}/usage`, {
    params: { symbol_name: symbolName, file_path: filePath },
  })
  return res.data
}

export const fetchImpact = async (
  projectId: string,
  symbolName: string,
  filePath: string,
  changeDescription?: string
) => {
  const res = await axios.post(`${API_BASE}/projects/${projectId}/impact`, {
    symbol_name: symbolName,
    file_path: filePath,
    change_description: changeDescription || '',
  })
  return res.data
}

