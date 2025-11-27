import { useState } from 'react'
import { useProjectChat } from '../hooks/useProjectChat'

interface ChatPanelProps {
  projectId: number | null
  isCompact?: boolean
}

export default function ChatPanel({ projectId, isCompact = false }: ChatPanelProps) {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([])
  const { sendMessage, isSending } = useProjectChat()

  const handleSend = async () => {
    if (!message.trim() || !projectId) return

    const userMessage = message
    setMessage('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])

    try {
      const response = await sendMessage(projectId, userMessage)
      setMessages((prev) => [...prev, { role: 'assistant', content: response.answer }])
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Error: Failed to get response' }])
    }
  }

  if (!projectId && !isCompact) {
    return (
      <div className="w-80 bg-gray-800 border-l border-gray-700 transition-all">
        <div className="p-4 text-gray-400 text-sm">
          Select a project to chat
        </div>
      </div>
    )
  }

  if (!projectId) {
    return (
      <div className="flex-1 flex flex-col bg-gray-800">
        <div className="p-4 text-gray-400 text-sm">
          Select a project to chat
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-800 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-gray-400 text-sm text-center">
            Ask questions about your codebase...
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-lg ${
              msg.role === 'user'
                ? 'bg-blue-600 ml-auto max-w-[80%]'
                : 'bg-gray-700 mr-auto max-w-[80%]'
            }`}
          >
            <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
          </div>
        ))}
        {isSending && (
          <div className="bg-gray-700 p-3 rounded-lg mr-auto max-w-[80%]">
            <div className="text-sm text-gray-400">Thinking...</div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about your code..."
            className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-sm focus:outline-none focus:border-blue-500"
            disabled={isSending}
          />
          <button
            onClick={handleSend}
            disabled={isSending || !message.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
