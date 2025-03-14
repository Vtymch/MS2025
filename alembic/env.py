import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from app.models import Base  # Import the Base model from the app
from alembic import context

# Add the "master-server" folder to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'master-server')))

# Alembic configuration object
config = context.config

# Interpret the configuration file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define the metadata for the database models
target_metadata = Base.metadata

# Functions to perform migrations
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    
    This mode does not require a database connection. Instead, 
    it generates SQL migration scripts.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # Start a new transaction and run migrations
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    This mode requires a database connection to apply the migrations directly.
    """
    # Create an engine using the configuration settings
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),  # Get database configuration
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Disable connection pooling for migrations
    )

    # Establish a connection and run migrations
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        # Start a new transaction and run migrations
        with context.begin_transaction():
            context.run_migrations()


# Determine whether to run migrations in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
