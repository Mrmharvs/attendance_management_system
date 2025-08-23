CREATE DATABASE attendance_db;

USE attendance_db;

-- Student table with NFC UID + Face embedding
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nfc_uid VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    mi VARCHAR(5),
    course VARCHAR(50),
    year VARCHAR(10),
    subject VARCHAR(100),
    room VARCHAR(50),
    embedding BLOB
);

CREATE TABLE status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE
);

-- Attendance log
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    status_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (status_id) REFERENCES status(id)
);

INSERT INTO status (name) VALUES
('Present'),
('Late'),
('Failed');
ALTER TABLE attendance ADD COLUMN status_message VARCHAR(100);

SELECT a.id, s.first_name, s.last_name, a.timestamp, st.name AS status
FROM attendance a
JOIN students s ON a.student_id = s.id
JOIN status st ON a.status_id = st.id;