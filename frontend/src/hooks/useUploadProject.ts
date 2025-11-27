import { useMutation, useQueryClient } from '@tanstack/react-query'
import { uploadProjectZip } from '../api/projects'

export const useUploadProject = (projectId: string | null) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (file: File) => {
      if (!projectId) throw new Error('No project selected')
      return uploadProjectZip(projectId, file)
    },
    onSuccess: () => {
      // Invalidate files query to refresh file list
      queryClient.invalidateQueries({ queryKey: ['files', projectId] })
    },
  })
}

