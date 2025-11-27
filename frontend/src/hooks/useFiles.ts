import { useQuery } from '@tanstack/react-query'
import { fetchFiles, fetchFileContent } from '../api/files'

export const useProjectFiles = (projectId: string | null) =>
  useQuery({
    queryKey: ['files', projectId],
    queryFn: () => {
      if (!projectId) throw new Error('No project selected')
      return fetchFiles(projectId)
    },
    enabled: !!projectId,
  })

export const useFileContent = (projectId: string | null, filePath: string | null) =>
  useQuery({
    queryKey: ['fileContent', projectId, filePath],
    queryFn: () => {
      if (!projectId || !filePath) throw new Error('No project or file selected')
      return fetchFileContent(projectId, filePath)
    },
    enabled: !!projectId && !!filePath,
  })

