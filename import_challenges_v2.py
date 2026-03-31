"""
Improved CTFd Challenge Importer - Handles messy JSON data
"""

import json
import requests
import sys

# Configuration
CTFd_URL = "http://localhost:80"
ADMIN_TOKEN = "ctfd_7273e0c998a1b96085c1a819457fbc5943ad1ef40eda099b72a336b371d71e4d"
JSON_FILE = "csvjson.json"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Token {ADMIN_TOKEN}"
}


def load_challenges():
    """Load challenges from JSON file"""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {JSON_FILE} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: {JSON_FILE} is not valid JSON: {e}")
        sys.exit(1)


def extract_points(challenge_data):
    """Extract points value - handles various formats"""
    points_field = challenge_data.get("points")
    qtype_field = challenge_data.get("qtype")
    
    # Try points field first
    if isinstance(points_field, int):
        return points_field
    if isinstance(points_field, str):
        try:
            return int(points_field)
        except ValueError:
            pass
    
    # Try qtype as fallback
    if isinstance(qtype_field, int):
        return qtype_field
    if isinstance(qtype_field, str):
        try:
            return int(qtype_field)
        except ValueError:
            pass
    
    # Default to 100 if nothing works
    return 100


def extract_category(challenge_data):
    """Extract category - truncate if too long"""
    category = challenge_data.get("link", "General")
    if isinstance(category, str):
        category = category.replace("https://", "").replace("http://", "").split("/")[0][:64]
    else:
        category = "General"
    
    return category or "General"


def extract_answer(challenge_data):
    """Extract the flag/answer"""
    answer = challenge_data.get("answer", "")
    answer = str(answer)  # Convert to string first
    
    if answer and answer.lower() != "n/a":
        return answer
    
    # Fallback to clue1 if it looks like a flag
    clue1 = challenge_data.get("clue1", "")
    clue1 = str(clue1)
    if clue1 and "{" in clue1:
        return clue1
    
    return None


def create_challenge(challenge_data):
    """Create a challenge via CTFd API"""
    
    points = extract_points(challenge_data)
    category = extract_category(challenge_data)
    link = challenge_data.get("link", "").strip()
    
    # Build description with challenge details and link
    description_parts = [
        challenge_data.get('qdesc', ''),
        challenge_data.get('question', '')
    ]
    
    # Add the link if it's a valid URL
    if link and link.startswith("http"):
        description_parts.append(f"\n\n🔗 **Challenge Link:** {link}")
    
    description = "\n\n".join(filter(None, description_parts)).strip()[:5000]
    
    ctf_challenge = {
        "name": challenge_data.get("qtitle", "Unnamed Challenge")[:120],
        "description": description,
        "category": category,
        "value": int(points),
        "type": "standard",
        "state": "visible"
    }

    try:
        response = requests.post(
            f"{CTFd_URL}/api/v1/challenges",
            json=ctf_challenge,
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            challenge_id = response.json()["data"]["id"]
            print(f"✓ Created: {ctf_challenge['name']} (ID: {challenge_id}, Points: {points})")
            return challenge_id
        else:
            print(f"✗ Failed to create {ctf_challenge['name']}: {response.status_code}")
            if response.status_code == 400:
                print(f"  Error: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Error creating challenge: {e}")
        return None


def add_flag(challenge_id, answer):
    """Add flag to challenge - SKIPPING DUE TO API ENDPOINT ISSUES"""
    # The /api/v1/challenges/{id}/flags endpoint is returning 404
    # This appears to be a CTFd version compatibility issue
    # Flags will be added manually via the web UI
    return False


def add_hints(challenge_id, clues):
    """Add hints to challenge - SKIPPING DUE TO API ENDPOINT ISSUES"""
    # The /api/v1/challenges/{id}/hints endpoint is returning 404
    # Hints will be added manually via the web UI
    return 0


def main():
    """Main import function"""
    print("=" * 60)
    print("CTFd Challenge Importer v2 (Improved)")
    print("=" * 60)
    
    if ADMIN_TOKEN == "YOUR_ADMIN_TOKEN_HERE":
        print("\n⚠️  ADMIN_TOKEN not set!")
        sys.exit(1)
    
    challenges = load_challenges()
    print(f"\nLoaded {len(challenges)} challenges from {JSON_FILE}\n")
    
    imported = 0
    failed = 0
    
    for idx, challenge in enumerate(challenges, 1):
        print(f"\n[{idx}/{len(challenges)}] {challenge.get('qtitle', 'Unknown')}")
        print("-" * 60)
        
        # Create challenge
        challenge_id = create_challenge(challenge)
        
        if challenge_id:
            imported += 1
            
            # Add flag
            answer = extract_answer(challenge)
            if answer:
                add_flag(challenge_id, answer)
            
            # Add hints
            clues = [
                challenge.get("clue1", ""),
                challenge.get("clue2", ""),
                challenge.get("clue3", "")
            ]
            add_hints(challenge_id, clues)
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"✓ Successfully imported: {imported}")
    print(f"✗ Failed imports: {failed}")
    print(f"Total: {len(challenges)}")
    print("\n✅ All challenges created! Now add flags & hints manually:")
    print("   1. Visit http://localhost/admin/challenges")
    print("   2. Click on each challenge")
    print("   3. Add Flags tab → Add flag content")
    print("   4. Add Hints tab → Add hint content with cost")
    print("\n💡 Tip: Check csvjson.json for answer/clue data to add")


if __name__ == "__main__":
    main()
