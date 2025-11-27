"""
Chat service - handles project-aware chat queries using RAG
"""
from typing import List, Dict
from models.chat import ChatRequest, ChatResponse, Reference
from services.embedding_service import search
from services.llm_service import generate_response


class ChatService:
    async def process_chat(self, project_id: int, request: ChatRequest) -> ChatResponse:
        """Process a chat query with RAG"""
        project_id_str = str(project_id)
        
        # Step 1: Search for relevant code snippets using embeddings
        relevant_results = search(project_id_str, request.message, k=5)
        
        # Step 2: Build context from relevant snippets
        context_snippets = self._build_context_snippets(relevant_results)
        
        # Step 3: Build LLM prompts
        system_prompt = (
            "You are an AI code assistant with full context of this repository. "
            "Use the provided code snippets as context to answer the user's question. "
            "If the provided context is insufficient or you're unsure about something, say so clearly. "
            "Be concise but thorough in your explanations."
        )
        
        user_prompt = self._build_user_prompt(request.message, context_snippets)
        
        # Step 4: Generate response using LLM
        answer = await generate_response(system_prompt, user_prompt)
        
        # Step 5: Build references
        references = [
            Reference(
                file_path=result.get("file_path", ""),
                line_start=result.get("line_start", 0),
                line_end=result.get("line_end", 0),
                snippet=result.get("code", "")[:200]  # Truncate
            )
            for result in relevant_results
        ]
        
        return ChatResponse(answer=answer, references=references)
    
    def _build_context_snippets(self, results: List[Dict]) -> List[str]:
        """Build context snippets from search results"""
        snippets = []
        for result in results:
            snippet = (
                f"File: {result.get('file_path', 'unknown')}\n"
                f"Symbol: {result.get('type', 'unknown')} {result.get('name', 'unknown')}\n"
                f"Lines: {result.get('line_start', 0)}-{result.get('line_end', 0)}\n"
                f"Code:\n{result.get('code', '')}\n"
            )
            snippets.append(snippet)
        return snippets
    
    def _build_user_prompt(self, query: str, context_snippets: List[str]) -> str:
        """Build user prompt with question and context"""
        prompt = f"User question: {query}\n\n"
        
        if context_snippets:
            prompt += "Relevant code snippets from the repository:\n\n"
            for i, snippet in enumerate(context_snippets, 1):
                prompt += f"--- Snippet {i} ---\n{snippet}\n\n"
        else:
            prompt += "No relevant code snippets found in the repository.\n\n"
        
        prompt += "Please answer the user's question based on the provided context."
        
        return prompt

