import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { fetchUsage, fetchImpact } from '../api/analysis'

interface UsageImpactPanelProps {
  projectId: number | null
  defaultSymbolName?: string
  defaultFilePath?: string | null
}

export default function UsageImpactPanel({
  projectId,
  defaultSymbolName = '',
  defaultFilePath = null,
}: UsageImpactPanelProps) {
  const [symbolName, setSymbolName] = useState(defaultSymbolName)
  const [filePath, setFilePath] = useState(defaultFilePath || '')
  const [usageResult, setUsageResult] = useState<any>(null)
  const [impactResult, setImpactResult] = useState<any>(null)

  const usageMutation = useMutation({
    mutationFn: async () => {
      if (!projectId) throw new Error('No project selected')
      return fetchUsage(projectId.toString(), symbolName, filePath)
    },
    onSuccess: (data) => {
      setUsageResult(data)
    },
    onError: () => {
      setUsageResult(null)
    },
  })

  const impactMutation = useMutation({
    mutationFn: async () => {
      if (!projectId) throw new Error('No project selected')
      return fetchImpact(projectId.toString(), symbolName, filePath)
    },
    onSuccess: (data) => {
      setImpactResult(data)
    },
    onError: () => {
      setImpactResult(null)
    },
  })

  const handleShowUsage = () => {
    if (!symbolName.trim() || !filePath.trim()) {
      alert('Please enter symbol name and file path')
      return
    }
    usageMutation.mutate()
  }

  const handleAnalyzeImpact = () => {
    if (!symbolName.trim() || !filePath.trim()) {
      alert('Please enter symbol name and file path')
      return
    }
    impactMutation.mutate()
  }

  if (!projectId) {
    return (
      <div className="p-4 text-gray-400 text-sm">
        Select a project to analyze usage and impact
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-gray-700 space-y-3">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Symbol Name</label>
          <input
            type="text"
            value={symbolName}
            onChange={(e) => setSymbolName(e.target.value)}
            placeholder="function_name or Class.method"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-sm focus:outline-none focus:border-blue-500 text-white"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">File Path</label>
          <input
            type="text"
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
            placeholder="path/to/file.py"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-sm focus:outline-none focus:border-blue-500 text-white"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleShowUsage}
            disabled={usageMutation.isPending || !symbolName.trim() || !filePath.trim()}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {usageMutation.isPending ? 'Loading...' : 'Show Usage'}
          </button>
          <button
            onClick={handleAnalyzeImpact}
            disabled={impactMutation.isPending || !symbolName.trim() || !filePath.trim()}
            className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {impactMutation.isPending ? 'Analyzing...' : 'Analyze Impact'}
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Usage Results */}
        {usageResult && (
          <div>
            <h3 className="text-white font-semibold mb-3 text-sm">Usage</h3>

            {usageMutation.isError && (
              <div className="text-red-400 text-xs mb-2">Error loading usage data</div>
            )}

            {usageResult.symbol && (
              <div className="mb-4">
                <div className="text-gray-400 text-xs mb-2">
                  Symbol: <span className="text-white">{usageResult.symbol.name}</span> (
                  {usageResult.symbol.type})
                </div>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <h4 className="text-gray-300 font-medium text-xs mb-2">
                  Calls ({usageResult.calls?.length || 0})
                </h4>
                {usageResult.calls && usageResult.calls.length > 0 ? (
                  <div className="space-y-1">
                    {usageResult.calls.map((call: any, idx: number) => (
                      <div key={idx} className="text-xs text-gray-400 bg-gray-800 p-2 rounded">
                        <span className="text-white">{call.name}</span> ({call.type}) -{' '}
                        {call.file_path}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs text-gray-500">None</div>
                )}
              </div>

              <div>
                <h4 className="text-gray-300 font-medium text-xs mb-2">
                  Called By ({usageResult.called_by?.length || 0})
                </h4>
                {usageResult.called_by && usageResult.called_by.length > 0 ? (
                  <div className="space-y-1">
                    {usageResult.called_by.map((caller: any, idx: number) => (
                      <div key={idx} className="text-xs text-gray-400 bg-gray-800 p-2 rounded">
                        <span className="text-white">{caller.name}</span> ({caller.type}) -{' '}
                        {caller.file_path}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs text-gray-500">None</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Impact Results */}
        {impactResult && (
          <div>
            <h3 className="text-white font-semibold mb-3 text-sm">Impact Analysis</h3>

            {impactMutation.isError && (
              <div className="text-red-400 text-xs mb-2">Error analyzing impact</div>
            )}

            {impactResult.risk_level && (
              <div className="mb-3">
                <span className="text-xs text-gray-400">Risk Level: </span>
                <span
                  className={`text-xs font-semibold ${
                    impactResult.risk_level === 'high'
                      ? 'text-red-400'
                      : impactResult.risk_level === 'medium'
                      ? 'text-yellow-400'
                      : 'text-green-400'
                  }`}
                >
                  {impactResult.risk_level.toUpperCase()}
                </span>
              </div>
            )}

            <div className="mb-3 text-xs text-gray-400">
              Affected: {impactResult.affected_count || 0} symbols | Dependencies:{' '}
              {impactResult.dependency_count || 0}
            </div>

            {impactResult.analysis && (
              <div className="bg-gray-800 p-3 rounded text-xs text-gray-300 whitespace-pre-wrap">
                {impactResult.analysis}
              </div>
            )}

            {impactResult.affected_symbols && impactResult.affected_symbols.length > 0 && (
              <div className="mt-4">
                <h4 className="text-gray-300 font-medium text-xs mb-2">
                  Affected Symbols ({impactResult.affected_symbols.length})
                </h4>
                <div className="space-y-1 max-h-48 overflow-y-auto">
                  {impactResult.affected_symbols.slice(0, 10).map((sym: any, idx: number) => (
                    <div key={idx} className="text-xs text-gray-400 bg-gray-800 p-2 rounded">
                      <span className="text-white">{sym.name}</span> ({sym.type}) - {sym.file_path}
                    </div>
                  ))}
                  {impactResult.affected_symbols.length > 10 && (
                    <div className="text-xs text-gray-500">
                      ... and {impactResult.affected_symbols.length - 10} more
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {!usageResult && !impactResult && (
          <div className="text-gray-400 text-xs text-center py-8">
            Enter symbol name and file path, then click "Show Usage" or "Analyze Impact"
          </div>
        )}
      </div>
    </div>
  )
}

