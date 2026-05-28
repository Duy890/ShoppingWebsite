"""Fix seed_data.py: remove duplicates, fix JS booleans, clean up __main__."""
import re

path = "app/seed_data.py"

with open(path, encoding="utf-8") as f:
    lines = f.readlines()

# Find all function definition lines
func_lines = [i for i, l in enumerate(lines) if "def seed_laptops_from_csv" in l]
print(f"Found {len(func_lines)} function defs at lines {[l + 1 for l in func_lines]}")

# Part 1: original code before first function def
part1 = lines[: func_lines[0]]

# Part 2: only the LAST function definition
part2 = "".join(lines[func_lines[-1] :])

# Fix JS booleans in part2
part2 = re.sub(r"\btrue\b", "True", part2)
part2 = re.sub(r"\bfalse\b", "False", part2)

# Insert seed_laptops_from_csv call into main() before SEED COMPLETE
part1_str = "".join(part1)
part1_str = part1_str.replace(
    '        print("\\n=== SEED COMPLETE ===")',
    '        print("Seeding laptops from CSV...")\n        seed_laptops_from_csv(db)\n\n        print("\\n=== SEED COMPLETE ===")',
)

# Replace the __main__ block to just call main()
part1_str = re.sub(
    r'if __name__ == "__main__":\s*\n\s+main\(\)\s*\n\s+db = SessionLocal\(\)\s*\n\s+try:\s*\n\s+seed_laptops_from_csv\(db\)\s*\n\s+finally:\s*\n\s+db\.close\(\)',
    'if __name__ == "__main__":\n    main()',
    part1_str,
)

result = part1_str + part2

with open(path, "w", encoding="utf-8") as f:
    f.write(result)

# Verify
js_true = re.findall(r"\btrue\b", result)
js_false = re.findall(r"\bfalse\b", result)
func_count = result.count("def seed_laptops_from_csv")
print(f"Total lines: {len(result.splitlines())}")
print(f"Function defs remaining: {func_count}")
print(f"JS 'true' remaining: {len(js_true)}")
print(f"JS 'false' remaining: {len(js_false)}")
print("Done.")
