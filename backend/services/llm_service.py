"""
LLM Service - handles LLM API calls with OpenAI
"""
import logging
import openai
from fastapi import HTTPException
from typing import Optional
from config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

# Initialize OpenAI client
_client: Optional[openai.AsyncOpenAI] = None


def _get_client() -> openai.AsyncOpenAI:
    """Get or initialize OpenAI client"""
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            error_msg = "OPENAI_API_KEY environment variable is not set. Please set it to use LLM features."
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail="LLM service is not configured. OPENAI_API_KEY is missing."
            )
        _client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        logger.info(f"OpenAI client initialized with model: {OPENAI_MODEL}")
    return _client


async def generate_response(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> str:
    """
    Generate a response using the LLM
    
    Args:
        system_prompt: System prompt to set the context
        user_prompt: User prompt/question
        model: Model to use (defaults to OPENAI_MODEL from config)
        temperature: Temperature for response generation (default: 0.7)
    
    Returns:
        Generated response text
    
    Raises:
        HTTPException: If LLM API call fails
    """
    if model is None:
        model = OPENAI_MODEL
    
    client = _get_client()
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        
        if not response.choices or not response.choices[0].message.content:
            logger.warning("LLM returned empty response")
            raise HTTPException(
                status_code=500,
                detail="LLM returned an empty response. Please try again."
            )
        
        return response.choices[0].message.content
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"LLM API error: {str(e)}"
        )
    except openai.APIConnectionError as e:
        logger.error(f"OpenAI connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to LLM service. Please check your network connection."
        )
    except Exception as e:
        logger.error(f"Unexpected error in LLM service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error in LLM service: {str(e)}"
        )

