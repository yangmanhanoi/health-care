#!/usr/bin/env python
"""
Script to add multiple test types to the laboratory service database.

Usage:
    python add_test_types.py [--replace] [--host HOST] [--port PORT] [--user USER] [--password PASSWORD] [--db DB]

Options:
    --replace    Replace existing test types with the same name
    --host       Database host (default: localhost)
    --port       Database port (default: 5432)
    --user       Database user (default: namdt25)
    --password   Database password (default: namdt25)
    --db         Database name (default: laboratory_db)
"""

import os
import sys
import django
import argparse
import logging
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Add multiple test types to the laboratory service')
    parser.add_argument('--replace', action='store_true', help='Replace existing test types with the same name')
    parser.add_argument('--host', default='localhost', help='Database host (default: localhost)')
    parser.add_argument('--port', default='5432', help='Database port (default: 5432)')
    parser.add_argument('--user', default='namdt25', help='Database user (default: namdt25)')
    parser.add_argument('--password', default='namdt25', help='Database password (default: namdt25)')
    parser.add_argument('--db', default='laboratory_db', help='Database name (default: laboratory_db)')
    args = parser.parse_args()

    # Set database connection environment variables
    os.environ['POSTGRES_HOST'] = args.host
    os.environ['POSTGRES_PORT'] = args.port
    os.environ['POSTGRES_USER'] = args.user
    os.environ['POSTGRES_PASSWORD'] = args.password
    os.environ['POSTGRES_DB'] = args.db

    # Setup Django environment after setting database connection variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laboratory_service.settings')

    try:
        django.setup()
        # Test database connection
        from django.db import connection
        connection.ensure_connection()
        logger.info(f"Successfully connected to database at {args.host}:{args.port}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.error("Please check your database connection parameters")
        sys.exit(1)

    # Define a list of common laboratory test types
    test_types = [
        {
            'name': 'Complete Blood Count (CBC)',
            'description': 'Measures different components of blood including red cells, white cells, and platelets',
            'cost': Decimal('25.00'),
            'unit': 'various',
            'normal_range': 'varies by component',
        },
        {
            'name': 'Blood Glucose',
            'description': 'Measures the amount of glucose in the blood',
            'cost': Decimal('15.00'),
            'unit': 'mg/dL',
            'normal_range': '70-99',
        },
        {
            'name': 'Hemoglobin A1C',
            'description': 'Measures average blood glucose levels over the past 2-3 months',
            'cost': Decimal('30.00'),
            'unit': '%',
            'normal_range': '4.0-5.6',
        },
        {
            'name': 'Lipid Panel',
            'description': 'Measures cholesterol and triglycerides in the blood',
            'cost': Decimal('35.00'),
            'unit': 'mg/dL',
            'normal_range': 'varies by component',
        },
        {
            'name': 'Liver Function Test',
            'description': 'Measures enzymes and proteins that indicate liver function',
            'cost': Decimal('40.00'),
            'unit': 'U/L',
            'normal_range': 'varies by component',
        },
        {
            'name': 'Kidney Function Test',
            'description': 'Measures substances that indicate kidney function',
            'cost': Decimal('35.00'),
            'unit': 'mg/dL',
            'normal_range': 'varies by component',
        },
        {
            'name': 'Thyroid Function Test',
            'description': 'Measures thyroid hormones and TSH',
            'cost': Decimal('45.00'),
            'unit': 'mIU/L',
            'normal_range': 'varies by component',
        },
        {
            'name': 'Urinalysis',
            'description': 'Analyzes the physical, chemical, and microscopic properties of urine',
            'cost': Decimal('20.00'),
            'unit': 'various',
            'normal_range': 'varies by component',
        },
        {
            'name': 'Electrolyte Panel',
            'description': 'Measures sodium, potassium, chloride, and bicarbonate levels',
            'cost': Decimal('30.00'),
            'unit': 'mmol/L',
            'normal_range': 'varies by component',
        },
        {
            'name': 'C-Reactive Protein (CRP)',
            'description': 'Measures inflammation in the body',
            'cost': Decimal('25.00'),
            'unit': 'mg/L',
            'normal_range': '0-10',
        },
        {
            'name': 'Vitamin D',
            'description': 'Measures vitamin D levels in the blood',
            'cost': Decimal('50.00'),
            'unit': 'ng/mL',
            'normal_range': '20-50',
        },
        {
            'name': 'Iron Panel',
            'description': 'Measures iron levels and related proteins in the blood',
            'cost': Decimal('40.00'),
            'unit': 'μg/dL',
            'normal_range': 'varies by component',
        },
        {
            'name': 'Coagulation Panel',
            'description': 'Measures how well blood clots',
            'cost': Decimal('35.00'),
            'unit': 'seconds',
            'normal_range': 'varies by component',
        },
        {
            'name': 'Vitamin B12',
            'description': 'Measures vitamin B12 levels in the blood',
            'cost': Decimal('45.00'),
            'unit': 'pg/mL',
            'normal_range': '200-900',
        },
        {
            'name': 'Folate',
            'description': 'Measures folate levels in the blood',
            'cost': Decimal('40.00'),
            'unit': 'ng/mL',
            'normal_range': '2.7-17.0',
        },
    ]

    created_count = 0
    updated_count = 0
    skipped_count = 0

    # Import TestType locally to avoid issues with circular imports
    from laboratory.models import TestType

    for test_type_data in test_types:
        name = test_type_data['name']

        try:
            # Check if test type already exists
            existing_test_type = TestType.objects.filter(name=name).first()

            if existing_test_type:
                if args.replace:
                    # Update existing test type
                    for key, value in test_type_data.items():
                        setattr(existing_test_type, key, value)
                    existing_test_type.save()
                    updated_count += 1
                    logger.info(f'Updated test type: {name}')
                else:
                    # Skip if test type already exists
                    skipped_count += 1
                    logger.info(f'Skipped existing test type: {name}')
            else:
                # Create new test type
                TestType.objects.create(**test_type_data)
                created_count += 1
                logger.info(f'Created test type: {name}')
        except Exception as e:
            logger.error(f"Error processing test type '{name}': {e}")
            continue

    # Print summary
    logger.info(f'Summary: {created_count} created, {updated_count} updated, {skipped_count} skipped')

if __name__ == '__main__':
    main()
