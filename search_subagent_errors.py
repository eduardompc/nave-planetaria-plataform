import json

log_path = "C:/Users/Eduardo/.gemini/antigravity-ide/brain/6e705346-793e-44fc-90bd-4df35e36191a/.system_generated/logs/transcript.jsonl"
output_path = "subagent_results.txt"

with open(log_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as out:
    for line in f:
        data = json.loads(line)
        step = data.get("step_index", 0)
        # We want steps related to valida_final_2 subagent (step >= 210)
        if step >= 210:
            source = data.get("source", "")
            type_ = data.get("type", "")
            content = data.get("content", "")
            tool_calls = data.get("tool_calls", [])
            
            out.write(f"=== Step {step} | Source: {source} | Type: {type_} ===\n")
            if tool_calls:
                out.write(f"Tool Calls: {json.dumps(tool_calls, indent=2, ensure_ascii=False)}\n")
            if content:
                out.write(f"Content:\n{content}\n")
            out.write("\n" + "="*80 + "\n\n")

print("Done writing subagent results!")
