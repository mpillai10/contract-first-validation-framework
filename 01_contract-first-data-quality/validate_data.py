import csv
import json
import argparse
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='logs/validation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validate_row(row, schema):
    errors = []
    for field in schema['fields']:
        name = field['name']
        dtype = field['type']
        required = field.get('required', False)

        if required and not row.get(name):
            errors.append(f"Missing required field: {name}")
            continue

        value = row.get(name)

        if dtype == 'int':
            try:
                int(value)
            except (ValueError, TypeError):
                errors.append(f"Invalid int for {name}: {value}")
        elif dtype == 'float':
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append(f"Invalid float for {name}: {value}")
        elif dtype == 'str':
            if not isinstance(value, str):
                errors.append(f"Invalid str for {name}: {value}")
        # Add more types if needed

    return errors

def validate_data(schema_file, data_file, output_file):
    logging.info("Validation started")
    
    with open(schema_file) as sf:
        schema = json.load(sf)

    with open(data_file) as df:
        reader = csv.DictReader(df)
        rows = list(reader)

    error_rows = []
    total = len(rows)
    failed = 0

    for i, row in enumerate(rows, start=1):
        errors = validate_row(row, schema)
        if errors:
            failed += 1
            error_rows.append({
                'row': i,
                'errors': '; '.join(errors),
                'data': row
            })

    with open(output_file, 'w', newline='') as ef:
        fieldnames = ['row', 'errors', 'data']
        writer = csv.DictWriter(ef, fieldnames=fieldnames)
        writer.writeheader()
        for er in error_rows:
            writer.writerow(er)

    success = total - failed
    logging.info(f"Validation complete. Processed {total} rows. Failed: {failed}. Passed: {success}.")

    print("✅ Validation Summary:")
    print(f"   Total records: {total}")
    print(f"   Passed: {success}")
    print(f"   Failed: {failed}")
    print(f"   Failure rate: {round((failed/total)*100, 2)}%" if total > 0 else "   No data found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate CSV data using a JSON contract schema.')
    parser.add_argument('--schema', required=True, help='Path to JSON schema file')
    parser.add_argument('--data', required=True, help='Path to CSV data file')
    parser.add_argument('--output', required=True, help='Path to output error file')

    args = parser.parse_args()
    validate_data(args.schema, args.data, args.output)
