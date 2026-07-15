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
  rig_id BIGINT UNSIGNED NULL,
  wellbore_id BIGINT UNSIGNED NULL,
  project_id BIGINT UNSIGNED NULL,
  job_id BIGINT UNSIGNED NULL,
  master_match_status VARCHAR(32) NOT NULL DEFAULT '',
  master_match_message TEXT NULL,
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
  KEY idx_report_records_rig (rig),
  KEY idx_report_records_master_refs (project_id, rig_id, wellbore_id, job_id),
  KEY idx_report_records_match_status (master_match_status)
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
  KEY idx_translation_memory_lookup (target_language, prompt_version, translation_status, source_hash),
  CONSTRAINT fk_translation_content_record
    FOREIGN KEY (record_id) REFERENCES report_records(record_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS translation_memory (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  source_language VARCHAR(16) NOT NULL DEFAULT '',
  target_language VARCHAR(16) NOT NULL,
  source_text MEDIUMTEXT NOT NULL,
  source_hash VARCHAR(64) NOT NULL,
  translated_text MEDIUMTEXT NOT NULL,
  report_type VARCHAR(32) NOT NULL DEFAULT '',
  operation_category VARCHAR(64) NOT NULL DEFAULT '',
  field_code VARCHAR(128) NOT NULL DEFAULT '',
  source_record_id VARCHAR(191) NOT NULL DEFAULT '',
  confirmed VARCHAR(16) NOT NULL DEFAULT 'true',
  confirmed_by VARCHAR(128) NOT NULL DEFAULT '',
  usage_count INT UNSIGNED NOT NULL DEFAULT 0,
  created_at VARCHAR(64) NOT NULL DEFAULT '',
  updated_at VARCHAR(64) NOT NULL DEFAULT '',
  mysql_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_translation_memory_scope (target_language, source_hash, report_type, field_code),
  KEY idx_translation_memory_confirmed (target_language, confirmed, source_hash),
  KEY idx_translation_memory_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS translation_revisions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_id VARCHAR(191) NOT NULL,
  entity_id VARCHAR(255) NOT NULL,
  field_code VARCHAR(128) NOT NULL,
  target_language VARCHAR(16) NOT NULL,
  source_text MEDIUMTEXT NULL,
  previous_text MEDIUMTEXT NULL,
  revised_text MEDIUMTEXT NOT NULL,
  revision_type VARCHAR(32) NOT NULL DEFAULT 'manual',
  editor VARCHAR(128) NOT NULL DEFAULT '',
  note TEXT NULL,
  created_at VARCHAR(64) NOT NULL DEFAULT '',
  inserted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_translation_revisions_record (record_id, target_language, created_at),
  CONSTRAINT fk_translation_revisions_record
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

CREATE TABLE IF NOT EXISTS md_geo_region (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  region_code VARCHAR(64) NOT NULL,
  region_name VARCHAR(255) NOT NULL,
  region_type_code VARCHAR(64) NOT NULL DEFAULT 'COUNTRY',
  iso_alpha2 VARCHAR(2) NOT NULL DEFAULT '',
  parent_id BIGINT UNSIGNED NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_geo_region_code (region_code),
  KEY idx_md_geo_region_parent (parent_id),
  CONSTRAINT fk_md_geo_region_parent FOREIGN KEY (parent_id) REFERENCES md_geo_region(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_appendix_category (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  category_code VARCHAR(64) NOT NULL,
  category_name VARCHAR(255) NOT NULL,
  parent_id BIGINT UNSIGNED NULL,
  level_no INT UNSIGNED NOT NULL DEFAULT 1,
  description VARCHAR(512) NOT NULL DEFAULT '',
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_appendix_category_code (category_code),
  KEY idx_md_appendix_category_parent (parent_id),
  CONSTRAINT fk_md_appendix_category_parent FOREIGN KEY (parent_id) REFERENCES md_appendix_category(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_appendix_value (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  category_id BIGINT UNSIGNED NOT NULL,
  value_code VARCHAR(64) NOT NULL,
  value_name VARCHAR(255) NOT NULL,
  parent_value_id BIGINT UNSIGNED NULL,
  level_no INT UNSIGNED NOT NULL DEFAULT 1,
  sort_order INT NOT NULL DEFAULT 100,
  display_color VARCHAR(16) NOT NULL DEFAULT '',
  description VARCHAR(512) NOT NULL DEFAULT '',
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_appendix_value_code (category_id, value_code),
  KEY idx_md_appendix_value_parent (parent_value_id),
  CONSTRAINT fk_md_appendix_value_category FOREIGN KEY (category_id) REFERENCES md_appendix_category(id),
  CONSTRAINT fk_md_appendix_value_parent FOREIGN KEY (parent_value_id) REFERENCES md_appendix_value(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_organization (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  organization_code VARCHAR(64) NOT NULL,
  organization_name VARCHAR(255) NOT NULL,
  organization_type VARCHAR(32) NOT NULL DEFAULT '',
  legal_name VARCHAR(255) NOT NULL DEFAULT '',
  country_region_id BIGINT UNSIGNED NULL,
  parent_id BIGINT UNSIGNED NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_organization_code (organization_code),
  KEY idx_md_organization_parent (parent_id),
  KEY idx_md_organization_region (country_region_id),
  CONSTRAINT fk_md_organization_parent FOREIGN KEY (parent_id) REFERENCES md_organization(id),
  CONSTRAINT fk_md_organization_region FOREIGN KEY (country_region_id) REFERENCES md_geo_region(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_field (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  field_code VARCHAR(64) NOT NULL,
  field_name VARCHAR(255) NOT NULL,
  region_id BIGINT UNSIGNED NULL,
  operator_company_id BIGINT UNSIGNED NULL,
  field_type_code VARCHAR(64) NOT NULL DEFAULT 'ONSHORE',
  lifecycle_status_code VARCHAR(64) NOT NULL DEFAULT 'ACTIVE',
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_field_code (field_code),
  KEY idx_md_field_region (region_id),
  KEY idx_md_field_operator (operator_company_id),
  CONSTRAINT fk_md_field_region FOREIGN KEY (region_id) REFERENCES md_geo_region(id),
  CONSTRAINT fk_md_field_operator FOREIGN KEY (operator_company_id) REFERENCES md_organization(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_block (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  block_code VARCHAR(64) NOT NULL,
  block_name VARCHAR(255) NOT NULL,
  country VARCHAR(128) NOT NULL DEFAULT '',
  area_name VARCHAR(255) NOT NULL DEFAULT '',
  field_name VARCHAR(255) NOT NULL DEFAULT '',
  platform_name VARCHAR(255) NOT NULL DEFAULT '',
  parent_id BIGINT UNSIGNED NULL,
  field_id BIGINT UNSIGNED NULL,
  region_id BIGINT UNSIGNED NULL,
  operator_company_id BIGINT UNSIGNED NULL,
  block_type_code VARCHAR(64) NOT NULL DEFAULT 'OPERATING_AREA',
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_block_code (block_code),
  KEY idx_md_block_parent (parent_id),
  KEY idx_md_block_field (field_id),
  KEY idx_md_block_region (region_id),
  KEY idx_md_block_operator (operator_company_id),
  CONSTRAINT fk_md_block_parent FOREIGN KEY (parent_id) REFERENCES md_block(id),
  CONSTRAINT fk_md_block_field FOREIGN KEY (field_id) REFERENCES md_field(id),
  CONSTRAINT fk_md_block_region FOREIGN KEY (region_id) REFERENCES md_geo_region(id),
  CONSTRAINT fk_md_block_operator FOREIGN KEY (operator_company_id) REFERENCES md_organization(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_team (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  team_code VARCHAR(64) NOT NULL,
  team_name VARCHAR(255) NOT NULL,
  team_type_code VARCHAR(64) NOT NULL DEFAULT 'DRILLING',
  company_id BIGINT UNSIGNED NULL,
  model_code VARCHAR(64) NOT NULL DEFAULT '',
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_team_code (team_code),
  KEY idx_md_team_company (company_id),
  CONSTRAINT fk_md_team_company FOREIGN KEY (company_id) REFERENCES md_organization(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_rig_model (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  model_code VARCHAR(64) NOT NULL,
  model_name VARCHAR(255) NOT NULL,
  equipment_type VARCHAR(32) NOT NULL DEFAULT '',
  specification_json JSON NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_rig_model_code (model_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_rig (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  rig_code VARCHAR(64) NOT NULL,
  rig_name VARCHAR(255) NOT NULL,
  rig_model_id BIGINT UNSIGNED NULL,
  owner_organization_id BIGINT UNSIGNED NULL,
  rig_type VARCHAR(32) NOT NULL DEFAULT '',
  team_id BIGINT UNSIGNED NULL,
  manufacturer VARCHAR(128) NOT NULL DEFAULT '',
  model_code VARCHAR(64) NOT NULL DEFAULT '',
  drive_type_code VARCHAR(64) NOT NULL DEFAULT '',
  rated_power_hp DECIMAL(12,2) NULL,
  rated_depth_m DECIMAL(12,2) NULL,
  equipment_status_code VARCHAR(64) NOT NULL DEFAULT 'AVAILABLE',
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_rig_code (rig_code),
  KEY idx_md_rig_model (rig_model_id),
  KEY idx_md_rig_owner (owner_organization_id),
  KEY idx_md_rig_team (team_id),
  CONSTRAINT fk_md_rig_model FOREIGN KEY (rig_model_id) REFERENCES md_rig_model(id),
  CONSTRAINT fk_md_rig_owner FOREIGN KEY (owner_organization_id) REFERENCES md_organization(id),
  CONSTRAINT fk_md_rig_team FOREIGN KEY (team_id) REFERENCES md_team(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_well (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  well_code VARCHAR(128) NOT NULL,
  well_name VARCHAR(255) NOT NULL DEFAULT '',
  block_id BIGINT UNSIGNED NULL,
  field_id BIGINT UNSIGNED NULL,
  operator_company_id BIGINT UNSIGNED NULL,
  well_type_code VARCHAR(64) NOT NULL DEFAULT 'DEVELOPMENT',
  surface_latitude DECIMAL(10,7) NULL,
  surface_longitude DECIMAL(10,7) NULL,
  lifecycle_status_code VARCHAR(64) NOT NULL DEFAULT 'ACTIVE',
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_well_code (well_code),
  KEY idx_md_well_block (block_id),
  KEY idx_md_well_field (field_id),
  KEY idx_md_well_operator (operator_company_id),
  CONSTRAINT fk_md_well_block FOREIGN KEY (block_id) REFERENCES md_block(id),
  CONSTRAINT fk_md_well_field FOREIGN KEY (field_id) REFERENCES md_field(id),
  CONSTRAINT fk_md_well_operator FOREIGN KEY (operator_company_id) REFERENCES md_organization(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_wellbore (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  wellbore_code VARCHAR(128) NOT NULL,
  wellbore_name VARCHAR(255) NOT NULL DEFAULT '',
  well_id BIGINT UNSIGNED NOT NULL,
  parent_wellbore_id BIGINT UNSIGNED NULL,
  block_id BIGINT UNSIGNED NULL,
  well_type VARCHAR(64) NOT NULL DEFAULT '',
  wellbore_profile_code VARCHAR(64) NOT NULL DEFAULT 'VERTICAL',
  trajectory_status_code VARCHAR(64) NOT NULL DEFAULT 'PLANNED',
  kickoff_md_m DECIMAL(12,2) NULL,
  planned_td_md_m DECIMAL(12,2) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_wellbore_code (wellbore_code),
  KEY idx_md_wellbore_well (well_id),
  KEY idx_md_wellbore_parent (parent_wellbore_id),
  KEY idx_md_wellbore_block (block_id),
  CONSTRAINT fk_md_wellbore_well FOREIGN KEY (well_id) REFERENCES md_well(id),
  CONSTRAINT fk_md_wellbore_parent FOREIGN KEY (parent_wellbore_id) REFERENCES md_wellbore(id),
  CONSTRAINT fk_md_wellbore_block FOREIGN KEY (block_id) REFERENCES md_block(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_contract (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  contract_no VARCHAR(128) NOT NULL,
  contract_name VARCHAR(255) NOT NULL DEFAULT '',
  customer_organization_id BIGINT UNSIGNED NULL,
  valid_from DATE NULL,
  valid_to DATE NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_contract_no (contract_no),
  KEY idx_md_contract_customer (customer_organization_id),
  CONSTRAINT fk_md_contract_customer FOREIGN KEY (customer_organization_id) REFERENCES md_organization(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_project (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  project_code VARCHAR(128) NOT NULL,
  project_name VARCHAR(255) NOT NULL,
  contract_id BIGINT UNSIGNED NULL,
  service_scope VARCHAR(255) NOT NULL DEFAULT '',
  valid_from DATE NULL,
  valid_to DATE NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_project_code (project_code),
  KEY idx_md_project_contract (contract_id),
  CONSTRAINT fk_md_project_contract FOREIGN KEY (contract_id) REFERENCES md_contract(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS md_alias (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  entity_type VARCHAR(32) NOT NULL,
  source_system VARCHAR(64) NOT NULL DEFAULT 'manual',
  alias_value VARCHAR(255) NOT NULL,
  normalized_alias VARCHAR(255) NOT NULL,
  entity_id BIGINT UNSIGNED NOT NULL,
  confirmation_status VARCHAR(32) NOT NULL DEFAULT 'confirmed',
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_md_alias_scope (entity_type, source_system, normalized_alias),
  KEY idx_md_alias_target (entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rel_project_team_assignment (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  project_id BIGINT UNSIGNED NOT NULL,
  team_id BIGINT UNSIGNED NOT NULL,
  valid_from DATETIME NOT NULL,
  valid_to DATETIME NULL,
  service_discipline VARCHAR(32) NOT NULL DEFAULT '',
  assignment_note VARCHAR(512) NOT NULL DEFAULT '',
  priority INT NOT NULL DEFAULT 100,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_project_team_assignment_start (project_id, team_id, valid_from),
  KEY idx_project_team_assignment_lookup (team_id, valid_from, valid_to, status),
  CONSTRAINT fk_project_team_assignment_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_project_team_assignment_team FOREIGN KEY (team_id) REFERENCES md_team(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rel_project_rig_assignment (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  project_id BIGINT UNSIGNED NOT NULL,
  rig_id BIGINT UNSIGNED NOT NULL,
  valid_from DATETIME NOT NULL,
  valid_to DATETIME NULL,
  service_discipline VARCHAR(32) NOT NULL DEFAULT '',
  assignment_note VARCHAR(512) NOT NULL DEFAULT '',
  priority INT NOT NULL DEFAULT 100,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_project_rig_assignment_start (project_id, rig_id, valid_from),
  KEY idx_project_rig_assignment_lookup (rig_id, valid_from, valid_to, status),
  CONSTRAINT fk_project_rig_assignment_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_project_rig_assignment_rig FOREIGN KEY (rig_id) REFERENCES md_rig(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rel_project_well_scope (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  project_id BIGINT UNSIGNED NOT NULL,
  wellbore_id BIGINT UNSIGNED NOT NULL,
  job_type VARCHAR(32) NOT NULL DEFAULT '',
  scope_note VARCHAR(512) NOT NULL DEFAULT '',
  valid_from DATETIME NOT NULL,
  valid_to DATETIME NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_project_well_scope_start (project_id, wellbore_id, job_type, valid_from),
  KEY idx_project_well_scope_lookup (wellbore_id, job_type, valid_from, valid_to, status),
  CONSTRAINT fk_project_well_scope_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_project_well_scope_wellbore FOREIGN KEY (wellbore_id) REFERENCES md_wellbore(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS biz_job (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  job_code VARCHAR(191) NOT NULL,
  project_id BIGINT UNSIGNED NULL,
  wellbore_id BIGINT UNSIGNED NOT NULL,
  job_type VARCHAR(32) NOT NULL,
  sequence_no INT UNSIGNED NOT NULL DEFAULT 1,
  planned_start DATETIME NULL,
  planned_end DATETIME NULL,
  planned_depth_ft DECIMAL(14,3) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'planned',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_biz_job_code (job_code),
  UNIQUE KEY uq_biz_job_sequence (project_id, wellbore_id, job_type, sequence_no),
  KEY idx_biz_job_wellbore (wellbore_id, job_type, status),
  CONSTRAINT fk_biz_job_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_biz_job_wellbore FOREIGN KEY (wellbore_id) REFERENCES md_wellbore(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rel_job_rig_assignment (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  job_id BIGINT UNSIGNED NOT NULL,
  rig_id BIGINT UNSIGNED NOT NULL,
  valid_from DATETIME NOT NULL,
  valid_to DATETIME NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_job_rig_assignment_start (job_id, rig_id, valid_from),
  KEY idx_job_rig_assignment_lookup (rig_id, valid_from, valid_to, status),
  CONSTRAINT fk_job_rig_assignment_job FOREIGN KEY (job_id) REFERENCES biz_job(id),
  CONSTRAINT fk_job_rig_assignment_rig FOREIGN KEY (rig_id) REFERENCES md_rig(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_daily_report (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_id VARCHAR(191) NOT NULL,
  report_date DATE NULL,
  report_type VARCHAR(32) NOT NULL,
  project_id BIGINT UNSIGNED NULL,
  job_id BIGINT UNSIGNED NULL,
  rig_id BIGINT UNSIGNED NULL,
  wellbore_id BIGINT UNSIGNED NULL,
  match_status VARCHAR(32) NOT NULL DEFAULT 'UNASSIGNED',
  match_message TEXT NULL,
  normalization_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
  source_version VARCHAR(64) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_fact_daily_report_record (record_id),
  KEY idx_fact_daily_report_date (report_date, report_type),
  KEY idx_fact_daily_report_match (match_status, normalization_status),
  KEY idx_fact_daily_report_refs (project_id, job_id, rig_id, wellbore_id),
  CONSTRAINT fk_fact_daily_report_record FOREIGN KEY (record_id) REFERENCES report_records(record_id) ON DELETE CASCADE,
  CONSTRAINT fk_fact_daily_report_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_fact_daily_report_job FOREIGN KEY (job_id) REFERENCES biz_job(id),
  CONSTRAINT fk_fact_daily_report_rig FOREIGN KEY (rig_id) REFERENCES md_rig(id),
  CONSTRAINT fk_fact_daily_report_wellbore FOREIGN KEY (wellbore_id) REFERENCES md_wellbore(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_activity (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  daily_report_id BIGINT UNSIGNED NOT NULL,
  source_row_no INT NOT NULL,
  started_at DATETIME NULL,
  ended_at DATETIME NULL,
  hours DECIMAL(10,3) NOT NULL DEFAULT 0,
  op_code VARCHAR(64) NOT NULL DEFAULT '',
  op_sub VARCHAR(128) NOT NULL DEFAULT '',
  source_op_type VARCHAR(16) NOT NULL DEFAULT '',
  operation_details TEXT NULL,
  source_hash VARCHAR(64) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_fact_activity_row (daily_report_id, source_row_no),
  KEY idx_fact_activity_code (op_code, op_sub),
  CONSTRAINT fk_fact_activity_report FOREIGN KEY (daily_report_id) REFERENCES fact_daily_report(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS time_classification_rule (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  rule_code VARCHAR(80) NOT NULL,
  rule_name VARCHAR(255) NOT NULL,
  priority INT NOT NULL DEFAULT 100,
  op_code_pattern VARCHAR(255) NOT NULL DEFAULT '',
  op_sub_pattern VARCHAR(255) NOT NULL DEFAULT '',
  keyword_pattern VARCHAR(1000) NOT NULL DEFAULT '',
  classification_json JSON NOT NULL,
  rule_version VARCHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_time_classification_rule_code (rule_code),
  KEY idx_time_classification_rule_priority (status, priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_time_classification (
  activity_id BIGINT UNSIGNED NOT NULL,
  productive_flag VARCHAR(32) NOT NULL DEFAULT '',
  confirmed_op_type VARCHAR(16) NOT NULL DEFAULT '',
  work_bucket VARCHAR(64) NOT NULL DEFAULT '',
  billing_status VARCHAR(32) NOT NULL DEFAULT '',
  responsibility VARCHAR(32) NOT NULL DEFAULT '',
  cause_code VARCHAR(64) NOT NULL DEFAULT '',
  service_line VARCHAR(128) NOT NULL DEFAULT '',
  rule_id BIGINT UNSIGNED NULL,
  rule_version VARCHAR(64) NOT NULL DEFAULT '',
  confirmation_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
  confidence DECIMAL(5,4) NULL,
  confirmed_at DATETIME NULL,
  confirmed_by VARCHAR(128) NOT NULL DEFAULT '',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (activity_id),
  KEY idx_fact_time_classification_queue (confirmation_status, rule_version),
  CONSTRAINT fk_fact_time_classification_activity FOREIGN KEY (activity_id) REFERENCES fact_activity(id) ON DELETE CASCADE,
  CONSTRAINT fk_fact_time_classification_rule FOREIGN KEY (rule_id) REFERENCES time_classification_rule(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS time_classification_revision (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  activity_id BIGINT UNSIGNED NOT NULL,
  previous_json JSON NULL,
  revised_json JSON NOT NULL,
  revision_type VARCHAR(32) NOT NULL DEFAULT 'manual',
  reason VARCHAR(512) NOT NULL DEFAULT '',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  KEY idx_time_classification_revision_activity (activity_id, created_at),
  CONSTRAINT fk_time_classification_revision_activity FOREIGN KEY (activity_id) REFERENCES fact_activity(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_job_event (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  job_id BIGINT UNSIGNED NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  occurred_at DATETIME NOT NULL,
  source_record_id VARCHAR(191) NULL,
  source_type VARCHAR(32) NOT NULL DEFAULT 'report',
  confirmation_status VARCHAR(32) NOT NULL DEFAULT 'AUTO',
  note TEXT NULL,
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_fact_job_event_source (job_id, event_type, occurred_at, source_record_id),
  KEY idx_fact_job_event_lookup (job_id, event_type, occurred_at),
  CONSTRAINT fk_fact_job_event_job FOREIGN KEY (job_id) REFERENCES biz_job(id),
  CONSTRAINT fk_fact_job_event_record FOREIGN KEY (source_record_id) REFERENCES report_records(record_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_depth_progress (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  job_id BIGINT UNSIGNED NOT NULL,
  record_id VARCHAR(191) NOT NULL,
  progress_date DATE NOT NULL,
  measured_depth_ft DECIMAL(14,3) NULL,
  daily_progress_ft DECIMAL(14,3) NULL,
  source_field VARCHAR(64) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_fact_depth_progress_record (job_id, record_id, progress_date),
  KEY idx_fact_depth_progress_date (job_id, progress_date),
  CONSTRAINT fk_fact_depth_progress_job FOREIGN KEY (job_id) REFERENCES biz_job(id),
  CONSTRAINT fk_fact_depth_progress_record FOREIGN KEY (record_id) REFERENCES report_records(record_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_incident (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  job_id BIGINT UNSIGNED NULL,
  record_id VARCHAR(191) NOT NULL,
  incident_type VARCHAR(64) NOT NULL,
  occurred_at DATETIME NULL,
  description TEXT NULL,
  responsibility VARCHAR(32) NOT NULL DEFAULT '',
  confirmation_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  KEY idx_fact_incident_record (record_id, incident_type),
  KEY idx_fact_incident_job (job_id, occurred_at),
  CONSTRAINT fk_fact_incident_job FOREIGN KEY (job_id) REFERENCES biz_job(id),
  CONSTRAINT fk_fact_incident_record FOREIGN KEY (record_id) REFERENCES report_records(record_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS data_quality_issue (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  issue_key VARCHAR(255) NOT NULL,
  issue_type VARCHAR(64) NOT NULL,
  severity VARCHAR(16) NOT NULL DEFAULT 'warning',
  entity_type VARCHAR(32) NOT NULL DEFAULT '',
  entity_id VARCHAR(191) NOT NULL DEFAULT '',
  record_id VARCHAR(191) NULL,
  details_json JSON NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
  resolution_note VARCHAR(1000) NOT NULL DEFAULT '',
  resolved_at DATETIME NULL,
  resolved_by VARCHAR(128) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_data_quality_issue_key (issue_key),
  KEY idx_data_quality_issue_queue (status, issue_type, severity),
  KEY idx_data_quality_issue_record (record_id),
  CONSTRAINT fk_data_quality_issue_record FOREIGN KEY (record_id) REFERENCES report_records(record_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS monthly_report_snapshot (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  snapshot_code VARCHAR(191) NOT NULL,
  report_type VARCHAR(64) NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  project_id BIGINT UNSIGNED NULL,
  rule_version VARCHAR(64) NOT NULL DEFAULT '',
  source_cutoff_at DATETIME NOT NULL,
  snapshot_status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
  snapshot_version INT UNSIGNED NOT NULL DEFAULT 1,
  supersedes_id BIGINT UNSIGNED NULL,
  frozen_at DATETIME NULL,
  frozen_by VARCHAR(128) NOT NULL DEFAULT '',
  reopened_at DATETIME NULL,
  reopened_by VARCHAR(128) NOT NULL DEFAULT '',
  change_reason VARCHAR(512) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_monthly_report_snapshot_code (snapshot_code),
  UNIQUE KEY uq_monthly_report_snapshot_version (report_type, period_start, period_end, project_id, snapshot_version),
  KEY idx_monthly_report_snapshot_lookup (report_type, period_start, snapshot_status),
  CONSTRAINT fk_monthly_report_snapshot_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_monthly_report_snapshot_previous FOREIGN KEY (supersedes_id) REFERENCES monthly_report_snapshot(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS monthly_report_snapshot_row (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  snapshot_id BIGINT UNSIGNED NOT NULL,
  row_no INT NOT NULL,
  row_key VARCHAR(255) NOT NULL,
  row_json JSON NOT NULL,
  lineage_json JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_monthly_report_snapshot_row (snapshot_id, row_no),
  KEY idx_monthly_report_snapshot_row_key (snapshot_id, row_key),
  CONSTRAINT fk_monthly_report_snapshot_row_header FOREIGN KEY (snapshot_id) REFERENCES monthly_report_snapshot(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS migration_batch (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  batch_code VARCHAR(128) NOT NULL,
  source_type VARCHAR(32) NOT NULL,
  source_path VARCHAR(1024) NOT NULL DEFAULT '',
  batch_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
  summary_json JSON NULL,
  started_at DATETIME NULL,
  completed_at DATETIME NULL,
  rolled_back_at DATETIME NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_migration_batch_code (batch_code),
  KEY idx_migration_batch_status (batch_status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS migration_entry (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  batch_id BIGINT UNSIGNED NOT NULL,
  source_locator VARCHAR(1024) NOT NULL,
  source_locator_hash CHAR(64) NOT NULL,
  entity_type VARCHAR(32) NOT NULL,
  entity_id VARCHAR(191) NOT NULL DEFAULT '',
  old_value_json JSON NULL,
  new_value_json JSON NULL,
  entry_status VARCHAR(32) NOT NULL DEFAULT 'APPLIED',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_migration_entry_source (batch_id, source_locator_hash, entity_type),
  KEY idx_migration_entry_entity (entity_type, entity_id),
  CONSTRAINT fk_migration_entry_batch FOREIGN KEY (batch_id) REFERENCES migration_batch(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE OR REPLACE VIEW vw_rig_production_timeline AS
SELECT
  fdr.record_id,
  fdr.report_date,
  fdr.report_type,
  fdr.project_id,
  project.project_name,
  fdr.job_id,
  fdr.rig_id,
  rig.rig_name,
  model.model_name AS rig_model,
  fdr.wellbore_id,
  wellbore.wellbore_name,
  activity.id AS activity_id,
  activity.source_row_no,
  activity.hours,
  classification.productive_flag,
  classification.confirmed_op_type,
  classification.work_bucket,
  classification.billing_status,
  classification.responsibility,
  classification.cause_code,
  classification.service_line,
  classification.confirmation_status
FROM fact_daily_report fdr
JOIN fact_activity activity ON activity.daily_report_id = fdr.id
LEFT JOIN fact_time_classification classification ON classification.activity_id = activity.id
LEFT JOIN md_project project ON project.id = fdr.project_id
LEFT JOIN md_rig rig ON rig.id = fdr.rig_id
LEFT JOIN md_rig_model model ON model.id = rig.rig_model_id
LEFT JOIN md_wellbore wellbore ON wellbore.id = fdr.wellbore_id
WHERE fdr.normalization_status = 'NORMALIZED' AND fdr.match_status = 'MATCHED';

CREATE OR REPLACE VIEW vw_monthly_rig_workload AS
SELECT
  DATE_FORMAT(report_date, '%Y-%m-01') AS month_start,
  project_id,
  project_name,
  rig_id,
  rig_name,
  rig_model,
  work_bucket,
  ROUND(SUM(hours), 3) AS hours,
  COUNT(DISTINCT record_id) AS report_count
FROM vw_rig_production_timeline
GROUP BY DATE_FORMAT(report_date, '%Y-%m-01'), project_id, project_name, rig_id, rig_name, rig_model, work_bucket;

CREATE OR REPLACE VIEW vw_drilling_basic_metrics AS
SELECT
  job.id AS job_id,
  job.job_code,
  job.job_type,
  job.project_id,
  project.project_name,
  job.wellbore_id,
  wellbore.wellbore_name,
  MIN(report.rig_id) AS rig_id,
  MIN(rig.rig_name) AS rig_name,
  COALESCE(job.planned_depth_ft, 0) AS planned_depth,
  MIN(report.report_date) AS start_date,
  MAX(report.report_date) AS end_date,
  DATEDIFF(MAX(report.report_date), MIN(report.report_date)) + 1 AS calendar_days,
  COALESCE(MAX(depth.measured_depth_ft), 0) AS latest_depth,
  COALESCE(SUM(depth.daily_progress_ft), 0) AS period_progress,
  COALESCE(SUM(depth.daily_progress_ft), 0) AS year_progress,
  GROUP_CONCAT(DISTINCT report.record_id ORDER BY report.record_id) AS source_ids
FROM biz_job job
JOIN md_project project ON project.id = job.project_id
JOIN md_wellbore wellbore ON wellbore.id = job.wellbore_id
JOIN fact_daily_report report ON report.job_id = job.id AND report.match_status = 'MATCHED'
LEFT JOIN md_rig rig ON rig.id = report.rig_id
LEFT JOIN fact_depth_progress depth ON depth.job_id = job.id AND depth.record_id = report.record_id
WHERE job.job_type = 'drilling'
GROUP BY job.id, job.job_code, job.job_type, job.project_id, project.project_name,
         job.wellbore_id, wellbore.wellbore_name, job.planned_depth_ft;

CREATE OR REPLACE VIEW vw_job_efficiency AS
SELECT
  job.id AS job_id,
  job.job_code,
  job.job_type,
  job.project_id,
  project.project_name,
  job.wellbore_id,
  wellbore.wellbore_name,
  MIN(report.rig_id) AS rig_id,
  MIN(rig.rig_name) AS rig_name,
  MIN(report.report_date) AS period_start,
  MAX(report.report_date) AS period_end,
  ROUND(SUM(CASE WHEN classification.productive_flag = 'PRODUCTION' THEN activity.hours ELSE 0 END), 3) AS productive_hours,
  ROUND(SUM(CASE WHEN classification.productive_flag <> 'PRODUCTION'
                  AND classification.confirmed_op_type <> 'SC' THEN activity.hours ELSE 0 END), 3) AS included_nonproductive_hours,
  ROUND(SUM(CASE WHEN classification.confirmed_op_type = 'SC' THEN activity.hours ELSE 0 END), 3) AS excluded_hours,
  ROUND(SUM(activity.hours), 3) AS total_hours,
  CASE WHEN SUM(CASE WHEN classification.confirmed_op_type <> 'SC' THEN activity.hours ELSE 0 END) = 0 THEN 0
       ELSE ROUND(SUM(CASE WHEN classification.productive_flag = 'PRODUCTION' THEN activity.hours ELSE 0 END)
                  / SUM(CASE WHEN classification.confirmed_op_type <> 'SC' THEN activity.hours ELSE 0 END), 6) END AS efficiency,
  SUM(CASE WHEN classification.confirmation_status IN ('CONFIRMED','AUTO_CONFIRMED') THEN 1 ELSE 0 END) AS confirmed_rows,
  SUM(CASE WHEN classification.confirmation_status NOT IN ('CONFIRMED','AUTO_CONFIRMED')
            OR classification.confirmation_status IS NULL THEN 1 ELSE 0 END) AS pending_rows,
  GROUP_CONCAT(DISTINCT report.record_id ORDER BY report.record_id) AS source_ids
FROM biz_job job
JOIN md_project project ON project.id = job.project_id
JOIN md_wellbore wellbore ON wellbore.id = job.wellbore_id
JOIN fact_daily_report report ON report.job_id = job.id AND report.match_status = 'MATCHED'
LEFT JOIN md_rig rig ON rig.id = report.rig_id
JOIN fact_activity activity ON activity.daily_report_id = report.id
LEFT JOIN fact_time_classification classification ON classification.activity_id = activity.id
GROUP BY job.id, job.job_code, job.job_type, job.project_id, project.project_name,
         job.wellbore_id, wellbore.wellbore_name;

CREATE OR REPLACE VIEW vw_workover_basic_metrics AS
SELECT
  job_id,
  job_code,
  job_type,
  project_id,
  project_name,
  wellbore_id,
  wellbore_name,
  rig_id,
  rig_name,
  period_start AS start_date,
  period_end AS end_date,
  DATEDIFF(period_end, period_start) + 1 AS calendar_days,
  productive_hours,
  included_nonproductive_hours,
  efficiency,
  confirmed_rows,
  pending_rows,
  source_ids
FROM vw_job_efficiency
WHERE job_type IN ('workover', 'completion');
