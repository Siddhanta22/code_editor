// This file is deprecated - use useFiles.ts instead
// Keeping for backwards compatibility if needed
export function useProjectFiles(projectId: number | null) {
  return {
    files: [],
    isLoading: false,
  }
}

