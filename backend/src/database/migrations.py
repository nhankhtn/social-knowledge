"""
Database migration utilities
"""
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
import logging

from .connection import engine

logger = logging.getLogger(__name__)


def migrate_add_slug_column():
    """Add slug column to sources table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sources' AND column_name='slug'
            """))
            
            if result.fetchone():
                logger.info("Column 'slug' already exists in sources table")
                return
            
            # Check if table has data
            count_result = conn.execute(text("SELECT COUNT(*) FROM sources"))
            has_data = count_result.scalar() > 0
            
            if has_data:
                # Add column as nullable first
                conn.execute(text("""
                    ALTER TABLE sources 
                    ADD COLUMN slug VARCHAR(255)
                """))
                conn.commit()
                
                # Update existing rows with a default slug (using id as fallback)
                conn.execute(text("""
                    UPDATE sources 
                    SET slug = 'source-' || id::text 
                    WHERE slug IS NULL
                """))
                conn.commit()
                
                # Now add NOT NULL constraint
                conn.execute(text("""
                    ALTER TABLE sources 
                    ALTER COLUMN slug SET NOT NULL
                """))
                # Add unique constraint
                try:
                    conn.execute(text("""
                        ALTER TABLE sources 
                        ADD CONSTRAINT sources_slug_key UNIQUE (slug)
                    """))
                except ProgrammingError:
                    # Constraint might already exist
                    pass
                conn.commit()
            else:
                # No data, can add with NOT NULL directly
                conn.execute(text("""
                    ALTER TABLE sources 
                    ADD COLUMN slug VARCHAR(255) NOT NULL UNIQUE
                """))
                conn.commit()
            
            logger.info("Successfully added 'slug' column to sources table")
            
    except ProgrammingError as e:
        logger.error(f"Error adding slug column: {e}")
        # If unique constraint already exists, that's okay
        if "already exists" not in str(e).lower():
            raise


def migrate_add_users_table():
    """Create users table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='users'
            """))
            
            if result.fetchone():
                logger.info("Table 'users' already exists")
                return
            
            # Table will be created by init_db() via SQLAlchemy
            logger.info("Users table will be created by SQLAlchemy")
            
    except Exception as e:
        logger.warning(f"Error checking users table: {e}")


def migrate_add_category_id_to_articles():
    """Add category_id column to articles table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='articles' AND column_name='category_id'
            """))
            
            if result.fetchone():
                logger.info("Column 'category_id' already exists in articles table")
                return
            
            # Add column as nullable (since existing articles may not have categories)
            conn.execute(text("""
                ALTER TABLE articles 
                ADD COLUMN category_id INTEGER
            """))
            conn.commit()
            
            # Add index for better query performance
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_articles_category_id 
                    ON articles(category_id)
                """))
                conn.commit()
            except ProgrammingError:
                # Index might already exist
                pass
            
            # Check if categories table exists before adding foreign key
            categories_table_check = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='categories'
            """))
            
            if categories_table_check.fetchone():
                # Add foreign key constraint
                try:
                    conn.execute(text("""
                        ALTER TABLE articles 
                        ADD CONSTRAINT articles_category_id_fkey 
                        FOREIGN KEY (category_id) REFERENCES categories(id)
                    """))
                    conn.commit()
                    logger.info("Successfully added foreign key constraint for category_id")
                except ProgrammingError as e:
                    # Constraint might already exist
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Could not add foreign key constraint: {e}")
            else:
                logger.warning("Categories table does not exist yet, skipping foreign key constraint")
            
            logger.info("Successfully added 'category_id' column to articles table")
            
    except ProgrammingError as e:
        logger.error(f"Error adding category_id column: {e}")
        # If column already exists, that's okay
        if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
            raise


def migrate_add_unique_user_provider_constraint():
    """Add unique constraint on (user_id, provider) to notification_channels table"""
    try:
        with engine.connect() as conn:
            # Check if constraint already exists
            result = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name='notification_channels' 
                AND constraint_name='uq_user_provider'
            """))
            
            if result.fetchone():
                logger.info("Unique constraint 'uq_user_provider' already exists on notification_channels table")
                return
            
            # Check for duplicate records first
            duplicates_result = conn.execute(text("""
                SELECT user_id, provider, COUNT(*) as count
                FROM notification_channels
                GROUP BY user_id, provider
                HAVING COUNT(*) > 1
            """))
            
            duplicates = duplicates_result.fetchall()
            if duplicates:
                logger.warning(f"Found {len(duplicates)} duplicate (user_id, provider) pairs. Keeping the most recent one for each pair.")
                # For each duplicate pair, keep only the most recent one (by id or created_at)
                for dup in duplicates:
                    user_id, provider, count = dup
                    # Delete all but the most recent one
                    conn.execute(text("""
                        DELETE FROM notification_channels
                        WHERE user_id = :user_id AND provider = :provider
                        AND id NOT IN (
                            SELECT id FROM notification_channels
                            WHERE user_id = :user_id AND provider = :provider
                            ORDER BY created_at DESC, id DESC
                            LIMIT 1
                        )
                    """), {"user_id": user_id, "provider": provider})
                conn.commit()
                logger.info("Cleaned up duplicate notification channels")
            
            # Add unique constraint
            conn.execute(text("""
                ALTER TABLE notification_channels 
                ADD CONSTRAINT uq_user_provider UNIQUE (user_id, provider)
            """))
            conn.commit()
            
            logger.info("Successfully added unique constraint 'uq_user_provider' to notification_channels table")
            
    except ProgrammingError as e:
        logger.error(f"Error adding unique constraint: {e}")
        # If constraint already exists, that's okay
        if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
            raise


def init_db_with_migrations():
    """Initialize database and run migrations"""
    from .connection import init_db
    
    # Create all tables first
    init_db()
    
    # Run migrations
    try:
        migrate_add_slug_column()
        migrate_add_users_table()
        migrate_add_category_id_to_articles()
        migrate_add_unique_user_provider_constraint()
    except Exception as e:
        logger.warning(f"Migration failed (might be expected if column/table already exists): {e}")

