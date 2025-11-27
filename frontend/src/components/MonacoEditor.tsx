import { Editor } from '@monaco-editor/react'
import { useRef, useMemo } from 'react'

interface MonacoEditorProps {
  filePath: string
  value: string
  onChange: (value: string) => void
  onSelectionChange?: (selectedCode: string | null, language: string) => void
}

export default function MonacoEditor({
  filePath,
  value,
  onChange,
  onSelectionChange,
}: MonacoEditorProps) {
  const editorRef = useRef<any>(null)

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor

    // Listen for selection changes
    editor.onDidChangeCursorSelection(() => {
      if (onSelectionChange && editor) {
        const selection = editor.getSelection()
        const model = editor.getModel()
        
        if (selection && !selection.isEmpty()) {
          const selectedCode = model.getValueInRange(selection)
          const language = model.getLanguageId() || 'python'
          onSelectionChange(selectedCode, language)
        } else {
          onSelectionChange(null, '')
        }
      }
    })
  }

  // Detect language from file extension
  const language = useMemo(() => {
    const ext = filePath.split('.').pop()?.toLowerCase()
    const langMap: Record<string, string> = {
      py: 'python',
      js: 'javascript',
      ts: 'typescript',
      tsx: 'typescript',
      jsx: 'javascript',
      json: 'json',
      md: 'markdown',
      html: 'html',
      css: 'css',
    }
    return langMap[ext || ''] || 'python'
  }, [filePath])

  return (
    <div className="flex-1 flex flex-col relative">
      {/* Toolbar */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
        <span className="text-sm text-gray-300">{filePath || 'untitled'}</span>
      </div>

      {/* Editor */}
      <Editor
        height="100%"
        language={language}
        value={value}
        onChange={(val) => onChange(val || '')}
        onMount={handleEditorDidMount}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          readOnly: false,
        }}
      />
    </div>
  )
}

