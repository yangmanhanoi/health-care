# Test Types Management Command

This directory contains a Django management command to add multiple test types to the laboratory service database.

## Usage

### Using Django Management Command

```bash
# Add test types (skips existing ones)
python manage.py add_test_types

# Add test types and replace existing ones
python manage.py add_test_types --replace
```

### Using Standalone Script

Alternatively, you can use the standalone script in the root directory:

```bash
# Add test types (skips existing ones)
python add_test_types.py

# Add test types and replace existing ones
python add_test_types.py --replace

# Connect to a specific database
python add_test_types.py --host localhost --port 5432 --user namdt25 --password namdt25 --db laboratory_db
```

The standalone script supports the following options:

- `--replace`: Replace existing test types with the same name
- `--host`: Database host (default: localhost)
- `--port`: Database port (default: 5432)
- `--user`: Database user (default: namdt25)
- `--password`: Database password (default: namdt25)
- `--db`: Database name (default: laboratory_db)

## Test Types Included

The script adds the following common laboratory test types:

1. Complete Blood Count (CBC)
2. Blood Glucose
3. Hemoglobin A1C
4. Lipid Panel
5. Liver Function Test
6. Kidney Function Test
7. Thyroid Function Test
8. Urinalysis
9. Electrolyte Panel
10. C-Reactive Protein (CRP)
11. Vitamin D
12. Iron Panel
13. Coagulation Panel
14. Vitamin B12
15. Folate

Each test type includes:
- Name
- Description
- Cost
- Unit of measurement
- Normal range values

## Customization

To add more test types or modify existing ones, edit the `test_types` list in the script.
