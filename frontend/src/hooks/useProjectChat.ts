import { useState } from 'react'
import { chatWithProject } from '../api/chat'

export function useProjectChat() {
  const [isSending, setIsSending] = useState(false)

  const sendMessage = async (projectId: number, message: string) => {
    setIsSending(true)
    try {
      const response = await chatWithProject(projectId, message)
      return response
    } finally {
      setIsSending(false)
    }
  }

  return {
    sendMessage,
    isSending,
  }
}

