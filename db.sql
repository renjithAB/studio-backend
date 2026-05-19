-- =====================================================
-- CREATE SEQUENCES STARTING AT 1000 FOR ALL TABLES
-- =====================================================
CREATE SEQUENCE IF NOT EXISTS users_id_seq START WITH 1000;
CREATE SEQUENCE IF NOT EXISTS templates_id_seq START WITH 1000;
CREATE SEQUENCE IF NOT EXISTS projects_id_seq START WITH 1000;
CREATE SEQUENCE IF NOT EXISTS domains_id_seq START WITH 1000;
CREATE SEQUENCE IF NOT EXISTS categories_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS episodes_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS editorials_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS assets_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS variants_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS sequences_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS shots_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS shotsets_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS libraries_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS cycles_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS tasks_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS versions_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS files_id_seq START WITH 100001;
CREATE SEQUENCE IF NOT EXISTS publish_types_id_seq START WITH 100001;

-- =====================================================
-- USERS TABLE (from original schema with all fields)
-- =====================================================
CREATE TABLE users (
    id BIGINT PRIMARY KEY DEFAULT nextval('users_id_seq'),
    is_active BOOLEAN DEFAULT true,
    type VARCHAR(64),
    code VARCHAR(64),
    first_name VARCHAR(32),
    last_name VARCHAR(32),
    email VARCHAR(64) UNIQUE,
    role_id BIGINT,
    permission_id BIGINT,
    is_super BOOLEAN DEFAULT false,
    show_link JSONB,
    private_key VARCHAR(256),
    thumbnail_url VARCHAR(256),
    description TEXT,
    tag VARCHAR(64),
    phone VARCHAR(20),
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    locale VARCHAR(10) NOT NULL DEFAULT 'en_US',
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    preferences JSONB NOT NULL DEFAULT '{}',
    synced_to_superadmin BOOLEAN NOT NULL DEFAULT FALSE,
    superadmin_user_id VARCHAR(36),
    last_synced_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by BIGINT,
    CONSTRAINT fk_users_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_users_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

INSERT INTO users (
    id, is_active, type, code, first_name, last_name, email, 
    role_id, permission_id, is_super, private_key, description
) VALUES (
    1000, true, 'user', 'admin', 'Admin', 'User', 'test@test.com',
    NULL, NULL, true, 
    md5('Password@123'), 
    'System Administrator'
);

-- =====================================================
-- TEMPLATES TABLE (simplified blueprint)
-- =====================================================
CREATE TABLE templates (
    id BIGINT PRIMARY KEY DEFAULT nextval('templates_id_seq'),
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
	has_episode BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_templates_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_templates_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================
-- PROJECTS TABLE
-- =====================================================
CREATE TABLE projects (
    id BIGINT PRIMARY KEY DEFAULT nextval('projects_id_seq'),
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_projects_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_projects_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_projects_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================
-- DOMAINS TABLE
-- =====================================================
CREATE TABLE domains (
    id BIGINT PRIMARY KEY DEFAULT nextval('domains_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(256),
    domain_type VARCHAR(64),
    tag VARCHAR(64),
    project_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_domains_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_domains_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_domains_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_domain_project_code UNIQUE (project_id, code)
);

-- =====================================================
-- CATEGORIES TABLE
-- =====================================================
CREATE TABLE categories (
    id BIGINT PRIMARY KEY DEFAULT nextval('categories_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(256),
    tag VARCHAR(64),
    domain_id BIGINT NOT NULL,
    project_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_categories_domain FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    CONSTRAINT fk_categories_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_categories_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_categories_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_category_project_code UNIQUE (project_id, code)
);

-- =====================================================
-- EPISODES TABLE
-- =====================================================
CREATE TABLE episodes (
    id BIGINT PRIMARY KEY DEFAULT nextval('episodes_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_episodes_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_episodes_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_episodes_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_episodes_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_episode_project_code UNIQUE (project_id, code)
);

-- =====================================================
-- EDITORIALS TABLE
-- =====================================================
CREATE TABLE editorials (
    id BIGINT PRIMARY KEY DEFAULT nextval('editorials_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    episode_id BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_editorials_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_editorials_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_editorials_episode FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE SET NULL,
    CONSTRAINT fk_editorials_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_editorials_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_editorial_project_episode_code UNIQUE (project_id, episode_id, code)
);

-- =====================================================
-- ASSETS TABLE
-- =====================================================
CREATE TABLE assets (
    id BIGINT PRIMARY KEY DEFAULT nextval('assets_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_assets_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_assets_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_assets_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    CONSTRAINT fk_assets_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_assets_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_asset_project_category_code UNIQUE (project_id, category_id, code)
);

-- =====================================================
-- SEQUENCES TABLE
-- =====================================================
CREATE TABLE sequences (
    id BIGINT PRIMARY KEY DEFAULT nextval('sequences_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    episode_id BIGINT,
    frame_start INT,
    frame_end INT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_sequences_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_sequences_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_sequences_episode FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE SET NULL,
    CONSTRAINT fk_sequences_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_sequences_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_sequence_project_episode_code UNIQUE (project_id, episode_id, code)
);

-- =====================================================
-- SHOTS TABLE
-- =====================================================
CREATE TABLE shots (
    id BIGINT PRIMARY KEY DEFAULT nextval('shots_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    episode_id BIGINT,
    sequence_id BIGINT NOT NULL,
    frame_start INT,
    frame_end INT,
    cut_in INT,
    cut_out INT,
    asset_ids JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_shots_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_shots_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_shots_episode FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE SET NULL,
    CONSTRAINT fk_shots_sequence FOREIGN KEY (sequence_id) REFERENCES sequences(id) ON DELETE CASCADE,
    CONSTRAINT fk_shots_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_shots_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_shot_sequence_code UNIQUE (sequence_id, code)
);

-- =====================================================
-- LIBRARIES TABLE
-- =====================================================
CREATE TABLE libraries (
    id BIGINT PRIMARY KEY DEFAULT nextval('libraries_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_libraries_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_libraries_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_libraries_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_libraries_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_library_project_code UNIQUE (project_id, code)
);

-- =====================================================
-- CYCLES TABLE
-- =====================================================
CREATE TABLE cycles (
    id BIGINT PRIMARY KEY DEFAULT nextval('cycles_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    library_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_cycles_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_cycles_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_cycles_library FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE,
    CONSTRAINT fk_cycles_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_cycles_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_cycle_library_code UNIQUE (library_id, code)
);

-- =====================================================
-- TASKS TABLE
-- =====================================================
CREATE TABLE tasks (
    id BIGINT PRIMARY KEY DEFAULT nextval('tasks_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    asset_id BIGINT,
    category_id BIGINT,
    episode_id BIGINT,
    editorial_id BIGINT,
    sequence_id BIGINT,
    shot_id BIGINT,
    library_id BIGINT,
    cycle_id BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_tasks_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_tasks_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_tasks_asset FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    CONSTRAINT fk_tasks_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT fk_tasks_episode FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE,
    CONSTRAINT fk_tasks_editorial FOREIGN KEY (editorial_id) REFERENCES editorials(id) ON DELETE CASCADE,
    CONSTRAINT fk_tasks_sequence FOREIGN KEY (sequence_id) REFERENCES sequences(id) ON DELETE CASCADE,
    CONSTRAINT fk_tasks_shot FOREIGN KEY (shot_id) REFERENCES shots(id) ON DELETE CASCADE,
    CONSTRAINT fk_tasks_library FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE,
    CONSTRAINT fk_tasks_cycle FOREIGN KEY (cycle_id) REFERENCES cycles(id) ON DELETE CASCADE,
    CONSTRAINT fk_tasks_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_tasks_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);


-- =====================================================
-- VARIANTS TABLE
-- =====================================================
CREATE TABLE variants (
    id BIGINT PRIMARY KEY DEFAULT nextval('variants_id_seq'),
    code VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    asset_id BIGINT NOT NULL,
    category_id BIGINT,
	task_id BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_variants_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_variants_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_variants_asset FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    CONSTRAINT fk_variants_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT fk_variants_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_variants_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
	CONSTRAINT fk_variants_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
    CONSTRAINT uq_variant_asset_code UNIQUE (task_id, code)
);

-- =====================================================
-- SHOTSETS TABLE (bridge between shots and assets)
-- =====================================================
CREATE TABLE shotsets (
    id BIGINT PRIMARY KEY DEFAULT nextval('shotsets_id_seq'),
    code VARCHAR(64),
    name VARCHAR(256),
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    tag VARCHAR(64),
    template_id BIGINT,
    project_id BIGINT NOT NULL,
    episode_id BIGINT,
    sequence_id BIGINT,
    shot_id BIGINT NOT NULL,
    asset_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_shotsets_template FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_shotsets_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_shotsets_episode FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE SET NULL,
    CONSTRAINT fk_shotsets_sequence FOREIGN KEY (sequence_id) REFERENCES sequences(id) ON DELETE SET NULL,
    CONSTRAINT fk_shotsets_shot FOREIGN KEY (shot_id) REFERENCES shots(id) ON DELETE CASCADE,
    CONSTRAINT fk_shotsets_asset FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    CONSTRAINT fk_shotsets_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_shotsets_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uq_shotset_shot_asset UNIQUE (shot_id, asset_id)
);







-- =====================================================
-- VERSIONS TABLE
-- =====================================================
CREATE TABLE versions (
    id BIGINT PRIMARY KEY DEFAULT nextval('versions_id_seq'),
    code VARCHAR(64),
    name VARCHAR(256),
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    movie_url VARCHAR(512),
    tag VARCHAR(64),
    project_id BIGINT NOT NULL,
    publish_id BIGINT,
    asset_id BIGINT,
    category_id BIGINT,
    variant_id BIGINT,
    episode_id BIGINT,
    editorial_id BIGINT,
    sequence_id BIGINT,
    shot_id BIGINT,
    library_id BIGINT,
    cycle_id BIGINT,
    task_id BIGINT,
    dependency_id BIGINT,
    upstream_id BIGINT,
    downstream_id BIGINT,
    application VARCHAR(64),
    version_number VARCHAR(64),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_versions_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_versions_publish FOREIGN KEY (publish_id) REFERENCES publish_types(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_asset FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_variant FOREIGN KEY (variant_id) REFERENCES variants(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_episode FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_editorial FOREIGN KEY (editorial_id) REFERENCES editorials(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_sequence FOREIGN KEY (sequence_id) REFERENCES sequences(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_shot FOREIGN KEY (shot_id) REFERENCES shots(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_library FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_cycle FOREIGN KEY (cycle_id) REFERENCES cycles(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_dependency FOREIGN KEY (dependency_id) REFERENCES versions(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_upstream FOREIGN KEY (upstream_id) REFERENCES versions(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_downstream FOREIGN KEY (downstream_id) REFERENCES versions(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_versions_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================
-- FILES TABLE
-- =====================================================
CREATE TABLE files (
    id BIGINT PRIMARY KEY DEFAULT nextval('files_id_seq'),
    code VARCHAR(64),
    name VARCHAR(256),
    description VARCHAR(512),
    thumbnail_url VARCHAR(512),
    movie_url VARCHAR(512),
    file_extension VARCHAR(64),
    file_path TEXT,
    tag VARCHAR(64),
    project_id BIGINT NOT NULL,
    publish_id BIGINT,
    asset_id BIGINT,
    category_id BIGINT,
    variant_id BIGINT,
    episode_id BIGINT,
    editorial_id BIGINT,
    sequence_id BIGINT,
    shot_id BIGINT,
    library_id BIGINT,
    cycle_id BIGINT,
    task_id BIGINT,
    version_id BIGINT,
    dependency_id BIGINT,
    upstream_id BIGINT,
    downstream_id BIGINT,
    application VARCHAR(64),
    version_number VARCHAR(64),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by BIGINT,
    updated_by BIGINT,
    CONSTRAINT fk_files_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_files_publish FOREIGN KEY (publish_id) REFERENCES templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_asset FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_variant FOREIGN KEY (variant_id) REFERENCES variants(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_episode FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_editorial FOREIGN KEY (editorial_id) REFERENCES editorials(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_sequence FOREIGN KEY (sequence_id) REFERENCES sequences(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_shot FOREIGN KEY (shot_id) REFERENCES shots(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_library FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_cycle FOREIGN KEY (cycle_id) REFERENCES cycles(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_version FOREIGN KEY (version_id) REFERENCES versions(id) ON DELETE CASCADE,
    CONSTRAINT fk_files_dependency FOREIGN KEY (dependency_id) REFERENCES files(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_upstream FOREIGN KEY (upstream_id) REFERENCES files(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_downstream FOREIGN KEY (downstream_id) REFERENCES files(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_files_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_templates_code ON templates(code);
CREATE INDEX idx_projects_code ON projects(code);
CREATE INDEX idx_projects_template_id ON projects(template_id);
CREATE INDEX idx_domains_project_id ON domains(project_id);
CREATE INDEX idx_domains_code ON domains(code);
CREATE INDEX idx_categories_domain_id ON categories(domain_id);
CREATE INDEX idx_categories_project_id ON categories(project_id);
CREATE INDEX idx_categories_code ON categories(code);
CREATE INDEX idx_assets_project ON assets(project_id);
CREATE INDEX idx_assets_category ON assets(category_id);
CREATE INDEX idx_shots_sequence ON shots(sequence_id);
CREATE INDEX idx_shots_project ON shots(project_id);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_shot ON tasks(shot_id);
CREATE INDEX idx_tasks_asset ON tasks(asset_id);
CREATE INDEX idx_versions_project ON versions(project_id);
CREATE INDEX idx_versions_task ON versions(task_id);
CREATE INDEX idx_versions_shot ON versions(shot_id);
CREATE INDEX idx_files_version ON files(version_id);
CREATE INDEX idx_files_project ON files(project_id);

-- =====================================================
-- ADD FOREIGN KEY CONSTRAINTS FOR ROLE/PERMISSION IN USERS
-- =====================================================
ALTER TABLE users 
    ADD CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES templates(id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_users_permission FOREIGN KEY (permission_id) REFERENCES templates(id) ON DELETE SET NULL;

	-- Table: public.publish_types

-- DROP TABLE IF EXISTS public.publish_types;

CREATE TABLE IF NOT EXISTS public.publish_types
(
    id bigint NOT NULL DEFAULT nextval('publish_types_id_seq'::regclass),
    project_id bigint,
    name character varying(255) COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone,
    created_by bigint,
    updated_by bigint,
    code character varying(64) COLLATE pg_catalog."default",
    thumbnail_url character varying(1024) COLLATE pg_catalog."default",
    publish_type_code character varying(64) COLLATE pg_catalog."default",
    variant_id bigint,
    task_id bigint,
    CONSTRAINT publish_types_pkey PRIMARY KEY (id),
    CONSTRAINT publish_types_task_id_fkey FOREIGN KEY (task_id)
        REFERENCES public.tasks (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT publish_types_variant_id_fkey FOREIGN KEY (variant_id)
        REFERENCES public.variants (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.publish_types
    OWNER to postgres;




-- ============================================================
-- STEP 1: Create enum types (shared by both tables)
-- ============================================================

CREATE TYPE priority_enum AS ENUM (
    'not_yet_started',
    'work_in_progress',
    'review',
    'approved',
    'client_approved'
);

CREATE TYPE status_enum AS ENUM (
    'below_normal',
    'normal',
    'above_normal',
    'high',
    'critical'
);


-- ============================================================
-- STEP 2: Add columns to VARIANTS table
--         (form-fillable — all nullable, no forced defaults)
-- ============================================================

ALTER TABLE variants
    ADD COLUMN IF NOT EXISTS man_days     NUMERIC(6, 1),
    ADD COLUMN IF NOT EXISTS start_at     TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS end_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS priority     priority_enum,
    ADD COLUMN IF NOT EXISTS assigned_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS review_by    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS status       status_enum;


-- ============================================================
-- STEP 3: Add columns to TASKS table
--         (auto-created rows — enums default to first value,
--          numbers/dates stay NULL until edited)
-- ============================================================

ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS man_days     NUMERIC(6, 1),
    ADD COLUMN IF NOT EXISTS start_at     TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS end_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS priority     priority_enum DEFAULT 'not_yet_started',
    ADD COLUMN IF NOT EXISTS assigned_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS review_by    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS status       status_enum   DEFAULT 'below_normal';


INSERT INTO templates (id, code, name, description, thumbnail_url, tag, is_active, created_at, created_by, has_episode)
VALUES 
    (1001, 'featurefilm', 'Animation Feature Film', 'Animation feature film template', 'animation-template', NULL, true, NOW(), 1000, true),
    (1002, 'youtube', 'Youtube Episodic', 'YouTube Channel template (Suite for Episodic TV as well)', 'youtube-template', NULL, true, NOW(), 1000, false),
    (1003, 'vfx', 'Visual Effects', 'Visual Effects template', 'vfx-template', NULL, true, NOW(), 1000, false),
    (1004, 'shortfilm', 'Short Film', 'Short film template', 'shortfilm-template', NULL, true, NOW(), 1000, false),
    (1005, 'trailer', 'Trailer', 'Trailer template', 'trailer-template', NULL, true, NOW(), 1000, false),
    (1006, 'game', 'Game', 'Game template', 'game-template', NULL, true, NOW(), 1000, false);