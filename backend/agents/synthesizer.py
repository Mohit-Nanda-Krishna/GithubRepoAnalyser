from openai import OpenAI
from config import GROQ_API_KEY, GROQ_MODEL

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def synthesize_report(basics: dict, code_analysis: str, docs_analysis: str, health_analysis: str) -> str:
    """
    Takes the outputs of all three specialist agents and combines them
    into one coherent final report with an overall verdict.
    """
    system_prompt = (
        "You are a senior engineering lead writing a final repository "
        "assessment for a team considering adopting or contributing to "
        "this project. Combine the findings below into ONE coherent report. "
        "Do not repeat the same point across sections. Do not invent "
        "information not present in the findings below."
    )

    user_prompt = f"""
Repo: {basics['full_name']}
Description: {basics['description']}
Language: {basics['language']} | Stars: {basics['stars']} | Forks: {basics['forks']}

--- CODE STRUCTURE FINDINGS ---
{code_analysis}

--- DOCUMENTATION FINDINGS ---
{docs_analysis}

--- REPO HEALTH FINDINGS ---
{health_analysis}

Write a final report with these sections:
1. **Overall Summary** (2-3 sentences)
2. **Strengths** (bullet points)
3. **Concerns** (bullet points)
4. **Overall Verdict**: rate as Excellent / Good / Needs Improvement / Poor, with one sentence justifying it

Keep the entire report under 300 words.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=600,
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
    from code_agent import analyze_code_quality
    from docs_agent import analyze_documentation
    from health_agent import analyze_repo_health

    repo_url = "https://github.com/psf/requests"
    data = fetch_repo_data(repo_url)

    print("Running code agent...")
    code_result = analyze_code_quality(data)

    print("Running docs agent...")
    docs_result = analyze_documentation(data)

    print("Running health agent...")
    health_result = analyze_repo_health(data)

    print("Synthesizing final report...\n")
    final_report = synthesize_report(
        data["basics"], code_result, docs_result, health_result
    )

    print(final_report)
