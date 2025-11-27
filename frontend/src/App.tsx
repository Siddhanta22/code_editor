import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import MonacoEditor from './components/MonacoEditor'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'
import ProjectSelector from './components/ProjectSelector'
import ExplainPanel from './components/ExplainPanel'
import UsageImpactPanel from './components/UsageImpactPanel'
import { useFileContent } from './hooks/useFiles'

const queryClient = new QueryClient()

function App() {
  const [selectedProject, setSelectedProject] = useState<number | null>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [selectedCode, setSelectedCode] = useState<string | null>(null)
  const [selectedLanguage, setSelectedLanguage] = useState<string>('')
  const [rightPanelTab, setRightPanelTab] = useState<'chat' | 'explain' | 'analysis'>('chat')

  // Load file content from API
  const { data: fileData } = useFileContent(
    selectedProject?.toString() || null,
    selectedFile
  )

  const fileContent = fileData?.content || ''

  const handleSelectionChange = (code: string | null, language: string) => {
    setSelectedCode(code)
    setSelectedLanguage(language)
    if (code) {
      setRightPanelTab('explain')
    }
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="h-screen flex flex-col bg-gray-900 text-white">
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700 px-4 py-2">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold">IntelliForge</h1>
            <ProjectSelector
              selectedProject={selectedProject}
              onSelectProject={setSelectedProject}
            />
          </div>
        </header>

        {/* Main content area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <Sidebar
            projectId={selectedProject}
            selectedFile={selectedFile}
            onSelectFile={(file) => {
              setSelectedFile(file)
            }}
          />

          {/* Editor area */}
          <div className="flex-1 flex flex-col">
            <MonacoEditor
              filePath={selectedFile || 'untitled'}
              value={fileContent}
              onChange={() => {}} // Read-only for now
              onSelectionChange={handleSelectionChange}
            />
          </div>

          {/* Right panel with tabs */}
          <div className="w-80 flex flex-col border-l border-gray-700 bg-gray-800">
            <div className="flex text-xs border-b border-gray-700">
              <button
                className={`flex-1 px-3 py-2 text-left ${
                  rightPanelTab === 'chat'
                    ? 'bg-gray-700 font-semibold text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white'
                }`}
                onClick={() => setRightPanelTab('chat')}
              >
                Chat
              </button>
              <button
                className={`flex-1 px-3 py-2 text-left ${
                  rightPanelTab === 'explain'
                    ? 'bg-gray-700 font-semibold text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white'
                }`}
                onClick={() => setRightPanelTab('explain')}
              >
                Explain
              </button>
              <button
                className={`flex-1 px-3 py-2 text-left ${
                  rightPanelTab === 'analysis'
                    ? 'bg-gray-700 font-semibold text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white'
                }`}
                onClick={() => setRightPanelTab('analysis')}
              >
                Analysis
              </button>
            </div>

            <div className="flex-1 overflow-hidden">
              {rightPanelTab === 'chat' && <ChatPanel projectId={selectedProject} isCompact />}
              {rightPanelTab === 'explain' && (
                <ExplainPanel
                  projectId={selectedProject}
                  selectedCode={selectedCode}
                  filePath={selectedFile}
                  language={selectedLanguage}
                />
              )}
              {rightPanelTab === 'analysis' && (
                <UsageImpactPanel
                  projectId={selectedProject}
                  defaultFilePath={selectedFile}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App

