# MySQL Initialization Scripts

This directory contains MySQL initialization scripts that are automatically executed when the MySQL container starts for the first time.

## Files

### 01-init-databases.sql

- Creates all required databases for the healthcare system
- Sets up user permissions
- Creates the following databases:
  - `healthcare_sys` - for auth_service
  - `doctor_db` - for doctor_service
  - `appointment_db` - for appointment_service
  - `patient_db` - for patient_service
  - `chatbot_db` - for chatbot_service
  - `prescription_db` - for prescription_service

### 02-default-data.sql

- Contains placeholder scripts for inserting default/seed data
- Currently contains commented examples
- Can be uncommented and modified to insert actual default data

## How It Works

1. When the MySQL container starts for the first time, it automatically executes all `.sql` files in the `/docker-entrypoint-initdb.d` directory
2. Files are executed in alphabetical order (hence the numbering)
3. The scripts only run on the first container startup (when the data volume is empty)

## Database Configuration

Each microservice is configured to use its own database:

- **Auth Service**: `healthcare_sys`
- **Doctor Service**: `doctor_db`
- **Appointment Service**: `appointment_db`
- **Patient Service**: `patient_db`
- **Chatbot Service**: `chatbot_db`
- **Prescription Service**: `prescription_db`

**Note**: Laboratory and Pharmacy services use PostgreSQL databases (`laboratory_db` and `pharmacy_db`).

## User Permissions

The user `namdt25` is granted:

- Full privileges on all healthcare databases
- CREATE, DROP, ALTER, INDEX, REFERENCES privileges
- Access from any host (`%`)

## Troubleshooting

### Migration Errors

If you encounter migration errors like "Table 'django_migrations' already exists":

**Option 1: Use the reset script (Recommended)**

```bash
./reset-databases.sh
```

**Option 2: Manual reset**

1. Stop the containers: `docker-compose down`
2. Remove the MySQL volume: `docker volume rm health-care_healthcare_mysql_data`
3. Start the containers again: `docker-compose up`

**Option 3: Check volume name**
If the volume name is different, list all volumes:

```bash
docker volume ls
```

Then remove the correct one:

```bash
docker volume rm [actual-volume-name]
```

### Common Issues

1. **"django_migrations table already exists"**

   - This happens when database names change but old tables remain
   - Solution: Reset the databases using the methods above

2. **"Access denied for user"**

   - Check that the user permissions are set correctly
   - Verify the initialization scripts ran properly

3. **"Can't connect to MySQL server"**
   - Ensure MySQL health check is passing
   - Check if the 5-second delay is sufficient
   - Verify network connectivity between containers

## Adding Default Data

To add default data:

1. Edit `02-default-data.sql`
2. Uncomment and modify the example INSERT statements
3. Add your own INSERT statements as needed
4. Restart the MySQL container (only if it's the first time)
