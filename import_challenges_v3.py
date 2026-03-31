"""
CTFd Challenge Importer v3 - With Flags & Hints Support
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
    
    if isinstance(points_field, int):
        return points_field
    if isinstance(points_field, str):
        try:
            return int(points_field)
        except ValueError:
            pass
    
    if isinstance(qtype_field, int):
        return qtype_field
    if isinstance(qtype_field, str):
        try:
            return int(qtype_field)
        except ValueError:
            pass
    
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
    answer = str(answer)
    
    if answer and answer.lower() != "n/a":
        return answer
    
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
    """Add flag using direct /api/v1/flags endpoint"""
    if not answer:
        return False
    
    flag_data = {
        "challenge_id": challenge_id,
        "content": str(answer)[:1000],
        "type": "static"
    }

    try:
        # Try direct /api/v1/flags endpoint
        response = requests.post(
            f"{CTFd_URL}/api/v1/flags",
            json=flag_data,
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✓ Flag added: {str(answer)[:30]}...")
            return True
        else:
            print(f"  ✗ Flag failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"  ✗ Flag error: {e}")
        return False


def add_hints(challenge_id, clues):
    """Add hints using direct /api/v1/hints endpoint"""
    added = 0
    for i, clue in enumerate(clues, 1):
        clue = str(clue)
        
        if not clue or clue.lower() == "n/a":
            continue
        
        # Skip if it looks like a flag
        if "{" in clue and "}" in clue:
            continue
        
        hint_data = {
            "challenge_id": challenge_id,
            "content": str(clue)[:1000],
            "cost": 10 * i
        }

        try:
            # Try direct /api/v1/hints endpoint
            response = requests.post(
                f"{CTFd_URL}/api/v1/hints",
                json=hint_data,
                headers=HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"  ✓ Hint {i} added: {clue[:30]}...")
                added += 1
            else:
                pass
        except:
            pass

    return added


def main():
    """Main import function"""
    print("=" * 70)
    print("CTFd Challenge Importer v3 (With Flags & Hints)")
    print("=" * 70)
    
    if ADMIN_TOKEN == "YOUR_ADMIN_TOKEN_HERE":
        print("\n⚠️  ADMIN_TOKEN not set!")
        sys.exit(1)
    
    challenges = load_challenges()
    print(f"\nLoaded {len(challenges)} challenges from {JSON_FILE}\n")
    
    imported = 0
    failed = 0
    flags_added = 0
    hints_added = 0
    
    for idx, challenge in enumerate(challenges, 1):
        print(f"\n[{idx}/{len(challenges)}] {challenge.get('qtitle', 'Unknown')}")
        print("-" * 70)
        
        # Create challenge
        challenge_id = create_challenge(challenge)
        
        if challenge_id:
            imported += 1
            
            # Add flag
            answer = extract_answer(challenge)
            if answer:
                if add_flag(challenge_id, answer):
                    flags_added += 1
            
            # Add hints
            clues = [
                challenge.get("clue1", ""),
                challenge.get("clue2", ""),
                challenge.get("clue3", "")
            ]
            hints_count = add_hints(challenge_id, clues)
            hints_added += hints_count
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"✓ Challenges created: {imported}")
    print(f"✓ Flags added: {flags_added}")
    print(f"✓ Hints added: {hints_added}")
    print(f"✗ Failed imports: {failed}")
    print(f"Total: {len(challenges)}")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Visit: http://localhost/admin/challenges")
    print("2. Click on each challenge to verify flags & hints are visible")
    print("3. If any are missing, you can add them manually:")
    print("   - Flags Tab → Add flag content")
    print("   - Hints Tab → Add hint content with cost")


if __name__ == "__main__":
    main()
