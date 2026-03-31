"""
Script to import CTF challenges from csvjson.json into CTFd
"""

import json
import requests
import sys

# Configuration
CTFd_URL = "http://localhost:80"
ADMIN_TOKEN = "ctfd_7273e0c998a1b96085c1a819457fbc5943ad1ef40eda099b72a336b371d71e4d"  # Replace with your actual admin token
JSON_FILE = "csvjson.json"

# Headers for API requests
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
    except json.JSONDecodeError:
        print(f"Error: {JSON_FILE} is not valid JSON")
        sys.exit(1)


def create_challenge(challenge_data):
    """Create a challenge via CTFd API"""
    # Map the data to CTFd format
    ctf_challenge = {
        "name": challenge_data.get("qtitle", "Unnamed Challenge"),
        "description": f"{challenge_data.get('qdesc', '')}\n\n{challenge_data.get('question', '')}".strip(),
        "category": challenge_data.get("link", "General").replace("https://", "").split("/")[0] or "General",
        "value": challenge_data.get("points", 100),
        "type": "standard",  # You can modify based on qtype
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
            print(f"✓ Created: {ctf_challenge['name']} (ID: {challenge_id})")
            return challenge_id
        else:
            print(f"✗ Failed to create {ctf_challenge['name']}: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating challenge: {e}")
        return None


def add_flags(challenge_id, answer):
    """Add flags to a challenge"""
    if not answer or answer == "":
        return False
    
    flag_data = {
        "content": answer,
        "type": "static"
    }

    try:
        response = requests.post(
            f"{CTFd_URL}/api/v1/challenges/{challenge_id}/flags",
            json=flag_data,
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✓ Added flag: {answer}")
            return True
        else:
            print(f"  ✗ Failed to add flag: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error adding flag: {e}")
        return False


def add_hints(challenge_id, clues):
    """Add hints to a challenge"""
    for i, clue in enumerate(clues, 1):
        if not clue or clue == "N/A":
            continue
        
        hint_data = {
            "content": clue,
            "cost": 10 * i  # 10 points for clue1, 20 for clue2, etc.
        }

        try:
            response = requests.post(
                f"{CTFd_URL}/api/v1/challenges/{challenge_id}/hints",
                json=hint_data,
                headers=HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"  ✓ Added hint {i}: {clue[:50]}...")
            else:
                print(f"  ✗ Failed to add hint {i}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error adding hint {i}: {e}")


def main():
    """Main import function"""
    print("=" * 60)
    print("CTFd Challenge Importer")
    print("=" * 60)
    
    # Check admin token
    if ADMIN_TOKEN == "YOUR_ADMIN_TOKEN_HERE":
        print("\n⚠️  WARNING: ADMIN_TOKEN not set!")
        print("Steps to get your admin token:")
        print("1. Log in to CTFd Admin Panel")
        print("2. Go to Settings → API")
        print("3. Create a new token with 'admin' role")
        print("4. Replace ADMIN_TOKEN in this script with your token\n")
        sys.exit(1)
    
    # Load challenges
    challenges = load_challenges()
    print(f"\nLoaded {len(challenges)} challenges from {JSON_FILE}\n")
    
    imported = 0
    failed = 0
    
    for idx, challenge in enumerate(challenges, 1):
        print(f"\n[{idx}/{len(challenges)}] Processing: {challenge.get('qtitle', 'Unknown')}")
        print("-" * 60)
        
        # Create challenge
        challenge_id = create_challenge(challenge)
        
        if challenge_id:
            imported += 1
            
            # Add flags
            answer = challenge.get("answer", "")
            add_flags(challenge_id, answer)
            
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
    print("\nVisit http://localhost:4000/admin/challenges to view your challenges!")


if __name__ == "__main__":
    main()
