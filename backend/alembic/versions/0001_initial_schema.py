"""Create the initial Little Star Playhouse PostgreSQL schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-20
"""
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

_TABLES = (    'CREATE TABLE inquiries (\n\tid UUID NOT NULL, \n\tparent_name VARCHAR(200) NOT NULL, \n\tphone VARCHAR(20) NOT NULL, \n\temail VARCHAR(255), \n\tchild_age VARCHAR(50), \n\tprogram VARCHAR(100), \n\tmessage TEXT, \n\tstatus VARCHAR(20) NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id)\n)',
    'CREATE TABLE login_attempts (\n\tid SERIAL NOT NULL, \n\tip_address VARCHAR(45) NOT NULL, \n\tattempted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tsuccess BOOLEAN NOT NULL, \n\tPRIMARY KEY (id)\n)',
    'CREATE TABLE users (\n\tid UUID NOT NULL, \n\temail VARCHAR(255) NOT NULL, \n\tpassword_hash VARCHAR(512) NOT NULL, \n\tdisplay_name VARCHAR(100) NOT NULL, \n\trole VARCHAR(20) NOT NULL, \n\tis_active BOOLEAN NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id)\n)',
    'CREATE TABLE sessions (\n\tid UUID NOT NULL, \n\tuser_id UUID NOT NULL, \n\ttoken_hash VARCHAR(128) NOT NULL, \n\tcsrf_token VARCHAR(64) NOT NULL, \n\tip_address VARCHAR(45), \n\tuser_agent VARCHAR(512), \n\texpires_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE\n)',
    'CREATE TABLE stored_files (\n\tid UUID NOT NULL, \n\tstorage_key VARCHAR(512) NOT NULL, \n\toriginal_filename VARCHAR(255) NOT NULL, \n\tdisplay_filename VARCHAR(255) NOT NULL, \n\tmime_type VARCHAR(100) NOT NULL, \n\textension VARCHAR(20) NOT NULL, \n\tfile_size BIGINT NOT NULL, \n\tsha256_checksum VARCHAR(64) NOT NULL, \n\tis_public BOOLEAN NOT NULL, \n\tuploader_id UUID, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (storage_key), \n\tFOREIGN KEY(uploader_id) REFERENCES users (id) ON DELETE SET NULL\n)',
    'CREATE TABLE documents (\n\tid UUID NOT NULL, \n\ttitle VARCHAR(255) NOT NULL, \n\tdescription TEXT NOT NULL, \n\tcategory VARCHAR(50) NOT NULL, \n\tfile_id UUID NOT NULL, \n\tstatus VARCHAR(20) NOT NULL, \n\tuploader_id UUID, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tpublished_at TIMESTAMP WITH TIME ZONE, \n\texpires_at TIMESTAMP WITH TIME ZONE, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(file_id) REFERENCES stored_files (id) ON DELETE RESTRICT, \n\tFOREIGN KEY(uploader_id) REFERENCES users (id) ON DELETE SET NULL\n)',
    'CREATE TABLE notices (\n\tid UUID NOT NULL, \n\tslug VARCHAR(280) NOT NULL, \n\ttitle VARCHAR(255) NOT NULL, \n\texcerpt TEXT NOT NULL, \n\tbody TEXT NOT NULL, \n\tcategory VARCHAR(50) NOT NULL, \n\tstatus VARCHAR(20) NOT NULL, \n\tis_pinned BOOLEAN NOT NULL, \n\tis_important BOOLEAN NOT NULL, \n\tcover_image_id UUID, \n\texternal_url VARCHAR(2048), \n\tauthor_id UUID NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tpublished_at TIMESTAMP WITH TIME ZONE, \n\texpires_at TIMESTAMP WITH TIME ZONE, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(cover_image_id) REFERENCES stored_files (id) ON DELETE SET NULL, \n\tFOREIGN KEY(author_id) REFERENCES users (id) ON DELETE RESTRICT\n)',
    'CREATE TABLE notice_attachments (\n\tid UUID NOT NULL, \n\tnotice_id UUID NOT NULL, \n\tfile_id UUID NOT NULL, \n\tattachment_type VARCHAR(20) NOT NULL, \n\tdisplay_order INTEGER NOT NULL, \n\tcaption VARCHAR(500), \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(notice_id) REFERENCES notices (id) ON DELETE CASCADE, \n\tFOREIGN KEY(file_id) REFERENCES stored_files (id) ON DELETE CASCADE\n)'
)
_INDEXES = (    'CREATE INDEX ix_login_attempts_ip_address ON login_attempts (ip_address)',
    'CREATE UNIQUE INDEX ix_users_email ON users (email)',
    'CREATE UNIQUE INDEX ix_sessions_token_hash ON sessions (token_hash)',
    'CREATE INDEX ix_sessions_user_id ON sessions (user_id)',
    'CREATE INDEX ix_documents_category ON documents (category)',
    'CREATE INDEX ix_notices_category ON notices (category)',
    'CREATE UNIQUE INDEX ix_notices_slug ON notices (slug)',
    'CREATE INDEX ix_notices_status ON notices (status)',
    'CREATE INDEX ix_notice_attachments_notice_id ON notice_attachments (notice_id)'
)
_DROP_TABLES = ['notice_attachments', 'notices', 'documents', 'stored_files', 'sessions', 'users', 'login_attempts', 'inquiries']


def upgrade() -> None:
    """Create application tables and indexes on an empty database."""
    for statement in _TABLES:
        op.execute(statement)
    for statement in _INDEXES:
        op.execute(statement)


def downgrade() -> None:
    """Drop only tables introduced by this initial revision."""
    for table in _DROP_TABLES:
        op.drop_table(table)
