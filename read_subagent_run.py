import json

with open("C:/Users/Eduardo/.gemini/antigravity-ide/brain/92902ca4-1cba-4ec9-86a3-0d95bb25682b/.system_generated/logs/transcript.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        # We want to print any model response or subagent result after step 215
        if data.get("step_index", 0) >= 215:
            print(f"Step {data.get('step_index')} (type={data.get('type')}, source={data.get('source')}):")
            content = data.get("content", "")
            print(content[:1000]) # First 1000 characters
            print("=" * 60)
