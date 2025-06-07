-- Tables creation
CREATE TABLE IF NOT EXISTS applicant_profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS application_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    cv_path VARCHAR(255) NOT NULL,
    job_position VARCHAR(255),
    application_date DATE DEFAULT (CURDATE()),
    FOREIGN KEY (applicant_id) REFERENCES applicant_profile(id) ON DELETE CASCADE
);