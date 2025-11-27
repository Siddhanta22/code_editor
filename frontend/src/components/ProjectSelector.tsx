import { useState, useEffect } from 'react'
import { useProjects } from '../hooks/useProjects'
import { useUploadProject } from '../hooks/useUploadProject'

interface ProjectSelectorProps {
  selectedProject: number | null
  onSelectProject: (id: number | null) => void
}

export default function ProjectSelector({ selectedProject, onSelectProject }: ProjectSelectorProps) {
  const { projects, isLoading, createProject } = useProjects()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')
  const { mutate: uploadZip, isPending: isUploading } = useUploadProject(
    selectedProject?.toString() || null
  )

  const handleCreate = async () => {
    if (!newProjectName.trim()) return
    try {
      const project = await createProject({ name: newProjectName, description: '' })
      onSelectProject(project.id)
      setNewProjectName('')
      setShowCreateModal(false)
    } catch (error) {
      console.error('Error creating project:', error)
      alert('Failed to create project')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.name.endsWith('.zip')) {
      alert('Please select a ZIP file')
      return
    }
    uploadZip(file, {
      onSuccess: () => {
        alert('Project uploaded and indexed successfully!')
      },
      onError: (error: any) => {
        alert(`Failed to upload project: ${error.message || 'Unknown error'}`)
      },
    })
    // Reset input
    e.target.value = ''
  }

  return (
    <div className="flex items-center gap-2">
      <select
        value={selectedProject || ''}
        onChange={(e) => onSelectProject(e.target.value ? parseInt(e.target.value) : null)}
        className="px-3 py-1 bg-gray-700 border border-gray-600 rounded text-sm focus:outline-none focus:border-blue-500"
      >
        <option value="">Select Project</option>
        {projects.map((project) => (
          <option key={project.id} value={project.id}>
            {project.name}
          </option>
        ))}
      </select>
      <button
        onClick={() => setShowCreateModal(true)}
        className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
      >
        + New
      </button>
      {selectedProject && (
        <label className="inline-flex items-center gap-1 cursor-pointer text-xs">
          <span className="px-2 py-1 border border-gray-600 rounded bg-gray-700 hover:bg-gray-600 text-sm">
            {isUploading ? 'Uploading...' : 'Upload ZIP'}
          </span>
          <input
            type="file"
            accept=".zip"
            className="hidden"
            onChange={handleFileChange}
            disabled={isUploading}
          />
        </label>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h3 className="text-lg font-semibold mb-4">Create New Project</h3>
            <input
              type="text"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              placeholder="Project name"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded mb-4 focus:outline-none focus:border-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleCreate()}
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

