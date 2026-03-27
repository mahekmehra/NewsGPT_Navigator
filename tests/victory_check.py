
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from agents.orchestrator import run_pipeline
from agents.state import create_initial_state

def test_victory_flow():
    print("🚀 Starting Dynamic Video Verification...")
    
    topic = "SpaceX Starship Latest Launch"
    persona = "Tech Enthusiast"
    
    print(f"Topic: {topic}")
    
    try:
        result = run_pipeline(topic=topic, persona=persona)
        
        print("\n✅ Pipeline Completed!")
        
        briefing = result.get("briefing", {})
        
        # Check Videos
        videos = briefing.get("videos", [])
        print(f"🎥 Videos count: {len(videos)}")
        if videos:
            for i, v in enumerate(videos):
                print(f"  [{i+1}] Title: {v.get('title')}")
                print(f"      URL: {v.get('url')}")
                print(f"      Thumb: {v.get('thumbnail')}")
                
                # Assertions
                if "youtube.com/watch?v=" not in v.get('url', ''):
                    print(f"      ❌ ERROR: Invalid URL for video {i+1}")
                if "img.youtube.com/vi/" not in v.get('thumbnail', ''):
                    print(f"      ❌ ERROR: Invalid Thumbnail for video {i+1}")
        else:
            print("  - ❌ No videos found (Fallback might have triggered without thumbnail).")
            
        # Check Audio
        audio_url = briefing.get("audio_url")
        print(f"🔊 Audio URL: {audio_url}")

    except Exception as e:
        print(f"💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_victory_flow()
