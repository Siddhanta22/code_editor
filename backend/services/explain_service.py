"""
Explain service - handles code explanation requests
"""
from typing import Optional
from models.explain import ExplainRequest, ExplainResponse
from services.llm_service import generate_response


class ExplainService:
    async def explain_code(
        self, 
        project_id: Optional[int], 
        request: ExplainRequest
    ) -> ExplainResponse:
        """Explain code with optional project context"""
        # For now, use standalone explanation
        # Later: can use project context for better explanations
        return await self.explain_code_standalone(request)
    
    async def explain_code_standalone(self, request: ExplainRequest) -> ExplainResponse:
        """Explain code without project context"""
        # Build system prompt
        system_prompt = (
            "You are a helpful code explainer. Explain the provided code to an intermediate developer. "
            "Mention the code's purpose, how it works, its complexity level, and any potential pitfalls or issues. "
            "Be clear and concise."
        )
        
        # Build user prompt with code
        language_info = f"Language: {request.language or 'unknown'}\n" if request.language else ""
        file_info = f"File: {request.file_path}\n" if request.file_path else ""
        
        user_prompt = (
            f"{file_info}"
            f"{language_info}\n"
            f"Code to explain:\n"
            f"```\n{request.code}\n```\n\n"
            f"Please provide:\n"
            f"1. A clear explanation of what this code does\n"
            f"2. The complexity level (low/medium/high)\n"
            f"3. Any potential issues or pitfalls"
        )
        
        # Generate explanation using LLM
        explanation = await generate_response(system_prompt, user_prompt)
        
        # Parse response to extract complexity and issues (simple heuristic for now)
        complexity = "medium"  # Default
        issues = []
        
        # Try to extract complexity from response
        explanation_lower = explanation.lower()
        if "complexity: low" in explanation_lower or "low complexity" in explanation_lower:
            complexity = "low"
        elif "complexity: high" in explanation_lower or "high complexity" in explanation_lower:
            complexity = "high"
        
        # Try to extract issues (look for common patterns)
        if "issue" in explanation_lower or "pitfall" in explanation_lower or "problem" in explanation_lower:
            # Simple extraction - in production, use structured output
            issues = ["See explanation for details"]
        
        return ExplainResponse(
            explanation=explanation,
            complexity=complexity,
            issues=issues
        )

