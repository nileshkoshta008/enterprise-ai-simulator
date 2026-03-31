import requests
import json

BASE_URL = "http://localhost:8000"

def test_autopilot():
    try:
        # 1. Reset
        print("Resetting environment...")
        r = requests.post(f"{BASE_URL}/reset", json={"task_tier": "easy"})
        if r.status_code != 200:
            print(f"Reset failed: {r.status_code} {r.text}")
            return
        
        obs_data = r.json()
        state = obs_data.get("state")
        print(f"Current State: {state}")
        
        # 2. Auto-step
        print("Triggering auto-step...")
        r = requests.post(f"{BASE_URL}/auto-step", json={"state": state})
        if r.status_code != 200:
            print(f"Auto-step failed: {r.status_code}")
            print(f"Error Detail: {r.text}")
        else:
            print("Auto-step success!")
            print(json.dumps(r.json(), indent=2))
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_autopilot()
