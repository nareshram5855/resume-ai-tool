import json
import os
from groq import Groq

MODEL = "llama-3.3-70b-versatile"


def _get_client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY", ""))


ANALYSIS_PROMPT = """You are a resume analysis expert. Compare the following resume against the job description.

Your task:
1. Identify resume bullet points that ALREADY MATCH or align with the job description requirements.
2. Identify JD requirements that are NOT covered by the resume — these are the GAPS.
3. For each gap, suggest a new bullet point to add under the most relevant client/experience section.
4. Identify skills mentioned in the JD that are missing from the resume's skills section.

IMPORTANT RULES:
- Do NOT modify or rephrase existing resume points that already match.
- Only suggest NEW points for genuine gaps.
- Suggested points should sound natural and achievement-oriented (use metrics where plausible).
- Assign each suggested point to the most relevant existing client/experience section.

RESUME:
{resume_json}

JOB DESCRIPTION:
{jd_text}

Respond ONLY with valid JSON in this exact format (no extra text, no markdown):
{{
  "matched_points": [
    {{"client": "client/company name from resume", "point": "the existing resume point", "jd_match": "the JD requirement it matches"}}
  ],
  "missing_points": [
    {{"client": "client/company name to add under", "suggested_point": "new bullet point to add", "jd_requirement": "the JD requirement this addresses"}}
  ],
  "missing_skills": ["skill1", "skill2"]
}}"""


async def analyze_resume_vs_jd(resume_data: dict, jd_text: str) -> dict:
    """Use Groq (Llama 3.3 70B) to compare resume against JD and find gaps."""
    resume_json = json.dumps(resume_data, indent=2)

    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a resume analysis expert. Always respond with valid JSON only, no markdown formatting.",
            },
            {
                "role": "user",
                "content": ANALYSIS_PROMPT.format(
                    resume_json=resume_json, jd_text=jd_text
                ),
            },
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    response_text = response.choices[0].message.content.strip()

    # Strip markdown code blocks if present
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    return json.loads(response_text.strip())
