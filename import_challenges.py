"""
Improved CTFd Challenge Importer - Handles messy JSON data
"""

import json
import requests
import sys

# Configuration
CTFd_URL = "http://10.20.22.9:8000/"
ADMIN_TOKEN = "ctfd_d7669c2a3054eff9d7c003f813faffebec319993e12a57ea6fc150b181011f81"
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
    """Extract category from 'category' field, fallback to domain from link if missing"""
    category = challenge_data.get("category")
    if category and isinstance(category, str) and category.strip():
        return category.strip()
    # Fallback to domain from link if no category
    link = challenge_data.get("link", "")
    if isinstance(link, str) and link.startswith("http"):
        return link.replace("https://", "").replace("http://", "").split("/")[0][:64]
    return "General"


def extract_answer(challenge_data):
    """Extract the flag/answer"""
    answer = challenge_data.get("answer", "")
    answer = str(answer)  # Convert to string first
    
    if answer and answer.lower() != "n/a":
        return answer
    
    # Fallback to first clue if it looks like a flag
    clues = challenge_data.get("clues", [])
    if clues and len(clues) > 0:
        clue1 = str(clues[0])
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
        challenge_data.get('description', ''),
        challenge_data.get('question', '')
    ]
    
    # Add the link if it's a valid URL
    if link and link.startswith("http"):
        description_parts.append(f"\n\n🔗 **Challenge Link:** {link}")
    
    description = "\n\n".join(filter(None, description_parts)).strip()[:5000]
    
    ctf_challenge = {
        "name": challenge_data.get("title", "Unnamed Challenge")[:120],
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
    """Add flag to challenge via API"""
    if not answer:
        return False
    
    # Try the standard flags endpoint first
    payload = {
        "challenge_id": challenge_id,
        "content": answer.strip(),
        "type": "static"
    }
    
    try:
        # Try /api/v1/flags endpoint
        resp = requests.post(
            f"{CTFd_URL}/api/v1/flags",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        if resp.status_code == 200:
            print(f"  ✓ Added flag: {answer.strip()[:50]}...")
            return True
        else:
            print(f"  ✗ Failed to add flag via /api/v1/flags: {resp.status_code}")
            if resp.status_code == 404:
                print(f"    Trying alternative endpoint...")
                # Try challenge-specific endpoint
                resp2 = requests.post(
                    f"{CTFd_URL}/api/v1/challenges/{challenge_id}/flags",
                    json=payload,
                    headers=HEADERS,
                    timeout=10
                )
                if resp2.status_code == 200:
                    print(f"  ✓ Added flag via challenge endpoint: {answer.strip()[:50]}...")
                    return True
                else:
                    print(f"    Alternative endpoint also failed: {resp2.status_code}")
                    print(f"    ⚠️  Flag must be added manually via CTFd UI")
                    return False
            return False
            
    except Exception as e:
        print(f"  ✗ Exception adding flag: {e}")
        return False


def add_hints(challenge_id, clues, costs):
    """Add hints to challenge via API using clues array and costs array."""
    added = 0
    for idx, clue in enumerate(clues):
        clue = str(clue).strip() if clue else ""
        if clue:
            cost = costs[idx] if idx < len(costs) else 0
            payload = {
                "challenge_id": challenge_id,
                "content": clue,
                "cost": int(cost)
            }
            try:
                resp = requests.post(
                    f"{CTFd_URL}/api/v1/hints",
                    json=payload,
                    headers=HEADERS,
                    timeout=10
                )
                if resp.status_code == 200:
                    print(f"  ✓ Added hint (cost: {cost}): {clue[:40]}{'...' if len(clue) > 40 else ''}")
                    added += 1
                else:
                    print(f"  ✗ Failed to add hint: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"  ✗ Exception adding hint: {e}")
    return added


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
        print(f"\n[{idx}/{len(challenges)}] {challenge.get('title', 'Unknown')}")
        print("-" * 60)
        
        # Create challenge
        challenge_id = create_challenge(challenge)
        
        if challenge_id:
            imported += 1
            
            # Add flag
            answer = extract_answer(challenge)
            if answer:
                add_flag(challenge_id, answer)
            
            # Add hints with costs
            clues = challenge.get("clues", [])
            costs = challenge.get("costs", [])
            if clues:
                add_hints(challenge_id, clues, costs)
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
