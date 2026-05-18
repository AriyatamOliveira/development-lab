import os
from google import genai
from google.genai import types
from pydantic import BaseModel
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Require GEMINI_API_KEY environment variable to be set
client = genai.Client(api_key=GEMINI_API_KEY)

async def generate_study_materials(text_content: str, material_type: str):
    prompt = ""
    if material_type == "summary":
        prompt = """Analyze the following content and produce a structured summary as a JSON object.
The JSON must have this exact shape:
{
  "title": "A short descriptive title for the entire content",
  "sections": [
    {
      "heading": "Section heading",
      "summary": "A concise 2-4 sentence summary of this section's key points."
    }
  ]
}
Rules:
- Create between 3 and 8 sections depending on content complexity.
- Each summary should be precise and technical, not vague.
- Do NOT include markdown formatting or code fences. Return ONLY raw JSON."""

    elif material_type == "flashcards":
        prompt = "Generate 5 flashcards from the text. Return a JSON array of objects with 'question' and 'answer' keys. Do NOT include any markdown formatting or code blocks. Return purely the raw JSON."
    elif material_type == "quiz":
        prompt = "Generate a 3-question multiple choice quiz. Return a JSON array of objects with 'question', 'options' (array of 4 strings), and 'answer' (the correct option string). Do NOT include any markdown formatting or code blocks. Return purely the raw JSON."
    else:
        raise ValueError("Invalid material type")

    full_prompt = f"{prompt}\n\nCONTENT:\n{text_content}"

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=full_prompt,
    )
    
    res_text = response.text
    
    if material_type in ["flashcards", "quiz", "summary"]:
        # Clean up possible markdown json blocks
        res_text = res_text.strip()
        if res_text.startswith("```json"):
            res_text = res_text[7:]
        if res_text.startswith("```"):
            res_text = res_text[3:]
        if res_text.endswith("```"):
            res_text = res_text[:-3]
        try:
            return json.loads(res_text.strip())
        except json.JSONDecodeError:
            if material_type == "summary":
                return {"title": "Summary", "sections": [{"heading": "Full Content", "summary": res_text.strip()}]}
            return {"error": "Failed to parse JSON from LLM", "raw": res_text}
            
    return res_text


async def chat_with_context(text_content: str, message: str, history: list[dict]):
    """Chat with Gemini about a specific document context."""
    
    history_text = ""
    for msg in history[-10:]:  # Keep last 10 messages for context window
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"
    
    prompt = f"""You are a study assistant. The user is studying the following content.
Answer their questions concisely and accurately based on the content provided.
If the question is unrelated to the content, politely note that and answer briefly anyway.

STUDY CONTENT:
{text_content}

CONVERSATION HISTORY:
{history_text}

USER MESSAGE:
{message}

Respond directly and concisely."""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    return response.text
