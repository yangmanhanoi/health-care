-- Default data initialization script for healthcare system
-- This script can be used to insert default/seed data after database creation

-- Switch to healthcare_sys database for auth service default data
USE healthcare_sys;

-- Note: Django will create the actual tables through migrations
-- This script is prepared for future default data insertion

-- Insert default user roles for the healthcare system
-- Table name follows Django convention: api_role (app_name_model_name)
INSERT IGNORE INTO api_role (name) VALUES
('ADMIN'),
('DOCTOR'),
('PATIENT'),
('STAFF'),
('customer');

-- Switch to doctor_db for doctor service default data
USE doctor_db;

-- Example: Insert default specialties (uncomment when needed)
-- INSERT IGNORE INTO doctor_specialties (name, description) VALUES
-- ('Cardiology', 'Heart and cardiovascular system'),
-- ('Neurology', 'Nervous system and brain'),
-- ('Pediatrics', 'Medical care of infants, children, and adolescents'),
-- ('Orthopedics', 'Musculoskeletal system'),
-- ('Dermatology', 'Skin, hair, and nails');

-- Switch to appointment_db for appointment service default data
USE appointment_db;

-- Example: Insert default appointment types (uncomment when needed)
-- INSERT IGNORE INTO appointment_types (name, duration_minutes, description) VALUES
-- ('Consultation', 30, 'General medical consultation'),
-- ('Follow-up', 15, 'Follow-up appointment'),
-- ('Emergency', 60, 'Emergency medical consultation'),
-- ('Specialist', 45, 'Specialist consultation');

-- Switch to patient_db for patient service default data
USE patient_db;

-- Example: Insert default patient categories (uncomment when needed)
-- INSERT IGNORE INTO patient_categories (name, description) VALUES
-- ('Regular', 'Regular outpatient'),
-- ('Emergency', 'Emergency patient'),
-- ('Inpatient', 'Admitted patient'),
-- ('Pediatric', 'Child patient');

-- Log completion
SELECT 'Database initialization completed successfully' AS status;
