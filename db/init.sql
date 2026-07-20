CREATE DATABASE IF NOT EXISTS drilling_report_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE drilling_report_db;

CREATE TABLE IF NOT EXISTS dpr_report_record (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_id VARCHAR(191) NOT NULL COMMENT '稳定日报业务ID',
  report_type VARCHAR(32) NOT NULL COMMENT '日报类型：drilling/completion/workover/move',
  source_file VARCHAR(512) NOT NULL DEFAULT '',
  parser VARCHAR(128) NOT NULL DEFAULT '',
  source_page_start INT UNSIGNED NULL COMMENT '合并PDF内的起始页码，从1开始',
  source_page_end INT UNSIGNED NULL COMMENT '合并PDF内的结束页码，从1开始',
  source_report_index INT UNSIGNED NULL COMMENT '合并PDF内日报序号，从1开始',
  source_report_count INT UNSIGNED NULL COMMENT '合并PDF内识别出的日报总数',
  batch_inherited_fields VARCHAR(255) NOT NULL DEFAULT '' COMMENT '批内一致性继承的字段，逗号分隔',
  report_date VARCHAR(32) NOT NULL DEFAULT '',
  report_no VARCHAR(64) NOT NULL DEFAULT '',
  wellbore VARCHAR(128) NOT NULL DEFAULT '',
  rig VARCHAR(128) NOT NULL DEFAULT '',
  rig_id BIGINT UNSIGNED NULL,
  well_id BIGINT UNSIGNED NULL,
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
  UNIQUE KEY uq_report_records_business_identity (report_type, report_date, report_no, wellbore),
  KEY idx_report_records_type_date (report_type, report_date),
  KEY idx_report_records_well_date (wellbore, report_date),
  KEY idx_report_records_type_well_date (report_type, well_id, report_date),
  KEY idx_report_records_rig (rig),
  KEY idx_report_records_master_refs (project_id, rig_id, well_id, job_id),
  KEY idx_report_records_match_status (master_match_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日报原始审计主表；保存来源、业务标识、处理状态及主数据引用';

CREATE TABLE IF NOT EXISTS dpr_report_field (
  record_id VARCHAR(191) NOT NULL,
  fields_json JSON NOT NULL COMMENT '日报全部单值字段原始解析JSON',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (record_id),
  CONSTRAINT fk_report_fields_record
    FOREIGN KEY (record_id) REFERENCES dpr_report_record(record_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日报单值字段原始审计表；fields_json永久保留解析结果';

CREATE TABLE IF NOT EXISTS dpr_report_row (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_id VARCHAR(191) NOT NULL,
  module_name VARCHAR(64) NOT NULL COMMENT '明细模块标准代码',
  row_no INT NOT NULL COMMENT '来源模块内行号，从1开始',
  row_json JSON NOT NULL COMMENT '日报明细行原始解析JSON',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_report_rows_record_module_row (record_id, module_name, row_no),
  KEY idx_report_rows_module (module_name),
  CONSTRAINT fk_report_rows_record
    FOREIGN KEY (record_id) REFERENCES dpr_report_record(record_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日报重复明细原始审计表；按module_name和row_no保存来源行';

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
    FOREIGN KEY (record_id) REFERENCES dpr_report_record(record_id)
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

CREATE TABLE IF NOT EXISTS translation_revision (
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
    FOREIGN KEY (record_id) REFERENCES dpr_report_record(record_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ai_extraction_result (
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
  CONSTRAINT fk_ai_extraction_record FOREIGN KEY (record_id) REFERENCES dpr_report_record(record_id) ON DELETE CASCADE
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
  well_profile_code VARCHAR(64) NOT NULL DEFAULT '',
  trajectory_status_code VARCHAR(64) NOT NULL DEFAULT 'PLANNED',
  kickoff_md_m DECIMAL(12,2) NULL,
  planned_td_md_m DECIMAL(12,2) NULL,
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
  CONSTRAINT fk_md_well_operator FOREIGN KEY (operator_company_id) REFERENCES md_organization(id),
  CONSTRAINT ck_md_well_coordinates CHECK (
    (surface_latitude IS NULL OR (surface_latitude >= -90 AND surface_latitude <= 90)) AND
    (surface_longitude IS NULL OR (surface_longitude >= -180 AND surface_longitude <= 180))
  )
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
  CONSTRAINT fk_project_team_assignment_team FOREIGN KEY (team_id) REFERENCES md_team(id),
  CONSTRAINT ck_rel_project_team_period CHECK (valid_to IS NULL OR valid_to > valid_from)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rel_project_well_scope (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  project_id BIGINT UNSIGNED NOT NULL,
  well_id BIGINT UNSIGNED NOT NULL,
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
  UNIQUE KEY uq_project_well_scope_start (project_id, well_id, job_type, valid_from),
  KEY idx_project_well_scope_lookup (well_id, job_type, valid_from, valid_to, status),
  CONSTRAINT fk_project_well_scope_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_project_well_scope_well FOREIGN KEY (well_id) REFERENCES md_well(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS biz_job (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  job_code VARCHAR(191) NOT NULL,
  project_id BIGINT UNSIGNED NULL,
  well_id BIGINT UNSIGNED NOT NULL,
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
  UNIQUE KEY uq_biz_job_sequence (project_id, well_id, job_type, sequence_no),
  KEY idx_biz_job_well (well_id, job_type, status),
  CONSTRAINT fk_biz_job_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_biz_job_well FOREIGN KEY (well_id) REFERENCES md_well(id)
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
  CONSTRAINT fk_job_rig_assignment_rig FOREIGN KEY (rig_id) REFERENCES md_rig(id),
  CONSTRAINT ck_rel_job_rig_period CHECK (valid_to IS NULL OR valid_to > valid_from)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dpr_report (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  record_id VARCHAR(191) NOT NULL,
  report_date DATE NULL,
  report_no INT UNSIGNED NULL COMMENT '日报序号；原始文本保留在dpr_report_record.report_no',
  report_type VARCHAR(32) NOT NULL,
  project_id BIGINT UNSIGNED NULL,
  job_id BIGINT UNSIGNED NULL,
  rig_id BIGINT UNSIGNED NULL,
  well_id BIGINT UNSIGNED NULL,
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
  KEY idx_fact_daily_report_refs (project_id, job_id, rig_id, well_id),
  CONSTRAINT fk_fact_daily_report_record FOREIGN KEY (record_id) REFERENCES dpr_report_record(record_id) ON DELETE CASCADE,
  CONSTRAINT fk_fact_daily_report_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_fact_daily_report_job FOREIGN KEY (job_id) REFERENCES biz_job(id),
  CONSTRAINT fk_fact_daily_report_rig FOREIGN KEY (rig_id) REFERENCES md_rig(id),
  CONSTRAINT fk_fact_daily_report_well FOREIGN KEY (well_id) REFERENCES md_well(id),
  CONSTRAINT ck_fact_daily_report_type CHECK (report_type IN ('drilling','completion','workover','move'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dpr_operation (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  daily_report_id BIGINT UNSIGNED NOT NULL,
  source_row_no INT NOT NULL,
  source_from_text VARCHAR(16) NOT NULL DEFAULT '' COMMENT '来源表格FROM原文',
  source_to_text VARCHAR(16) NOT NULL DEFAULT '' COMMENT '来源表格TO原文',
  started_at DATETIME NULL,
  ended_at DATETIME NULL,
  hours DECIMAL(6,3) NULL COMMENT '统计作业时长，单位h；优先来源申报，缺失时可由钟表时间推导',
  hours_source VARCHAR(16) NOT NULL DEFAULT 'DECLARED' COMMENT 'DECLARED/CLOCK_DERIVED',
  clock_hours DECIMAL(6,3) NULL COMMENT '由起止时间计算的钟表时长，单位h',
  duration_variance_hours DECIMAL(7,3) NULL COMMENT '申报时长减钟表时长，单位h',
  cross_midnight_flag BOOLEAN NOT NULL DEFAULT FALSE COMMENT '结束时间是否跨至次日',
  time_validation_status VARCHAR(32) NOT NULL DEFAULT 'MISSING_TIME' COMMENT 'VALID/DURATION_MISMATCH/MISSING_TIME/INVALID_TIME/MISSING_HOURS',
  op_code VARCHAR(64) NOT NULL DEFAULT '',
  op_sub VARCHAR(128) NOT NULL DEFAULT '',
  work_category_code VARCHAR(80) NOT NULL DEFAULT 'UNSPECIFIED' COMMENT '标准化一级工作分类代码',
  work_subcategory_code VARCHAR(160) NOT NULL DEFAULT 'UNSPECIFIED' COMMENT '标准化二级工作分类代码',
  source_op_type VARCHAR(16) NOT NULL DEFAULT '',
  operation_details TEXT NULL COMMENT '来源工作内容描述原文，非JSON',
  operation_details_normalized TEXT NULL COMMENT '规范化空白后的工作内容描述',
  description_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '规范化工作描述SHA-256',
  source_hash VARCHAR(64) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_fact_activity_row (daily_report_id, source_row_no),
  KEY idx_fact_activity_code (op_code, op_sub),
  KEY idx_fact_activity_work_category (work_category_code, work_subcategory_code),
  KEY idx_fact_activity_time_type (source_op_type, time_validation_status),
  KEY idx_fact_activity_timeline (started_at, ended_at),
  CONSTRAINT fk_fact_activity_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_fact_activity_hours CHECK (hours IS NULL OR (hours >= 0 AND hours <= 24)),
  CONSTRAINT ck_fact_activity_hours_source CHECK (hours_source IN ('DECLARED','CLOCK_DERIVED')),
  CONSTRAINT ck_fact_activity_timeline CHECK (started_at IS NULL OR ended_at IS NULL OR ended_at > started_at),
  CONSTRAINT ck_fact_activity_source_type CHECK (source_op_type IN ('','P','SC','NPT')),
  CONSTRAINT ck_fact_activity_time_status CHECK (time_validation_status IN ('VALID','DURATION_MISMATCH','MISSING_TIME','INVALID_TIME','MISSING_HOURS'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dpr_operation_classification_rule (
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

CREATE TABLE IF NOT EXISTS dpr_operation_classification (
  activity_id BIGINT UNSIGNED NOT NULL,
  productive_flag VARCHAR(32) NOT NULL DEFAULT '',
  productivity_type_code VARCHAR(32) NOT NULL DEFAULT '' COMMENT '生产属性类别代码；替代名称易误解的productive_flag',
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
  CONSTRAINT fk_fact_time_classification_activity FOREIGN KEY (activity_id) REFERENCES dpr_operation(id) ON DELETE CASCADE,
  CONSTRAINT fk_fact_time_classification_rule FOREIGN KEY (rule_id) REFERENCES dpr_operation_classification_rule(id),
  CONSTRAINT ck_fact_time_classification_confidence CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dpr_operation_classification_revision (
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
  CONSTRAINT fk_time_classification_revision_activity FOREIGN KEY (activity_id) REFERENCES dpr_operation(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS biz_job_event (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  job_id BIGINT UNSIGNED NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  event_date DATE NULL COMMENT '事件日期',
  event_time TIME NULL COMMENT '事件时间；来源未提供时为NULL',
  time_precision_code VARCHAR(16) NOT NULL DEFAULT 'DATE' COMMENT '时间精度：DATE或DATETIME',
  occurred_at DATETIME NULL COMMENT '仅来源明确到具体时间时填写',
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
  UNIQUE KEY uq_fact_job_event_source_date (job_id, event_type, event_date, source_record_id),
  KEY idx_fact_job_event_lookup (job_id, event_type, occurred_at),
  CONSTRAINT fk_fact_job_event_job FOREIGN KEY (job_id) REFERENCES biz_job(id),
  CONSTRAINT fk_fact_job_event_record FOREIGN KEY (source_record_id) REFERENCES dpr_report_record(record_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS biz_job_depth_progress (
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
  CONSTRAINT fk_fact_depth_progress_record FOREIGN KEY (record_id) REFERENCES dpr_report_record(record_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS hsse_incident (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  job_id BIGINT UNSIGNED NULL,
  record_id VARCHAR(191) NOT NULL,
  incident_type VARCHAR(64) NOT NULL,
  incident_date DATE NULL COMMENT '事故日期',
  incident_time TIME NULL COMMENT '事故时间；来源未提供时为NULL',
  time_precision_code VARCHAR(16) NOT NULL DEFAULT 'DATE' COMMENT '时间精度：DATE或DATETIME',
  occurred_at DATETIME NULL COMMENT '仅来源明确到具体时间时填写',
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
  CONSTRAINT fk_fact_incident_record FOREIGN KEY (record_id) REFERENCES dpr_report_record(record_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dpr_report_summary (
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  event_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT '日报事件名称',
  primary_reason VARCHAR(255) NOT NULL DEFAULT '' COMMENT '主要作业原因',
  afe_number VARCHAR(128) NOT NULL DEFAULT '' COMMENT 'AFE编号',
  reference_datum_ft DECIMAL(14,3) NULL COMMENT '参考基准，单位ft',
  current_operation TEXT NULL COMMENT '当前作业描述',
  summary_24h TEXT NULL COMMENT '过去24小时作业总结',
  forecast_24h TEXT NULL COMMENT '未来24小时作业计划',
  other_remarks TEXT NULL COMMENT '其他备注',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源字段内容哈希',
  version INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '乐观锁版本号',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (daily_report_id),
  CONSTRAINT fk_fact_report_summary_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日报公共摘要标准事实';

CREATE TABLE IF NOT EXISTS dpr_drilling_report (
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  measured_depth_ft DECIMAL(14,3) NULL COMMENT '当日测量井深，单位ft',
  previous_measured_depth_ft DECIMAL(14,3) NULL COMMENT '前日测量井深，单位ft',
  daily_progress_ft DECIMAL(14,3) NULL COMMENT '当日进尺，单位ft',
  rotary_hours DECIMAL(10,3) NULL COMMENT '当日旋转时长，单位h',
  previous_casing_description VARCHAR(255) NOT NULL DEFAULT '' COMMENT '上一层套管描述',
  previous_casing_size_in DECIMAL(10,3) NULL COMMENT '上一层套管尺寸，单位in',
  previous_casing_depth_ft DECIMAL(14,3) NULL COMMENT '上一层套管深度，单位ft',
  next_casing_description VARCHAR(255) NOT NULL DEFAULT '' COMMENT '下一层套管描述',
  next_casing_size_in DECIMAL(10,3) NULL COMMENT '下一层套管尺寸，单位in',
  next_casing_depth_ft DECIMAL(14,3) NULL COMMENT '下一层套管深度，单位ft',
  formation_test_type VARCHAR(32) NOT NULL DEFAULT '' COMMENT '地层测试类型，例如FIT或LOT',
  formation_test_emw_ppg DECIMAL(10,3) NULL COMMENT '地层测试等效泥浆密度，单位ppg',
  last_bop_test_date DATE NULL COMMENT '最近一次BOP试压日期',
  pump_rate_gpm DECIMAL(12,3) NULL COMMENT '泵排量，单位gpm',
  pump_pressure_psi DECIMAL(12,3) NULL COMMENT '泵压，单位psi',
  string_weight_up_kip DECIMAL(12,3) NULL COMMENT '钻柱上提重量，单位kip',
  string_weight_down_kip DECIMAL(12,3) NULL COMMENT '钻柱下放重量，单位kip',
  torque_off_bottom_ft_lbf DECIMAL(16,3) NULL COMMENT '离底扭矩，单位ft-lbf',
  torque_on_bottom_ft_lbf DECIMAL(16,3) NULL COMMENT '井底扭矩，单位ft-lbf',
  bit_sequence_no VARCHAR(64) NOT NULL DEFAULT '' COMMENT '钻头序号',
  bit_size_in DECIMAL(10,3) NULL COMMENT '钻头尺寸，单位in',
  bit_manufacturer VARCHAR(255) NOT NULL DEFAULT '' COMMENT '钻头制造商',
  bit_serial_no VARCHAR(128) NOT NULL DEFAULT '' COMMENT '钻头序列号',
  bit_wear_iodl VARCHAR(128) NOT NULL DEFAULT '' COMMENT '钻头磨损I-O-D-L',
  bit_wear_bgor VARCHAR(128) NOT NULL DEFAULT '' COMMENT '钻头磨损B-G-O-R',
  bha_no VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'BHA编号',
  bha_md_in_ft DECIMAL(14,3) NULL COMMENT 'BHA入井测量井深，单位ft',
  bha_md_out_ft DECIMAL(14,3) NULL COMMENT 'BHA出井测量井深，单位ft',
  bha_total_length_ft DECIMAL(14,3) NULL COMMENT 'BHA总长度，单位ft',
  safety_incident_flag VARCHAR(16) NOT NULL DEFAULT '' COMMENT '安全事故标志',
  environmental_incident_flag VARCHAR(16) NOT NULL DEFAULT '' COMMENT '环境事故标志',
  days_since_recordable_incident INT NULL COMMENT '距上次可记录事故天数',
  days_since_lost_time_accident INT NULL COMMENT '距上次损失工时事故天数',
  incident_comments TEXT NULL COMMENT '事故说明',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源字段内容哈希',
  version INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '乐观锁版本号',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (daily_report_id),
  CONSTRAINT fk_fact_drilling_parameter_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='钻井日报施工参数标准事实';

CREATE TABLE IF NOT EXISTS dpr_drilling_fluid_property (
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  mud_engineer VARCHAR(255) NOT NULL DEFAULT '' COMMENT '泥浆工程师',
  sample_source VARCHAR(255) NOT NULL DEFAULT '' COMMENT '泥浆取样位置',
  mud_type VARCHAR(128) NOT NULL DEFAULT '' COMMENT '泥浆体系',
  sample_time TIME NULL COMMENT '泥浆取样时间',
  sample_depth_ft DECIMAL(14,3) NULL COMMENT '泥浆取样深度，单位ft',
  density_ppg DECIMAL(10,3) NULL COMMENT '泥浆密度，单位ppg',
  mud_temperature_f DECIMAL(10,3) NULL COMMENT '泥浆温度，单位华氏度',
  rheology_temperature_f DECIMAL(10,3) NULL COMMENT '流变测试温度，单位华氏度',
  funnel_viscosity_sec_per_qt DECIMAL(10,3) NULL COMMENT '漏斗黏度，单位sec/qt',
  plastic_viscosity_cp DECIMAL(10,3) NULL COMMENT '塑性黏度，单位cP',
  yield_point_lb_per_100ft2 DECIMAL(10,3) NULL COMMENT '动切力，单位lb/100ft2',
  gel_10s_lb_per_100ft2 DECIMAL(10,3) NULL COMMENT '10秒静切力，单位lb/100ft2',
  gel_10m_lb_per_100ft2 DECIMAL(10,3) NULL COMMENT '10分钟静切力，单位lb/100ft2',
  gel_30m_lb_per_100ft2 DECIMAL(10,3) NULL COMMENT '30分钟静切力，单位lb/100ft2',
  api_fluid_loss_ml_30min DECIMAL(10,3) NULL COMMENT 'API失水，单位ml/30min',
  oil_percent DECIMAL(7,3) NULL COMMENT '含油量百分比',
  water_percent DECIMAL(7,3) NULL COMMENT '含水量百分比',
  sand_percent DECIMAL(7,3) NULL COMMENT '含砂量百分比',
  equivalent_circulating_density_ppg DECIMAL(10,3) NULL COMMENT '当量循环密度，单位ppg',
  comments TEXT NULL COMMENT '泥浆备注',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源字段内容哈希',
  version INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '乐观锁版本号',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (daily_report_id),
  CONSTRAINT fk_fact_drilling_fluid_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='钻井液性能标准事实';

CREATE TABLE IF NOT EXISTS dpr_completion_report (
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  description TEXT NULL COMMENT '完井作业说明',
  operation_start_date DATE NULL COMMENT '完井作业开始日期',
  afe_cost_usd DECIMAL(18,2) NULL COMMENT 'AFE成本，单位USD',
  daily_cost_usd DECIMAL(18,2) NULL COMMENT '当日成本，单位USD',
  cumulative_cost_usd DECIMAL(18,2) NULL COMMENT '累计成本，单位USD',
  supervisor_1 VARCHAR(255) NOT NULL DEFAULT '' COMMENT '监督人员1',
  supervisor_2 VARCHAR(255) NOT NULL DEFAULT '' COMMENT '监督人员2',
  engineer VARCHAR(255) NOT NULL DEFAULT '' COMMENT '工程师',
  pam_engineer VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'PAM工程师',
  geologist VARCHAR(255) NOT NULL DEFAULT '' COMMENT '地质师',
  total_personnel INT NULL COMMENT '现场总人数',
  safety_comments TEXT NULL COMMENT '安全备注',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源字段内容哈希',
  version INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '乐观锁版本号',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (daily_report_id),
  CONSTRAINT fk_fact_completion_parameter_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='完井日报扩展参数标准事实';

CREATE TABLE IF NOT EXISTS dpr_workover_report (
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  workover_no VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修井作业编号',
  description TEXT NULL COMMENT '修井作业说明',
  operation_start_date DATE NULL COMMENT '修井作业开始日期',
  afe_cost_usd DECIMAL(18,2) NULL COMMENT 'AFE成本，单位USD',
  daily_cost_usd DECIMAL(18,2) NULL COMMENT '当日成本，单位USD',
  cumulative_cost_usd DECIMAL(18,2) NULL COMMENT '累计成本，单位USD',
  supervisor_1 VARCHAR(255) NOT NULL DEFAULT '' COMMENT '监督人员1',
  supervisor_2 VARCHAR(255) NOT NULL DEFAULT '' COMMENT '监督人员2',
  engineer VARCHAR(255) NOT NULL DEFAULT '' COMMENT '工程师',
  pam_engineer VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'PAM工程师',
  geologist VARCHAR(255) NOT NULL DEFAULT '' COMMENT '地质师',
  total_personnel INT NULL COMMENT '现场总人数',
  safety_comments TEXT NULL COMMENT '安全备注',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源字段内容哈希',
  version INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '乐观锁版本号',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (daily_report_id),
  CONSTRAINT fk_fact_workover_parameter_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='修井日报扩展参数标准事实';

CREATE TABLE IF NOT EXISTS dpr_move_report (
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  ground_elevation_ft DECIMAL(14,3) NULL COMMENT '地面海拔，单位ft',
  afe_design_depth_ft DECIMAL(14,3) NULL COMMENT 'AFE设计井深，单位ft',
  afe_design_days DECIMAL(10,3) NULL COMMENT 'AFE设计周期，单位d',
  rig_move_progress_pct DECIMAL(5,2) NULL COMMENT '搬迁进度，单位%',
  rig_up_progress_pct DECIMAL(5,2) NULL COMMENT '安装进度，单位%',
  loads_moved_today INT UNSIGNED NULL COMMENT '当日搬运载荷数量',
  loads_moved_total INT UNSIGNED NULL COMMENT '累计已搬运载荷数量',
  loads_planned_total INT UNSIGNED NULL COMMENT '计划搬运载荷总数',
  wellbore_prefix VARCHAR(64) NOT NULL DEFAULT '' COMMENT '井号前缀',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源字段内容哈希',
  version INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '乐观锁版本号',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (daily_report_id),
  CONSTRAINT fk_fact_move_parameter_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_fact_move_progress CHECK (rig_move_progress_pct IS NULL OR (rig_move_progress_pct >= 0 AND rig_move_progress_pct <= 100)),
  CONSTRAINT ck_fact_rig_up_progress CHECK (rig_up_progress_pct IS NULL OR (rig_up_progress_pct >= 0 AND rig_up_progress_pct <= 100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='搬迁日报扩展参数标准事实';

CREATE TABLE IF NOT EXISTS dpr_drilling_directional_survey (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '测斜事实ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  measured_depth_ft DECIMAL(14,3) NULL COMMENT '测量井深，单位ft',
  inclination_deg DECIMAL(10,4) NULL COMMENT '井斜角，单位deg',
  azimuth_deg DECIMAL(10,4) NULL COMMENT '方位角，单位deg',
  true_vertical_depth_ft DECIMAL(14,3) NULL COMMENT '垂直井深，单位ft',
  vertical_section_ft DECIMAL(14,3) NULL COMMENT '垂直剖面位移，单位ft',
  north_south_ft DECIMAL(14,3) NULL COMMENT '南北位移，单位ft',
  east_west_ft DECIMAL(14,3) NULL COMMENT '东西位移，单位ft',
  dogleg_severity_deg_per_100ft DECIMAL(10,4) NULL COMMENT '狗腿度，单位deg/100ft',
  build_rate_deg_per_100ft DECIMAL(10,4) NULL COMMENT '造斜率，单位deg/100ft',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_fact_directional_survey_row (daily_report_id, source_row_no),
  KEY idx_fact_directional_survey_depth (daily_report_id, measured_depth_ft),
  CONSTRAINT fk_fact_directional_survey_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_fact_directional_survey_values CHECK (
    (inclination_deg IS NULL OR (inclination_deg >= 0 AND inclination_deg <= 180)) AND
    (azimuth_deg IS NULL OR (azimuth_deg >= 0 AND azimuth_deg < 360)) AND
    (dogleg_severity_deg_per_100ft IS NULL OR dogleg_severity_deg_per_100ft >= 0)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='定向井测斜明细标准事实';

CREATE TABLE IF NOT EXISTS dpr_drilling_bha_component (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'BHA组件事实ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  component_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT '组件名称',
  outside_diameter_in DECIMAL(10,3) NULL COMMENT '外径，单位in',
  inside_diameter_in DECIMAL(10,3) NULL COMMENT '内径，单位in',
  joint_count INT NULL COMMENT '根数',
  component_length_ft DECIMAL(14,3) NULL COMMENT '组件长度，单位ft',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_fact_bha_component_row (daily_report_id, source_row_no),
  CONSTRAINT fk_fact_bha_component_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_fact_bha_component_values CHECK (
    (outside_diameter_in IS NULL OR outside_diameter_in >= 0) AND
    (inside_diameter_in IS NULL OR inside_diameter_in >= 0) AND
    (joint_count IS NULL OR joint_count >= 0) AND
    (component_length_ft IS NULL OR component_length_ft >= 0) AND
    (outside_diameter_in IS NULL OR inside_diameter_in IS NULL OR outside_diameter_in >= inside_diameter_in)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='BHA组件明细标准事实';

CREATE TABLE IF NOT EXISTS dpr_drilling_bulk_inventory (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '材料库存事实ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  material_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT '材料名称',
  opening_quantity DECIMAL(18,3) NULL COMMENT '期初数量',
  received_quantity DECIMAL(18,3) NULL COMMENT '当日接收数量；来源未提供时为NULL',
  used_quantity DECIMAL(18,3) NULL COMMENT '当日使用数量',
  closing_quantity DECIMAL(18,3) NULL COMMENT '期末数量',
  quantity_unit_code VARCHAR(32) NOT NULL DEFAULT 'SOURCE_UNSPECIFIED' COMMENT '数量单位代码；来源未标明时为SOURCE_UNSPECIFIED',
  quantity_balance_status VARCHAR(32) NOT NULL DEFAULT 'NOT_CHECKABLE' COMMENT '数量勾稽状态；缺少接收量或单位时不可校验',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_drilling_bulk_inventory_row (daily_report_id, source_row_no),
  CONSTRAINT fk_drilling_bulk_inventory_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_drilling_bulk_inventory_nonnegative CHECK (
    (opening_quantity IS NULL OR opening_quantity >= 0) AND
    (received_quantity IS NULL OR received_quantity >= 0) AND
    (used_quantity IS NULL OR used_quantity >= 0) AND
    (closing_quantity IS NULL OR closing_quantity >= 0)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='钻井日报散装料库存与消耗';

CREATE TABLE IF NOT EXISTS dpr_completion_bulk_inventory (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '完井散装料库存ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  material_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT '材料名称',
  opening_quantity DECIMAL(18,3) NULL COMMENT '期初数量',
  received_quantity DECIMAL(18,3) NULL COMMENT '当日接收数量；来源未提供时为NULL',
  used_quantity DECIMAL(18,3) NULL COMMENT '当日使用数量',
  closing_quantity DECIMAL(18,3) NULL COMMENT '期末数量',
  quantity_unit_code VARCHAR(32) NOT NULL DEFAULT 'SOURCE_UNSPECIFIED' COMMENT '数量单位代码',
  quantity_balance_status VARCHAR(32) NOT NULL DEFAULT 'NOT_CHECKABLE' COMMENT '数量勾稽状态',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_completion_bulk_inventory_row (daily_report_id, source_row_no),
  CONSTRAINT fk_completion_bulk_inventory_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_completion_bulk_inventory_nonnegative CHECK (
    (opening_quantity IS NULL OR opening_quantity >= 0) AND
    (received_quantity IS NULL OR received_quantity >= 0) AND
    (used_quantity IS NULL OR used_quantity >= 0) AND
    (closing_quantity IS NULL OR closing_quantity >= 0)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='完井日报散装料库存与消耗';

CREATE TABLE IF NOT EXISTS dpr_workover_bulk_inventory (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '修井散装料库存ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  material_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT '材料名称',
  opening_quantity DECIMAL(18,3) NULL COMMENT '期初数量',
  received_quantity DECIMAL(18,3) NULL COMMENT '当日接收数量；来源未提供时为NULL',
  used_quantity DECIMAL(18,3) NULL COMMENT '当日使用数量',
  closing_quantity DECIMAL(18,3) NULL COMMENT '期末数量',
  quantity_unit_code VARCHAR(32) NOT NULL DEFAULT 'SOURCE_UNSPECIFIED' COMMENT '数量单位代码',
  quantity_balance_status VARCHAR(32) NOT NULL DEFAULT 'NOT_CHECKABLE' COMMENT '数量勾稽状态',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_workover_bulk_inventory_row (daily_report_id, source_row_no),
  CONSTRAINT fk_workover_bulk_inventory_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_workover_bulk_inventory_nonnegative CHECK (
    (opening_quantity IS NULL OR opening_quantity >= 0) AND
    (received_quantity IS NULL OR received_quantity >= 0) AND
    (used_quantity IS NULL OR used_quantity >= 0) AND
    (closing_quantity IS NULL OR closing_quantity >= 0)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='修井日报散装料库存与消耗';

CREATE TABLE IF NOT EXISTS dpr_drilling_fluid_loss (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '钻井液漏失事实ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  injected_volume_bbl DECIMAL(14,3) NULL COMMENT '注入体积，单位bbl',
  returned_volume_bbl DECIMAL(14,3) NULL COMMENT '返出体积，单位bbl',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_fact_fluid_loss_row (daily_report_id, source_row_no),
  CONSTRAINT fk_fact_fluid_loss_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_fact_fluid_loss_injected_nonnegative CHECK (injected_volume_bbl IS NULL OR injected_volume_bbl >= 0),
  CONSTRAINT ck_fact_fluid_loss_returned_nonnegative CHECK (returned_volume_bbl IS NULL OR returned_volume_bbl >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='钻井日报漏失情况标准事实';

CREATE TABLE IF NOT EXISTS dpr_completion_mud_product (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '泥浆产品事实ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  product_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT '泥浆产品名称',
  quantity_unit VARCHAR(32) NOT NULL DEFAULT '' COMMENT '数量单位',
  received_quantity DECIMAL(18,3) NULL COMMENT '接收数量',
  used_quantity DECIMAL(18,3) NULL COMMENT '使用数量',
  returned_quantity DECIMAL(18,3) NULL COMMENT '退回数量',
  ending_quantity DECIMAL(18,3) NULL COMMENT '期末数量',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_completion_mud_product_row (daily_report_id, source_row_no),
  CONSTRAINT fk_completion_mud_product_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='完井日报泥浆产品收发存';

CREATE TABLE IF NOT EXISTS dpr_workover_mud_product (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '修井泥浆产品ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  product_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT '泥浆产品名称',
  quantity_unit VARCHAR(32) NOT NULL DEFAULT '' COMMENT '数量单位',
  received_quantity DECIMAL(18,3) NULL COMMENT '接收数量',
  used_quantity DECIMAL(18,3) NULL COMMENT '使用数量',
  returned_quantity DECIMAL(18,3) NULL COMMENT '退回数量',
  ending_quantity DECIMAL(18,3) NULL COMMENT '期末数量',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_workover_mud_product_row (daily_report_id, source_row_no),
  CONSTRAINT fk_workover_mud_product_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='修井日报泥浆产品收发存';

CREATE TABLE IF NOT EXISTS dpr_completion_perforation_interval (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '射孔井段事实ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报事实ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  formation_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT '地层名称',
  top_measured_depth_ft DECIMAL(14,3) NULL COMMENT '射孔顶界测量井深，单位ft',
  base_measured_depth_ft DECIMAL(14,3) NULL COMMENT '射孔底界测量井深，单位ft',
  interval_length_ft DECIMAL(14,3) NULL COMMENT '射孔井段长度，单位ft',
  shot_density_per_ft DECIMAL(10,3) NULL COMMENT '孔密，单位shot/ft',
  charge_description VARCHAR(255) NOT NULL DEFAULT '' COMMENT '射孔弹说明',
  phase_angle_deg DECIMAL(10,3) NULL COMMENT '相位角，单位deg',
  penetration_in DECIMAL(10,3) NULL COMMENT '穿深，单位in',
  hole_diameter_in DECIMAL(10,3) NULL COMMENT '孔径，单位in',
  perforation_date DATE NULL COMMENT '射孔日期',
  interval_status VARCHAR(64) NOT NULL DEFAULT '' COMMENT '井段状态',
  comments TEXT NULL COMMENT '备注',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_completion_perforation_interval_row (daily_report_id, source_row_no),
  KEY idx_completion_perforation_interval_depth (daily_report_id, top_measured_depth_ft, base_measured_depth_ft),
  CONSTRAINT fk_completion_perforation_interval_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_completion_perforation_interval_values CHECK (
    (top_measured_depth_ft IS NULL OR base_measured_depth_ft IS NULL OR base_measured_depth_ft >= top_measured_depth_ft) AND
    (interval_length_ft IS NULL OR interval_length_ft >= 0)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='完井日报射孔井段';

CREATE TABLE IF NOT EXISTS dpr_workover_perforation_interval (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '修井射孔井段ID',
  daily_report_id BIGINT UNSIGNED NOT NULL COMMENT '标准日报ID',
  source_row_no INT NOT NULL COMMENT '来源明细行号',
  formation_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT '地层名称',
  top_measured_depth_ft DECIMAL(14,3) NULL COMMENT '射孔顶界测量井深，单位ft',
  base_measured_depth_ft DECIMAL(14,3) NULL COMMENT '射孔底界测量井深，单位ft',
  interval_length_ft DECIMAL(14,3) NULL COMMENT '射孔井段长度，单位ft',
  shot_density_per_ft DECIMAL(10,3) NULL COMMENT '孔密，单位shot/ft',
  charge_description VARCHAR(255) NOT NULL DEFAULT '' COMMENT '射孔弹说明',
  phase_angle_deg DECIMAL(10,3) NULL COMMENT '相位角，单位deg',
  penetration_in DECIMAL(10,3) NULL COMMENT '穿深，单位in',
  hole_diameter_in DECIMAL(10,3) NULL COMMENT '孔径，单位in',
  perforation_date DATE NULL COMMENT '射孔日期',
  interval_status VARCHAR(64) NOT NULL DEFAULT '' COMMENT '井段状态',
  comments TEXT NULL COMMENT '备注',
  source_hash CHAR(64) NOT NULL DEFAULT '' COMMENT '来源行内容哈希',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  created_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '创建人',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  updated_by VARCHAR(128) NOT NULL DEFAULT '' COMMENT '更新人',
  PRIMARY KEY (id),
  UNIQUE KEY uq_workover_perforation_interval_row (daily_report_id, source_row_no),
  KEY idx_workover_perforation_interval_depth (daily_report_id, top_measured_depth_ft, base_measured_depth_ft),
  CONSTRAINT fk_workover_perforation_interval_report FOREIGN KEY (daily_report_id) REFERENCES dpr_report(id) ON DELETE CASCADE,
  CONSTRAINT ck_workover_perforation_interval_values CHECK (
    (top_measured_depth_ft IS NULL OR base_measured_depth_ft IS NULL OR base_measured_depth_ft >= top_measured_depth_ft) AND
    (interval_length_ft IS NULL OR interval_length_ft >= 0)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='修井日报射孔井段';

CREATE TABLE IF NOT EXISTS dq_issue (
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
  CONSTRAINT fk_data_quality_issue_record FOREIGN KEY (record_id) REFERENCES dpr_report_record(record_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS production_report_remark (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  remark_key VARCHAR(255) NOT NULL,
  project_id BIGINT UNSIGNED NULL,
  rig_id BIGINT UNSIGNED NULL,
  well_id BIGINT UNSIGNED NULL,
  source_rig_name VARCHAR(255) NOT NULL DEFAULT '',
  source_well_name VARCHAR(255) NOT NULL DEFAULT '',
  remark_text VARCHAR(500) NOT NULL DEFAULT '',
  version INT UNSIGNED NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by VARCHAR(128) NOT NULL DEFAULT '',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(128) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_production_report_remark_key (remark_key),
  KEY idx_production_report_remark_scope (project_id, rig_id, well_id),
  CONSTRAINT fk_production_report_remark_project FOREIGN KEY (project_id) REFERENCES md_project(id),
  CONSTRAINT fk_production_report_remark_rig FOREIGN KEY (rig_id) REFERENCES md_rig(id),
  CONSTRAINT fk_production_report_remark_well FOREIGN KEY (well_id) REFERENCES md_well(id)
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

CREATE OR REPLACE VIEW vw_operation_structured AS
SELECT
  fdr.record_id,
  fdr.report_date,
  fdr.report_no,
  fdr.report_type,
  fdr.project_id,
  fdr.job_id,
  fdr.rig_id,
  fdr.well_id,
  fdr.match_status,
  fdr.normalization_status,
  activity.id AS activity_id,
  activity.source_row_no,
  activity.source_from_text,
  activity.source_to_text,
  activity.started_at,
  activity.ended_at,
  activity.cross_midnight_flag,
  activity.hours AS declared_hours,
  activity.hours_source,
  activity.clock_hours,
  activity.duration_variance_hours,
  activity.time_validation_status,
  activity.op_code,
  activity.op_sub,
  activity.work_category_code,
  activity.work_subcategory_code,
  activity.source_op_type,
  COALESCE(NULLIF(classification.confirmed_op_type,''), activity.source_op_type) AS effective_op_type,
  activity.operation_details,
  activity.operation_details_normalized,
  activity.description_hash,
  activity.source_hash,
  classification.productive_flag,
  classification.productivity_type_code,
  classification.confirmed_op_type,
  classification.work_bucket,
  classification.billing_status,
  classification.responsibility,
  classification.cause_code,
  classification.service_line,
  classification.rule_id,
  classification.rule_version,
  classification.confirmation_status,
  classification.confidence,
  CASE
    WHEN activity.time_validation_status <> 'VALID' THEN 'TIME_REVIEW_REQUIRED'
    WHEN COALESCE(classification.confirmation_status,'PENDING') NOT IN ('CONFIRMED','AUTO_CONFIRMED') THEN 'CLASSIFICATION_PENDING'
    ELSE 'READY'
  END AS statistics_status,
  CASE
    WHEN activity.time_validation_status = 'VALID'
     AND COALESCE(classification.confirmation_status,'PENDING') IN ('CONFIRMED','AUTO_CONFIRMED')
    THEN activity.hours
  END AS statistical_hours
FROM dpr_report fdr
JOIN dpr_operation activity ON activity.daily_report_id = fdr.id
LEFT JOIN dpr_operation_classification classification ON classification.activity_id = activity.id;

CREATE OR REPLACE VIEW vw_report_analytics AS
SELECT
  report.record_id,
  report.report_date,
  report.report_no,
  report.report_type,
  report.project_id,
  project.project_code,
  project.project_name,
  contract.contract_no AS project_contract,
  report.job_id,
  report.rig_id,
  COALESCE(rig.rig_name, source.rig) AS rig_name,
  rig_model.model_name AS rig_model,
  report.well_id,
  COALESCE(well.well_name, source.wellbore) AS well_name,
  report.match_status,
  report.match_message,
  report.normalization_status,
  summary.event_name AS event,
  summary.afe_number,
  source.validation_status,
  source.master_match_status,
  source.master_match_message
FROM dpr_report report
JOIN dpr_report_record source ON source.record_id = report.record_id
LEFT JOIN md_project project ON project.id = report.project_id
LEFT JOIN md_contract contract ON contract.id = project.contract_id
LEFT JOIN md_rig rig ON rig.id = report.rig_id
LEFT JOIN md_rig_model rig_model ON rig_model.id = rig.rig_model_id
LEFT JOIN md_well well ON well.id = report.well_id
LEFT JOIN dpr_report_summary summary ON summary.daily_report_id = report.id;

CREATE OR REPLACE VIEW vw_rig_production_timeline AS
SELECT
  operation.record_id,
  operation.report_date,
  operation.report_no,
  operation.report_type,
  operation.project_id,
  report.project_code,
  report.project_name,
  report.project_contract,
  operation.job_id,
  operation.rig_id,
  report.rig_name,
  report.rig_model,
  operation.well_id,
  report.well_name,
  report.event,
  report.afe_number,
  report.validation_status,
  report.master_match_status,
  report.master_match_message,
  operation.activity_id,
  operation.source_row_no,
  operation.source_from_text,
  operation.source_to_text,
  operation.started_at,
  operation.ended_at,
  operation.cross_midnight_flag,
  operation.declared_hours AS hours,
  operation.hours_source,
  operation.clock_hours,
  operation.duration_variance_hours,
  operation.time_validation_status,
  operation.op_code,
  operation.op_sub,
  operation.work_category_code,
  operation.work_subcategory_code,
  operation.source_op_type,
  operation.effective_op_type,
  operation.operation_details,
  operation.operation_details_normalized,
  operation.productive_flag,
  operation.productivity_type_code,
  operation.confirmed_op_type,
  operation.work_bucket,
  operation.billing_status,
  operation.responsibility,
  operation.cause_code,
  operation.service_line,
  operation.rule_id,
  operation.rule_version,
  operation.confirmation_status,
  operation.confidence,
  operation.statistics_status,
  operation.statistical_hours
FROM vw_operation_structured operation
JOIN vw_report_analytics report ON report.record_id = operation.record_id
WHERE operation.normalization_status = 'NORMALIZED' AND operation.match_status = 'MATCHED';

CREATE OR REPLACE VIEW vw_report_record_typed AS
SELECT
  record_id,
  report_type,
  report_date AS source_report_date_text,
  STR_TO_DATE(NULLIF(report_date, ''), '%Y-%m-%d') AS report_date,
  report_no AS source_report_no_text,
  CASE WHEN report_no REGEXP '^[0-9]+$' THEN CAST(report_no AS UNSIGNED) END AS report_no,
  CASE WHEN translation_progress REGEXP '^[0-9]+$' THEN CAST(translation_progress AS UNSIGNED) END AS translation_progress_pct,
  CASE WHEN extraction_progress REGEXP '^[0-9]+$' THEN CAST(extraction_progress AS UNSIGNED) END AS extraction_progress_pct,
  CASE WHEN LOWER(locked) IN ('1','true','yes','y','on') THEN TRUE ELSE FALSE END AS locked_flag,
  CASE WHEN translation_updated_at REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN CAST(translation_updated_at AS DATETIME) END AS translation_updated_at,
  CASE WHEN extraction_updated_at REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN CAST(extraction_updated_at AS DATETIME) END AS extraction_updated_at,
  CASE WHEN confirmed_at REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN CAST(confirmed_at AS DATETIME) END AS confirmed_at,
  CASE WHEN created_at REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN CAST(created_at AS DATETIME) END AS created_at,
  CASE WHEN updated_at REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN CAST(updated_at AS DATETIME) END AS updated_at
FROM dpr_report_record;

CREATE OR REPLACE VIEW vw_monthly_rig_workload AS
SELECT
  CAST(DATE_FORMAT(report_date, '%Y-%m-01') AS DATE) AS month_start,
  project_id,
  project_name,
  rig_id,
  rig_name,
  rig_model,
  work_bucket,
  ROUND(SUM(statistical_hours), 3) AS hours,
  COUNT(DISTINCT record_id) AS report_count
FROM vw_rig_production_timeline
WHERE statistics_status = 'READY'
GROUP BY CAST(DATE_FORMAT(report_date, '%Y-%m-01') AS DATE), project_id, project_name, rig_id, rig_name, rig_model, work_bucket;

CREATE OR REPLACE VIEW vw_drilling_basic_metrics AS
SELECT
  job.id AS job_id,
  job.job_code,
  job.job_type,
  job.project_id,
  project.project_name,
  job.well_id,
  well.well_name,
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
JOIN md_well well ON well.id = job.well_id
JOIN dpr_report report ON report.job_id = job.id AND report.match_status = 'MATCHED'
LEFT JOIN md_rig rig ON rig.id = report.rig_id
LEFT JOIN biz_job_depth_progress depth ON depth.job_id = job.id AND depth.record_id = report.record_id
WHERE job.job_type = 'drilling'
GROUP BY job.id, job.job_code, job.job_type, job.project_id, project.project_name,
         job.well_id, well.well_name, job.planned_depth_ft;

CREATE OR REPLACE VIEW vw_job_efficiency AS
SELECT
  job.id AS job_id,
  job.job_code,
  job.job_type,
  job.project_id,
  project.project_name,
  job.well_id,
  well.well_name,
  MIN(report.rig_id) AS rig_id,
  MIN(rig.rig_name) AS rig_name,
  MIN(report.report_date) AS period_start,
  MAX(report.report_date) AS period_end,
  ROUND(SUM(CASE WHEN activity.time_validation_status = 'VALID'
                  AND classification.productive_flag = 'PRODUCTION'
                  AND classification.confirmation_status IN ('CONFIRMED','AUTO_CONFIRMED') THEN activity.hours ELSE 0 END), 3) AS productive_hours,
  ROUND(SUM(CASE WHEN classification.productive_flag <> 'PRODUCTION'
                  AND classification.confirmed_op_type <> 'SC'
                  AND classification.confirmation_status = 'CONFIRMED'
                  AND activity.time_validation_status = 'VALID' THEN activity.hours ELSE 0 END), 3) AS included_nonproductive_hours,
  ROUND(SUM(CASE WHEN classification.confirmed_op_type = 'SC'
                  AND classification.confirmation_status = 'CONFIRMED'
                  AND activity.time_validation_status = 'VALID' THEN activity.hours ELSE 0 END), 3) AS excluded_hours,
  ROUND(SUM(CASE WHEN activity.time_validation_status <> 'VALID'
                  OR COALESCE(classification.confirmation_status,'PENDING') NOT IN ('CONFIRMED','AUTO_CONFIRMED')
                 THEN activity.hours ELSE 0 END), 3) AS pending_review_hours,
  ROUND(SUM(activity.hours), 3) AS total_hours,
  CASE WHEN SUM(CASE WHEN activity.time_validation_status <> 'VALID'
                       OR COALESCE(classification.confirmation_status,'PENDING') NOT IN ('CONFIRMED','AUTO_CONFIRMED') THEN 1 ELSE 0 END) > 0 THEN NULL
       WHEN SUM(CASE WHEN classification.confirmed_op_type <> 'SC'
                      AND classification.confirmation_status IN ('CONFIRMED','AUTO_CONFIRMED')
                      AND activity.time_validation_status = 'VALID' THEN activity.hours ELSE 0 END) = 0 THEN 0
       ELSE ROUND(SUM(CASE WHEN classification.productive_flag = 'PRODUCTION'
                            AND classification.confirmation_status IN ('CONFIRMED','AUTO_CONFIRMED')
                            AND activity.time_validation_status = 'VALID' THEN activity.hours ELSE 0 END)
                  / SUM(CASE WHEN classification.confirmed_op_type <> 'SC'
                              AND classification.confirmation_status IN ('CONFIRMED','AUTO_CONFIRMED')
                              AND activity.time_validation_status = 'VALID' THEN activity.hours ELSE 0 END), 6) END AS efficiency,
  SUM(CASE WHEN activity.time_validation_status = 'VALID'
            AND classification.confirmation_status IN ('CONFIRMED','AUTO_CONFIRMED') THEN 1 ELSE 0 END) AS confirmed_rows,
  SUM(CASE WHEN activity.time_validation_status <> 'VALID'
            OR COALESCE(classification.confirmation_status,'PENDING') NOT IN ('CONFIRMED','AUTO_CONFIRMED') THEN 1 ELSE 0 END) AS pending_rows,
  CASE WHEN SUM(CASE WHEN activity.time_validation_status <> 'VALID' THEN 1 ELSE 0 END) > 0
       THEN 'PENDING_TIME_REVIEW'
       WHEN SUM(CASE WHEN COALESCE(classification.confirmation_status,'PENDING') NOT IN ('CONFIRMED','AUTO_CONFIRMED') THEN 1 ELSE 0 END) > 0
       THEN 'PENDING_CLASSIFICATION'
       ELSE 'OFFICIAL' END AS official_status,
  GROUP_CONCAT(DISTINCT report.record_id ORDER BY report.record_id) AS source_ids
FROM biz_job job
JOIN md_project project ON project.id = job.project_id
JOIN md_well well ON well.id = job.well_id
JOIN dpr_report report ON report.job_id = job.id AND report.match_status = 'MATCHED'
LEFT JOIN md_rig rig ON rig.id = report.rig_id
JOIN dpr_operation activity ON activity.daily_report_id = report.id
LEFT JOIN dpr_operation_classification classification ON classification.activity_id = activity.id
GROUP BY job.id, job.job_code, job.job_type, job.project_id, project.project_name,
         job.well_id, well.well_name;

CREATE OR REPLACE VIEW vw_workover_basic_metrics AS
SELECT
  job_id,
  job_code,
  job_type,
  project_id,
  project_name,
  well_id,
  well_name,
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
