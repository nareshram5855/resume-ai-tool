import json
import os
from groq import Groq

MODEL = "llama-3.3-70b-versatile"


def _get_client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY", ""))


SUMMARY_PROMPT = """You are a professional resume writer. Based on the updated resume below and the target job description, generate two types of summaries:

1. Per-client summaries: For each client/company in the experience section, write a concise 2-3 sentence summary highlighting the key contributions and impact at that client.

2. Overall professional summary: Write a compelling 3-4 sentence professional summary paragraph that positions the candidate as a strong fit for the target job description. This should tie together their overall experience.

UPDATED RESUME:
{resume_json}

TARGET JOB DESCRIPTION:
{jd_text}

Respond ONLY with valid JSON in this exact format (no extra text, no markdown):
{{
  "per_client_summaries": [
    {{"client": "Company/Client Name", "summary": "2-3 sentence summary of work at this client..."}}
  ],
  "overall_summary": "3-4 sentence professional summary paragraph tailored to the JD..."
}}"""


async def generate_summaries(resume_data: dict, jd_text: str) -> dict:
    """Use Groq (Llama 3.3 70B) to generate per-client and overall summaries."""
    resume_json = json.dumps(resume_data, indent=2)

    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional resume writer. Always respond with valid JSON only, no markdown formatting.",
            },
            {
                "role": "user",
                "content": SUMMARY_PROMPT.format(
                    resume_json=resume_json, jd_text=jd_text
                ),
            },
        ],
        temperature=0.4,
        max_tokens=2048,
    )

    response_text = response.choices[0].message.content.strip()

    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    return json.loads(response_text.strip())
