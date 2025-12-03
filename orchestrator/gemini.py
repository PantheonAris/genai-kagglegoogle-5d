import google.generativeai as genai
import os
import json
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional
from orchestrator.prompts import INTENT_RECOGNITION_PROMPT, RESPONSE_SYNTHESIS_PROMPT

class RecognizedIntent(BaseModel):
    intent: str
    entities: Dict[str, Any]

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def recognize_intent(self, user_query: str) -> RecognizedIntent:
        """
        Uses Gemini to recognize the intent of the user's query.
        """
        prompt = INTENT_RECOGNITION_PROMPT.format(user_query=user_query)
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract the JSON part of the response
            json_response = self._extract_json(response.text)
            
            # Parse and validate with Pydantic
            intent_data = RecognizedIntent.parse_obj(json_response)
            return intent_data
            
        except (ValueError, ValidationError) as e:
            # Handle cases where the response is not valid JSON or doesn't match the model
            # You might want to log this error
            return RecognizedIntent(intent="unknown", entities={"error": str(e)})
        except Exception as e:
            # Handle other potential errors (e.g., API issues)
            return RecognizedIntent(intent="unknown", entities={"error": f"An unexpected error occurred: {e}"})

    def synthesize_response(self, user_query: str, tool_results: Dict[str, Any]) -> str:
        """
        Synthesizes a response to the user based on the tool results.
        """
        prompt = RESPONSE_SYNTHESIS_PROMPT.format(user_query=user_query, tool_results=json.dumps(tool_results, indent=2))
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Sorry, I encountered an error while generating a response: {e}"


    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extracts a JSON object from a string.
        It assumes the JSON is enclosed in ```json ... ``` or is the main content.
        """
        try:
            # Find JSON block enclosed in ```json ... ```
            if '```json' in text:
                start = text.find('```json') + len('```json')
                end = text.find('```', start)
                json_str = text[start:end].strip()
            # If not, assume the whole string is a JSON object
            else:
                json_str = text

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON: {e}")

# This would be initialized in your main application with the key from a secure source
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# gemini_client = GeminiClient(api_key=GEMINI_API_KEY)
