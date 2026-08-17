from github import Github, Auth, GithubException
from config import GITHUB_TOKEN

auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)


def parse_repo_url(repo_url: str) -> str:
    """
    Converts a full GitHub URL into 'owner/repo' format.
    Handles trailing slashes and accidental .git suffixes.
    """
    path = repo_url.replace("https://github.com/", "").strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return path


def get_repo_basics(repo) -> dict:
    return {
        "name": repo.name,
        "full_name": repo.full_name,
        "description": repo.description,
        "language": repo.language,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "size_kb": repo.size,
        "default_branch": repo.default_branch,
    }


def get_file_tree(repo, max_files: int = 100) -> list[str]:
    contents = repo.get_contents("")
    file_paths = []

    while contents and len(file_paths) < max_files:
        item = contents.pop(0)
        if item.type == "dir":
            contents.extend(repo.get_contents(item.path))
        else:
            file_paths.append(item.path)

    return file_paths


def get_readme(repo) -> str | None:
    try:
        readme = repo.get_readme()
        return readme.decoded_content.decode("utf-8")
    except GithubException:
        return None


def get_recent_commits(repo, count: int = 10) -> list[dict]:
    commits = repo.get_commits()[:count]
    return [
        {
            "message": c.commit.message,
            "author": c.commit.author.name,
            "date": str(c.commit.author.date),
        }
        for c in commits
    ]


def fetch_repo_data(repo_url: str) -> dict:
    """
    Single entry point: takes a GitHub URL, returns everything
    our agents will need in one dictionary. This is the ONLY
    function the rest of the app should call directly.
    """
    repo_path = parse_repo_url(repo_url)

    try:
        repo = g.get_repo(repo_path)
    except GithubException as e:
        raise ValueError(f"Could not fetch repo '{repo_path}': {e}")

    return {
        "basics": get_repo_basics(repo),
        "file_tree": get_file_tree(repo),
        "readme": get_readme(repo),
        "recent_commits": get_recent_commits(repo),
    }


if __name__ == "__main__":
    data = fetch_repo_data("https://github.com/psf/requests")
    print("Repo:", data["basics"]["full_name"])
    print("Language:", data["basics"]["language"])
    print("Files found:", len(data["file_tree"]))
    print("Has README:", data["readme"] is not None)
    print("Commits fetched:", len(data["recent_commits"]))
