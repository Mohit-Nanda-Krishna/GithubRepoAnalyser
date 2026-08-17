from openai import OpenAI
from config import GROQ_API_KEY, GROQ_MODEL

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def analyze_documentation(repo_data: dict) -> str:
    """
    Assesses README/documentation quality.
    """
    readme = repo_data["readme"]
    basics = repo_data["basics"]

    if not readme:
        return "No README found in this repository. This is a significant documentation gap — new contributors and users have no entry point to understand the project."

    system_prompt = (
        "You are a technical writer reviewing documentation quality. "
        "Be specific and concise. Do not make up information you weren't given."
    )

    user_prompt = f"""
Repo: {basics['full_name']}

README content:
{readme[:3000]}

Evaluate this README on:
1. Does it explain what the project does and why?
2. Does it include installation/setup instructions?
3. Does it include usage examples?
4. What's missing that a good README should have?

Keep your answer under 200 words.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=400,
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from github_fetcher import fetch_repo_data

    data = fetch_repo_data("https://github.com/psf/requests")
    analysis = analyze_documentation(data)
    print(analysis)
