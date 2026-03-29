"""
NewsGPT Navigator — Video Agent

Fetches relevant YouTube video links for the analyzed topic
using lightweight HTML scraping (no API key required).
Returns video titles, URLs, and thumbnail images.
"""

import re
import requests
from datetime import datetime, timezone
from agents.state import PipelineState


def _generate_video_links(topic: str) -> list:
    """
    Fetch 3 relevant YouTube videos for each topic using lightweight scraping.
    """
    try:
        search_query = f"{topic} latest news analysis"
        url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception(f"YouTube search failed with status {response.status_code}")

        html = response.text
        # More robust regex for YouTube video IDs and TITLES from search results
        # IDs: /watch?v=XXXXXXXXXXX
        # Titles: "title":{"runs":[{"text":"VIDEO_TITLE"}]}
        video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
        video_titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"\}\]', html)

        # Unique IDs only
        unique_ids = []
        titles_map = {}
        
        for i, vid in enumerate(video_ids):
            if vid not in unique_ids:
                unique_ids.append(vid)
                # Map title to ID if possible (titles usually follow IDs in search response)
                if i < len(video_titles):
                    titles_map[vid] = video_titles[i]
            if len(unique_ids) >= 3:
                break

        if not unique_ids:
            raise Exception("No video IDs found in search results")

        videos = []
        fallback_templates = [
            f"{topic} Explained",
            f"{topic} Latest Update",
            f"{topic} Expert Analysis"
        ]

        for i, vid in enumerate(unique_ids):
            title = titles_map.get(vid)
            if not title or len(title) < 5:
                title = fallback_templates[i] if i < len(fallback_templates) else f"{topic} Analysis"
            
            videos.append({
                "title": title,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "thumbnail": f"https://img.youtube.com/vi/{vid}/0.jpg"
            })

        return videos

    except Exception as e:
        # Final Fallback: Simple search results link
        return [
            {
                "title": f"{topic} videos",
                "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}",
                "thumbnail": ""
            }
        ]


def video_agent(state: PipelineState) -> dict:
    """
    Dynamic Video Agent
    - Fetches relevant YouTube links via scraping
    """
    topic = state.get("topic", "")
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "timestamp": timestamp,
        "agent": "video",
        "action": "fetch_youtube_links",
        "inputs": {"topic": topic},
        "outputs": {},
    }

    try:
        videos = _generate_video_links(topic)

        audit_entry["outputs"] = {
            "videos_count": len(videos),
            "generated": True
        }

        return {
            "videos": videos,
            "video_generated": True,
            "current_agent": "video",
            "audit_trail": [audit_entry],
        }

    except Exception as e:
        audit_entry["outputs"] = {"error": str(e)}
        return {
            "videos": [],
            "video_generated": False,
            "current_agent": "video",
            "error": f"Video agent error: {e}",
            "audit_trail": [audit_entry],
        }
