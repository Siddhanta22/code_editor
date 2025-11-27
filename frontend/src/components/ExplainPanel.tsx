import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { explainCode } from '../api/explain'

interface ExplainPanelProps {
  projectId: number | null
  selectedCode: string | null
  filePath: string | null
  language?: string
}

export default function ExplainPanel({
  projectId,
  selectedCode,
  filePath,
  language,
}: ExplainPanelProps) {
  const [explanation, setExplanation] = useState<string | null>(null)

  const explainMutation = useMutation({
    mutationFn: async (code: string) => {
      const response = await explainCode({
        code,
        file_path: filePath || undefined,
        language: language || undefined,
      })
      return response
    },
    onSuccess: (data) => {
      setExplanation(data.explanation)
    },
  })

  const handleExplain = () => {
    if (!selectedCode || !selectedCode.trim()) {
      alert('Please select some code to explain')
      return
    }

    explainMutation.mutate(selectedCode)
  }

  if (!projectId) {
    return (
      <div className="p-4 text-gray-400 text-sm">
        Select a project and some code to explain
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={handleExplain}
          disabled={!selectedCode || explainMutation.isPending}
          className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {explainMutation.isPending ? 'Explaining...' : 'Explain Selected Code'}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {explainMutation.isError && (
          <div className="text-red-400 text-sm mb-4">
            Error: Failed to explain code
          </div>
        )}

        {explanation && (
          <div className="prose prose-invert max-w-none">
            <h3 className="text-white font-semibold mb-2">Explanation</h3>
            <div className="text-gray-300 text-sm whitespace-pre-wrap">{explanation}</div>
          </div>
        )}

        {!explanation && !explainMutation.isPending && (
          <div className="text-gray-400 text-sm">
            Select code in the editor and click "Explain Selected Code"
          </div>
        )}
      </div>
    </div>
  )
}

