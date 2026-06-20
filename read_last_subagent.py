log_path = "C:/Users/Eduardo/.gemini/antigravity-ide/brain/6e705346-793e-44fc-90bd-4df35e36191a/.system_generated/tasks/task-341.log"
output_path = "server_log_tail_5.txt"

try:
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    with open(output_path, "w", encoding="utf-8") as out:
        out.writelines(lines[-200:])
    print(f"Done writing server log tail! Total lines in log: {len(lines)}")
except Exception as e:
    print("Error:", e)
