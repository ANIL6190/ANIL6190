import os
import re
import json
import urllib.request
from datetime import datetime, timezone

USERNAME = "ANIL6190"
README_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")

HEADERS = {
    "User-Agent": f"GitHub-Profile-Updater-{USERNAME}",
    "Accept": "application/vnd.github.v3+json"
}

token = os.environ.get("GITHUB_TOKEN")
if token:
    HEADERS["Authorization"] = f"token {token}"

# Curated tags for known projects if repo topics are empty
KNOWN_TAGS = {
    "3-Body-Problem-Simulation": ["Unity URP", "C#", "Astrophysics", "Physics Engine"],
    "AEGIS-TOWER": ["Keplerian Mechanics", "Python", "AI/ML", "CelesTrak"],
    "SlefDrivingCar_simulation": ["Unity", "ML-Agents (PPO)", "Autonomous AI", "C#"],
    "Ksheera-Raksha": ["ShaderLab", "MATLAB", "Digital Twin", "Thermal Physics"],
    "Lost-and-Found-System": ["Next.js", "TypeScript", "Graph / Trie Algorithms"],
    "GharPayy-A-Smart-PG-Booking-Platform": ["Next.js", "TypeScript", "Full-Stack Web"],
}

def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_repo_icon(name, desc=""):
    name_lower = name.lower()
    desc_lower = (desc or "").lower()
    if "3-body" in name_lower or "astrophys" in desc_lower or "gravit" in desc_lower:
        return "🪐"
    if "aegis" in name_lower or "satellite" in desc_lower or "radar" in desc_lower:
        return "📡"
    if "car" in name_lower or "driving" in desc_lower or "autonomous" in desc_lower:
        return "🏎️"
    if "ksheera" in name_lower or "milk" in desc_lower or "thermal" in desc_lower:
        return "🧊"
    if "lost" in name_lower or "found" in name_lower or "trie" in desc_lower:
        return "🔍"
    if "pg" in name_lower or "booking" in desc_lower or "ghar" in name_lower or "house" in desc_lower:
        return "🏠"
    if "ai" in desc_lower or "nn" in desc_lower or "model" in desc_lower or "neural" in desc_lower or "learning" in desc_lower:
        return "🧠"
    if "game" in desc_lower or "unity" in desc_lower:
        return "🎮"
    return "🚀"

def fetch_projects():
    url = f"https://api.github.com/users/{USERNAME}/repos?sort=pushed&per_page=100"
    repos = get_json(url)
    if not repos:
        return []
    
    projects = []
    for repo in repos:
        if repo.get("fork"):
            continue
        if repo.get("name") == USERNAME:
            continue
        
        name = repo.get("name")
        desc = repo.get("description") or "Interactive simulation and software engineering project."
        html_url = repo.get("html_url")
        lang = repo.get("language")
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        topics = repo.get("topics", [])
        
        # Build tags list
        tags = []
        if name in KNOWN_TAGS:
            tags = KNOWN_TAGS[name].copy()
        else:
            if lang:
                tags.append(lang)
            for t in topics[:3]:
                tags.append(t.replace("-", " ").title())
        
        projects.append({
            "name": name,
            "desc": desc,
            "url": html_url,
            "tags": tags,
            "stars": stars,
            "forks": forks,
            "icon": get_repo_icon(name, desc)
        })
    return projects

def format_projects_markdown(projects):
    if not projects:
        return "_No public projects available at this moment._\n"
    
    lines = []
    for p in projects:
        tag_badges = " ".join(f"`{t}`" for t in p["tags"])
        metrics = []
        if p["stars"] > 0:
            metrics.append(f"⭐ {p['stars']}")
        if p["forks"] > 0:
            metrics.append(f"🍴 {p['forks']}")
        metrics_str = (" &nbsp;" + " ".join(metrics)) if metrics else ""
        
        lines.append(f"- {p['icon']} **[{p['name']}]({p['url']})** &nbsp;{tag_badges}{metrics_str}")
        lines.append(f"  > {p['desc']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def format_time_ago(dt_str):
    try:
        event_time = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - event_time
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            m = max(1, seconds // 60)
            return f"{m}m ago"
        elif seconds < 86400:
            h = seconds // 3600
            return f"{h}h ago"
        elif seconds < 604800:
            d = seconds // 86400
            return f"{d}d ago"
        else:
            return event_time.strftime("%b %d, %Y")
    except Exception:
        return dt_str[:10]

def fetch_activity(limit=7):
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=30"
    events = get_json(url)
    if not events:
        return []
    
    activity_items = []
    seen = set()
    
    for event in events:
        e_type = event.get("type")
        repo_name = event.get("repo", {}).get("name", "")
        repo_url = f"https://github.com/{repo_name}"
        created_at = event.get("created_at", "")
        time_ago = format_time_ago(created_at)
        payload = event.get("payload", {})
        clean_repo = repo_name.replace(f"{USERNAME}/", "")
        
        line = None
        if e_type == "PushEvent":
            commits = payload.get("commits", [])
            count = payload.get("size", len(commits))
            if count == 0:
                count = 1
            msg = commits[0].get("message", "").split("\n")[0] if commits else ""
            if len(msg) > 60:
                msg = msg[:57] + "..."
            msg_str = f" - _{msg}_" if msg else ""
            line = f"🔨 Pushed **{count} commit{'s' if count > 1 else ''}** to [`{clean_repo}`]({repo_url}){msg_str} • `{time_ago}`"
        elif e_type == "CreateEvent":
            ref_type = payload.get("ref_type", "repository")
            ref = payload.get("ref")
            if ref_type == "repository":
                line = f"✨ Created repository [`{clean_repo}`]({repo_url}) • `{time_ago}`"
            else:
                line = f"🌱 Created {ref_type} `{ref}` in [`{clean_repo}`]({repo_url}) • `{time_ago}`"
        elif e_type == "WatchEvent":
            line = f"⭐ Starred [`{clean_repo}`]({repo_url}) • `{time_ago}`"
        elif e_type == "ForkEvent":
            line = f"🍴 Forked [`{clean_repo}`]({repo_url}) • `{time_ago}`"
        elif e_type == "PullRequestEvent":
            action = payload.get("action", "opened")
            pr_num = payload.get("number", "")
            line = f"🔀 {action.capitalize()} PR [#{pr_num}]({repo_url}/pull/{pr_num}) in [`{clean_repo}`]({repo_url}) • `{time_ago}`"
        elif e_type == "IssuesEvent":
            action = payload.get("action", "opened")
            issue_num = payload.get("issue", {}).get("number", "")
            line = f"❗ {action.capitalize()} issue [#{issue_num}]({repo_url}/issues/{issue_num}) in [`{clean_repo}`]({repo_url}) • `{time_ago}`"
        elif e_type == "ReleaseEvent":
            rel_name = payload.get("release", {}).get("name", "Release")
            line = f"🚀 Published release **{rel_name}** in [`{clean_repo}`]({repo_url}) • `{time_ago}`"
        
        if line and line not in seen:
            seen.add(line)
            activity_items.append(line)
            if len(activity_items) >= limit:
                break
                
    return activity_items

def format_activity_markdown(activities):
    if not activities:
        return "_No recent public activity._\n"
    return "\n".join(f"- {act}" for act in activities) + "\n"

def update_section(content, section_name, new_content):
    pattern = rf"(<!--START_SECTION:{section_name}-->)(.*?)(<!--END_SECTION:{section_name}-->)"
    replacement = rf"\1\n{new_content}\3"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def main():
    print(f"Updating README for {USERNAME}...")
    if not os.path.exists(README_PATH):
        print(f"Error: {README_PATH} not found.")
        return
    
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()
    
    # 1. Update Projects
    projects = fetch_projects()
    print(f"Found {len(projects)} projects.")
    projects_md = format_projects_markdown(projects)
    readme = update_section(readme, "projects", projects_md)
    
    # 2. Update Activity
    activities = fetch_activity(limit=6)
    print(f"Found {len(activities)} activity items.")
    activity_md = format_activity_markdown(activities)
    readme = update_section(readme, "activity", activity_md)
    
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme)
    print("README.md updated successfully!")

if __name__ == "__main__":
    main()
