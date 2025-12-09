"""Initial schema creation with all core entities.

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-12-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all core tables for Phase 1."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_admin', sa.Boolean(), default=False, nullable=False),
        sa.Column('language_preference', sa.String(5), default='en', nullable=False),
        sa.Column('theme', sa.String(10), default='light', nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_active', 'users', ['is_active'])

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('bio', sa.String(500), nullable=True),
        sa.Column('avatar_url', sa.String(255), nullable=True),
        sa.Column('organization', sa.String(255), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('email_notifications', sa.Boolean(), default=True),
        sa.Column('show_progress_publicly', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )

    # Create modules table
    op.create_table(
        'modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('slug', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('is_published', sa.Boolean(), default=False, nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )
    op.create_index('idx_module_slug', 'modules', ['slug'])
    op.create_index('idx_module_published', 'modules', ['is_published'])

    # Create chapters table
    op.create_table(
        'chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('difficulty_level', sa.String(20), default='intermediate'),
        sa.Column('estimated_duration_minutes', sa.Integer(), default=60),
        sa.Column('content_html', sa.Text(), nullable=True),
        sa.Column('learning_objectives', sa.Text(), nullable=True),
        sa.Column('is_published', sa.Boolean(), default=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )
    op.create_index('idx_chapter_module_slug', 'chapters', ['module_id', 'slug'])
    op.create_index('idx_chapter_published', 'chapters', ['is_published'])
    op.create_index('idx_chapter_difficulty', 'chapters', ['difficulty_level'])

    # Create embeddings table
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), default=0),
        sa.Column('embedding_model', sa.String(100), default='text-embedding-3-small'),
        sa.Column('qdrant_point_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )
    op.create_index('idx_embedding_chapter', 'embeddings', ['chapter_id'])

    # Create chapter_progress table
    op.create_table(
        'chapter_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('status', sa.String(20), default='not_started'),
        sa.Column('progress_percentage', sa.Integer(), default=0),
        sa.Column('time_spent_seconds', sa.Integer(), default=0),
        sa.Column('quiz_score', sa.Float(), nullable=True),
        sa.Column('quiz_passed', sa.Boolean(), default=False),
        sa.Column('exercise_passed', sa.Boolean(), default=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )
    op.create_index('idx_progress_user', 'chapter_progress', ['user_id'])
    op.create_index('idx_progress_chapter', 'chapter_progress', ['chapter_id'])
    op.create_index('idx_progress_user_chapter', 'chapter_progress', ['user_id', 'chapter_id'])
    op.create_index('idx_progress_status', 'chapter_progress', ['status'])

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('conversation_session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('parent_message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_messages.id'), nullable=True),
        sa.Column('intent', sa.String(100), nullable=True),
        sa.Column('context_chapter_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('context_module_slug', sa.String(100), nullable=True),
        sa.Column('user_difficulty_level', sa.String(50), nullable=True),
        sa.Column('clarification_depth', sa.Integer(), default=0),
        sa.Column('was_follow_up', sa.Boolean(), default=False),
        sa.Column('sources', sa.Text(), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('helpful_count', sa.Integer(), default=0),
        sa.Column('unhelpful_count', sa.Integer(), default=0),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )
    op.create_index('idx_message_user', 'chat_messages', ['user_id'])
    op.create_index('idx_message_created', 'chat_messages', ['created_at'])
    op.create_index('idx_message_session', 'chat_messages', ['conversation_session_id'])

    # Create translations table
    op.create_table(
        'translations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('language_code', sa.String(5), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=True),
        sa.Column('is_published', sa.Boolean(), default=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )
    op.create_index('idx_translation_chapter_lang', 'translations', ['chapter_id', 'language_code'])

    # Create capstone_submissions table
    op.create_table(
        'capstone_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.func.gen_random_uuid()),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('source_code_url', sa.String(255), nullable=True),
        sa.Column('demo_url', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )
    op.create_index('idx_capstone_user', 'capstone_submissions', ['user_id'])
    op.create_index('idx_capstone_status', 'capstone_submissions', ['status'])


def downgrade() -> None:
    """Drop all tables created in upgrade."""
    op.drop_index('idx_capstone_status', table_name='capstone_submissions')
    op.drop_index('idx_capstone_user', table_name='capstone_submissions')
    op.drop_table('capstone_submissions')

    op.drop_index('idx_translation_chapter_lang', table_name='translations')
    op.drop_table('translations')

    op.drop_index('idx_message_session', table_name='chat_messages')
    op.drop_index('idx_message_created', table_name='chat_messages')
    op.drop_index('idx_message_user', table_name='chat_messages')
    op.drop_table('chat_messages')

    op.drop_index('idx_progress_status', table_name='chapter_progress')
    op.drop_index('idx_progress_user_chapter', table_name='chapter_progress')
    op.drop_index('idx_progress_chapter', table_name='chapter_progress')
    op.drop_index('idx_progress_user', table_name='chapter_progress')
    op.drop_table('chapter_progress')

    op.drop_index('idx_embedding_chapter', table_name='embeddings')
    op.drop_table('embeddings')

    op.drop_index('idx_chapter_difficulty', table_name='chapters')
    op.drop_index('idx_chapter_published', table_name='chapters')
    op.drop_index('idx_chapter_module_slug', table_name='chapters')
    op.drop_table('chapters')

    op.drop_index('idx_module_published', table_name='modules')
    op.drop_index('idx_module_slug', table_name='modules')
    op.drop_table('modules')

    op.drop_table('user_profiles')

    op.drop_index('idx_user_active', table_name='users')
    op.drop_index('idx_user_email', table_name='users')
    op.drop_table('users')
