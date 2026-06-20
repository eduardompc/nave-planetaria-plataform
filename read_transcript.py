import json

with open("C:/Users/Eduardo/.gemini/antigravity-ide/brain/92902ca4-1cba-4ec9-86a3-0d95bb25682b/.system_generated/logs/transcript.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        content = data.get("content", "")
        # Look for console logs or errors in MODEL messages
        if "console" in content.lower() or "500 (internal server error)" in content.lower():
            print(f"Step {data.get('step_index')} (type={data.get('type')}):")
            # Print around where console logs are
            idx = content.lower().find("console")
            if idx != -1:
                start = max(0, idx - 200)
                end = min(len(content), idx + 1000)
                print(content[start:end])
                print("-" * 50)
