import { useState } from 'react'
import { explainCode as explainCodeAPI } from '../api/explain'

export function useExplainCode() {
  const [isExplaining, setIsExplaining] = useState(false)

  const explainCode = async (request: { code: string; file_path?: string; language?: string }) => {
    setIsExplaining(true)
    try {
      const response = await explainCodeAPI(request)
      return response
    } finally {
      setIsExplaining(false)
    }
  }

  return {
    explainCode,
    isExplaining,
  }
}

