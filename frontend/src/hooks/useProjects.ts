import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProjects, createProject as createProjectAPI } from '../api/projects'

export function useProjects() {
  const queryClient = useQueryClient()

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  })

  const createMutation = useMutation({
    mutationFn: createProjectAPI,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })

  return {
    projects,
    isLoading,
    createProject: createMutation.mutateAsync,
  }
}

