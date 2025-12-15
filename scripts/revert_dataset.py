
filepath = "data/akura_dataset.json"
line_limit = 164

try:
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    if len(lines) > line_limit:
        print(f"Trimming {filepath} from {len(lines)} to {line_limit} lines...")
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines[:line_limit])
        print("Done.")
    else:
        print("File is already within limit.")

except Exception as e:
    print(f"Error: {e}")
