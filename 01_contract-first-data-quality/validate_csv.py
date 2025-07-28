import pandas as pd
import json
import re

# Load contract
with open("Customer_Contract.json", "r") as f:
    contract = json.load(f)

# Load data
df = pd.read_csv("Custome_Data.csv")
errors = []
def is_email(value):
    return re.match(r"[^@]+@[^@]+\.[^@]+", str(value)) is not None

def validate_column(row, col_name, rules, seen_uniques):
    row_errors = []
    value = row[col_name]

    # Required check
    if rules.get("required") and pd.isnull(value):
        row_errors.append(f"{col_name}: missing required value")
        return row_errors

    # Type check
    if rules.get("type") == "integer":
        try:
            int_val = int(value)
        except:
            row_errors.append(f"{col_name}: expected integer, got '{value}'")
            return row_errors
    elif rules.get("type") == "string":
        if not isinstance(value, str) and not pd.isnull(value):
            row_errors.append(f"{col_name}: expected string, got '{value}'")

    # Format check
    if rules.get("format") == "email" and not pd.isnull(value):
        if not is_email(value):
            row_errors.append(f"{col_name}: invalid email format")

    # Range check
    if rules.get("type") == "integer":
        val = int(value)
        if "min" in rules and val < rules["min"]:
            row_errors.append(f"{col_name}: value {val} < min {rules['min']}")
        if "max" in rules and val > rules["max"]:
            row_errors.append(f"{col_name}: value {val} > max {rules['max']}")

    # Allowed values
    if "allowed_values" in rules and not pd.isnull(value):
        if value not in rules["allowed_values"]:
            row_errors.append(f"{col_name}: value '{value}' not allowed")

    # Uniqueness
    if rules.get("unique"):
        if value in seen_uniques.get(col_name, set()):
            row_errors.append(f"{col_name}: duplicate value '{value}'")
        else:
            seen_uniques.setdefault(col_name, set()).add(value)

    return row_errors
seen_uniques = {}
for idx, row in df.iterrows():
    row_error_list = []
    for col, rules in contract["columns"].items():
        if col in df.columns:
            row_error_list.extend(validate_column(row, col, rules, seen_uniques))
    if row_error_list:
        errors.append({"row": idx + 2, "errors": row_error_list})  # +2 for header + 0-indexing
# Print errors
if errors:
    print("Validation Errors Found:")
    for err in errors:
        print(f"Row {err['row']}:")
        for e in err['errors']:
            print(f"  - {e}")
else:
    print("✅ All records passed validation.")
if errors:
    error_df = pd.DataFrame([
        {"row": e["row"], "error": "; ".join(e["errors"])} for e in errors
    ])
    error_df.to_csv("validation_errors.csv", index=False)
    print("🔍 Errors written to validation_errors.csv")
