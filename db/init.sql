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
  source_language VARCHAR(16) NOT NULL DEFAULT '',
  translation_status VARCHAR(64) NOT NULL DEFAULT '',
  translation_progress VARCHAR(16) NOT NULL DEFAULT '',
  translation_error TEXT NULL,
  translation_version VARCHAR(64) NOT NULL DEFAULT '',
  translation_updated_at VARCHAR(64) NOT NULL DEFAULT '',
  extraction_status VARCHAR(64) NOT NULL DEFAULT '',
  extraction_progress VARCHAR(16) NOT NULL DEFAULT '',
  extraction_error TEXT NULL,
  extraction_version VARCHAR(64) NOT NULL DEFAULT '',
  extraction_updated_at VARCHAR(64) NOT NULL DEFAULT '',
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

CREATE TABLE IF NOT EXISTS translation_content (
  record_id VARCHAR(191) NOT NULL,
  entity_type VARCHAR(64) NOT NULL,
  entity_id VARCHAR(255) NOT NULL,
  field_code VARCHAR(128) NOT NULL,
  source_language VARCHAR(16) NOT NULL DEFAULT '',
  target_language VARCHAR(16) NOT NULL,
  source_text MEDIUMTEXT NULL,
  translated_text MEDIUMTEXT NULL,
  source_hash VARCHAR(64) NOT NULL DEFAULT '',
  model_config_id VARCHAR(128) NOT NULL DEFAULT '',
  prompt_version VARCHAR(64) NOT NULL DEFAULT '',
  translation_status VARCHAR(64) NOT NULL DEFAULT '',
  error_message TEXT NULL,
  is_manual_modified VARCHAR(16) NOT NULL DEFAULT '',
  updated_at VARCHAR(64) NOT NULL DEFAULT '',
  created_at VARCHAR(64) NOT NULL DEFAULT '',
  mysql_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (record_id, entity_id, field_code, target_language),
  KEY idx_translation_content_status (translation_status),
  CONSTRAINT fk_translation_content_record
    FOREIGN KEY (record_id) REFERENCES report_records(record_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ai_extraction_results (
  record_id VARCHAR(191) NOT NULL,
  rule_id VARCHAR(80) NOT NULL,
  source_section VARCHAR(64) NOT NULL,
  source_row_no INT NOT NULL DEFAULT 0,
  source_field VARCHAR(128) NOT NULL,
  target_field VARCHAR(128) NOT NULL,
  source_hash VARCHAR(64) NOT NULL DEFAULT '',
  result_text TEXT NULL,
  extraction_status VARCHAR(64) NOT NULL DEFAULT '',
  error_message TEXT NULL,
  model_config_id VARCHAR(128) NOT NULL DEFAULT '',
  rule_version VARCHAR(64) NOT NULL DEFAULT '',
  attempt_count INT NOT NULL DEFAULT 0,
  started_at VARCHAR(64) NOT NULL DEFAULT '',
  completed_at VARCHAR(64) NOT NULL DEFAULT '',
  updated_at VARCHAR(64) NOT NULL DEFAULT '',
  mysql_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (record_id, rule_id, source_section, source_row_no, target_field),
  KEY idx_ai_extraction_status (extraction_status),
  CONSTRAINT fk_ai_extraction_record FOREIGN KEY (record_id) REFERENCES report_records(record_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
