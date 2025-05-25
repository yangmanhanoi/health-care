# PostgreSQL Initialization Scripts

This directory contains PostgreSQL initialization scripts that are automatically executed when the PostgreSQL container starts for the first time.

## Files

### 01-init-databases.sql

- Creates all required PostgreSQL databases for the healthcare system
- Sets up user permissions
- Creates the following databases:
  - `laboratory_db` - for laboratory_service
  - `pharmacy_db` - for pharmacy_service

## How It Works

1. When the PostgreSQL container starts for the first time, it automatically executes all `.sql` files in the `/docker-entrypoint-initdb.d` directory
2. Files are executed in alphabetical order (hence the numbering)
3. The scripts only run on the first container startup (when the data volume is empty)

## Database Configuration

Each microservice is configured to use its own database:

- **Laboratory Service**: `laboratory_db`
- **Pharmacy Service**: `pharmacy_db`

## User Permissions

The user `namdt25` is granted:

- Full privileges on all PostgreSQL databases
- Schema-level permissions
- Table and sequence permissions
- Access from any host

## Troubleshooting

### Migration Errors

If you encounter migration errors:

**Option 1: Use the reset script (Recommended)**

```bash
docker-compose down
docker volume rm health-care_healthcare_postgres_data
docker-compose up
```

**Option 2: Check volume name**
If the volume name is different, list all volumes:

```bash
docker volume ls
```

Then remove the correct one:

```bash
docker volume rm [actual-volume-name]
```

### Common Issues

1. **"relation already exists"**
   - This happens when database names change but old tables remain
   - Solution: Reset the databases using the methods above

2. **"permission denied"**
   - Check that the user permissions are set correctly
   - Verify the initialization scripts ran properly

3. **"could not connect to server"**
   - Ensure PostgreSQL health check is passing
   - Check if the 5-second delay is sufficient
   - Verify network connectivity between containers
