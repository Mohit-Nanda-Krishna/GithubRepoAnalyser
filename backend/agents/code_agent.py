import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def analyze_code_quality(repo_data: dict) -> str:
    """
    Takes the dict returned by fetch_repo_data() and asks the LLM
    to assess code quality/structure based on the file tree and basics.
    """
    file_tree = repo_data["file_tree"]
    basics = repo_data["basics"]

    # Truncate the file list — we don't need to send all 100 files,
    # just enough for the model to understand the project's shape
    files_preview = "\n".join(file_tree[:50])

    system_prompt = (
        "You are a senior software engineer reviewing a codebase's "
        "structure and organization. Be specific and concise. "
        "Do not make up information you weren't given."
    )

    user_prompt = f"""
Repo: {basics['full_name']}
Primary language: {basics['language']}
Description: {basics['description']}

File structure (partial):
{files_preview}

Based on this file structure, analyze:
1. What kind of project this appears to be
2. Whether the folder structure follows common conventions for this language
3. Any red flags visible from the structure alone (e.g. no tests folder, no config files)

Keep your answer under 200 words.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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
    sys.path.append("..")  # so we can import github_fetcher from the parent folder
    from github_fetcher import fetch_repo_data

    data = fetch_repo_data("https://github.com/psf/requests")
    analysis = analyze_code_quality(data)
    print(analysis)