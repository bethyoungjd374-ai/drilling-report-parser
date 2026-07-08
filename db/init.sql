CREATE DATABASE IF NOT EXISTS drilling_report_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE drilling_report_db;

CREATE TABLE IF NOT EXISTS report_records (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_id VARCHAR(191) NOT NULL,
  report_type VARCHAR(32) NOT NULL,
  source_file VARCHAR(512) NOT NULL DEFAULT '',
  parser VARCHAR(128) NOT NULL DEFAULT '',
  report_date VARCHAR(32) NOT NULL DEFAULT '',
  report_no VARCHAR(64) NOT NULL DEFAULT '',
  wellbore VARCHAR(128) NOT NULL DEFAULT '',
  rig VARCHAR(128) NOT NULL DEFAULT '',
  status VARCHAR(64) NOT NULL DEFAULT '',
  validation_status VARCHAR(64) NOT NULL DEFAULT '',
  validation_warnings TEXT NULL,
  locked VARCHAR(32) NOT NULL DEFAULT '',
  confirmation_status VARCHAR(64) NOT NULL DEFAULT '',
  confirmed_at VARCHAR(64) NOT NULL DEFAULT '',
  confirmed_by VARCHAR(128) NOT NULL DEFAULT '',
  confirmation_note TEXT NULL,
  created_at VARCHAR(64) NOT NULL DEFAULT '',
  updated_at VARCHAR(64) NOT NULL DEFAULT '',
  inserted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  mysql_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_report_records_record_id (record_id),
  KEY idx_report_records_type_date (report_type, report_date),
  KEY idx_report_records_well_date (wellbore, report_date),
  KEY idx_report_records_rig (rig)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS report_fields (
  record_id VARCHAR(191) NOT NULL,
  fields_json JSON NOT NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (record_id),
  CONSTRAINT fk_report_fields_record
    FOREIGN KEY (record_id) REFERENCES report_records(record_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS report_rows (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_id VARCHAR(191) NOT NULL,
  module_name VARCHAR(64) NOT NULL,
  row_no INT NOT NULL,
  row_json JSON NOT NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_report_rows_record_module_row (record_id, module_name, row_no),
  KEY idx_report_rows_module (module_name),
  CONSTRAINT fk_report_rows_record
    FOREIGN KEY (record_id) REFERENCES report_records(record_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
