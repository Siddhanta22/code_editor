import { useState } from 'react'
import { useProjectFiles } from '../hooks/useFiles'

interface SidebarProps {
  projectId: number | null
  selectedFile: string | null
  onSelectFile: (file: string) => void
}

export default function Sidebar({ projectId, selectedFile, onSelectFile }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(true)
  const { data: files, isLoading, error } = useProjectFiles(projectId?.toString() || null)

  if (!projectId) {
    return (
      <div className={`${isOpen ? 'w-64' : 'w-12'} bg-gray-800 border-r border-gray-700 transition-all`}>
        <div className="p-4 text-gray-400 text-sm">
          Select a project to view files
        </div>
      </div>
    )
  }

  return (
    <div className={`${isOpen ? 'w-64' : 'w-12'} bg-gray-800 border-r border-gray-700 transition-all flex flex-col`}>
      <div className="p-4 flex items-center justify-between border-b border-gray-700">
        <h2 className="font-semibold text-sm">Files</h2>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="text-gray-400 hover:text-white"
        >
          {isOpen ? '◀' : '▶'}
        </button>
      </div>
      
      {isOpen && (
        <div className="flex-1 overflow-y-auto p-2">
          {isLoading && (
            <div className="p-4 text-gray-400 text-sm">Loading files...</div>
          )}
          
          {error && (
            <div className="p-4 text-red-400 text-sm">
              Error loading files
            </div>
          )}
          
          {files && files.length > 0 ? (
            files.map((file) => (
              <div
                key={file}
                onClick={() => onSelectFile(file)}
                className={`px-3 py-2 text-sm rounded cursor-pointer transition-colors ${
                  selectedFile === file
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                {file}
              </div>
            ))
          ) : (
            !isLoading && (
              <div className="p-4 text-gray-400 text-sm">
                No files found. Upload a ZIP file to get started.
              </div>
            )
          )}
        </div>
      )}
    </div>
  )
}

