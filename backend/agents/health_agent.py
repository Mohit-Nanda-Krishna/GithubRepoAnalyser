from openai import OpenAI
from config import GROQ_API_KEY, GROQ_MODEL

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def analyze_repo_health(repo_data: dict) -> str:
    """
    Assesses repo activity/health from commit history and basic stats.
    """
    commits = repo_data["recent_commits"]
    basics = repo_data["basics"]

    commits_summary = "\n".join(
        [f"- {c['date']}: {c['message'][:80]}" for c in commits]
    )

    system_prompt = (
        "You assess open-source project health and maintenance activity. "
        "Be specific and concise. Do not make up information you weren't given."
    )

    user_prompt = f"""
Repo: {basics['full_name']}
Stars: {basics['stars']}
Forks: {basics['forks']}

Recent commits:
{commits_summary}

Based on this activity, assess:
1. How actively maintained does this project appear to be?
2. Are commits frequent and substantive, or sparse/trivial?
3. Overall health signal: Healthy / Moderate / Concerning

Keep your answer under 150 words.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=300,
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
    analysis = analyze_repo_health(data)
    print(analysis)
