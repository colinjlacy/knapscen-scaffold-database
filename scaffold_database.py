#!/usr/bin/env python3
"""
MySQL Database Schema Scaffolding Script

This script creates a MySQL database schema with the following tables:
- corporate_customers: Company information and subscription tiers
- user_roles: User role definitions
- users: User accounts linked to corporate customers
- touchpoints: Customer relationship touchpoints

Usage:
    python scaffold_database.py

Environment Variables Required:
    DB_HOST: MySQL server host
    DB_PORT: MySQL server port (default: 3306)
    DB_NAME: Database name
    DB_USER: Database username
    DB_PASSWORD: Database password
"""

import os
import sys
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

import pymysql


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseScaffolder:
    """Handles MySQL database schema creation and sample data insertion."""
    
    def __init__(self):
        """Initialize database connection parameters from environment variables."""
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'charset': 'utf8mb4'
        }
        
        # Validate required environment variables
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            sys.exit(1)
    
    def get_connection(self):
        """Create and return a database connection."""
        try:
            connection = pymysql.connect(**self.db_config)
            logger.info("Successfully connected to MySQL database")
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            sys.exit(1)
    
    def create_schema(self):
        """Create the database schema with all required tables."""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                logger.info("Creating database schema...")
                
                # Create corporate_customers table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS corporate_customers (
                        id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
                        name VARCHAR(64) NOT NULL,
                        subscription_tier ENUM('basic', 'groovy', 'far-out') NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_subscription_tier (subscription_tier),
                        INDEX idx_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                logger.info("✓ Created corporate_customers table")
                
                # Create user_roles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_roles (
                        id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
                        role_name VARCHAR(64) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                logger.info("✓ Created user_roles table")
                
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
                        customer_id CHAR(36) NOT NULL,
                        role_id CHAR(36) NOT NULL,
                        name VARCHAR(64) NOT NULL,
                        email VARCHAR(64) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES corporate_customers(id) ON DELETE CASCADE,
                        FOREIGN KEY (role_id) REFERENCES user_roles(id) ON DELETE RESTRICT,
                        INDEX idx_customer_id (customer_id),
                        INDEX idx_role_id (role_id),
                        INDEX idx_email (email)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                logger.info("✓ Created users table")
                
                # Create touchpoints table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS touchpoints (
                        id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
                        customer_id CHAR(36) NOT NULL,
                        welcome_outreach DATE NULL,
                        technical_onboarding DATE NULL,
                        follow_up_call DATE NULL,
                        feedback_session DATE NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES corporate_customers(id) ON DELETE CASCADE,
                        INDEX idx_customer_id (customer_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                logger.info("✓ Created touchpoints table")
                
            connection.commit()
            logger.info("Schema creation completed successfully!")
            
        except Exception as e:
            connection.rollback()
            logger.error(f"Error creating schema: {e}")
            raise
        finally:
            connection.close()
    
    def insert_sample_data(self):
        """Insert sample data into all tables."""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                logger.info("Inserting sample data...")
                
                # Insert user roles
                user_roles = [
                    (str(uuid.uuid4()), 'customer_account_owner'),
                    (str(uuid.uuid4()), 'admin_user'),
                    (str(uuid.uuid4()), 'generic_user')
                ]
                
                cursor.executemany("""
                    INSERT INTO user_roles (id, role_name) VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE role_name = VALUES(role_name)
                """, user_roles)
                logger.info("✓ Inserted user roles")
                
                # Get role IDs for reference
                cursor.execute("SELECT id, role_name FROM user_roles")
                roles = {row[1]: row[0] for row in cursor.fetchall()}
                
                # Insert corporate customers
                customers = [
                    (str(uuid.uuid4()), 'TechCorp Solutions', 'far-out'),
                    (str(uuid.uuid4()), 'StartupXYZ Inc.', 'basic'),
                    (str(uuid.uuid4()), 'Enterprise Dynamics', 'groovy'),
                    (str(uuid.uuid4()), 'Innovation Labs', 'far-out'),
                    (str(uuid.uuid4()), 'Digital Ventures', 'basic')
                ]
                
                cursor.executemany("""
                    INSERT INTO corporate_customers (id, name, subscription_tier) 
                    VALUES (%s, %s, %s)
                """, customers)
                logger.info("✓ Inserted corporate customers")
                
                # Get customer IDs for reference
                cursor.execute("SELECT id, name FROM corporate_customers")
                customer_ids = [row[0] for row in cursor.fetchall()]
                
                # Insert sample users
                sample_users = [
                    (str(uuid.uuid4()), customer_ids[0], roles['customer_account_owner'], 'John Smith', 'john.smith@techcorp.com'),
                    (str(uuid.uuid4()), customer_ids[0], roles['admin_user'], 'Sarah Johnson', 'sarah.johnson@techcorp.com'),
                    (str(uuid.uuid4()), customer_ids[0], roles['generic_user'], 'Mike Davis', 'mike.davis@techcorp.com'),
                    (str(uuid.uuid4()), customer_ids[1], roles['customer_account_owner'], 'Alice Brown', 'alice.brown@startupxyz.com'),
                    (str(uuid.uuid4()), customer_ids[1], roles['generic_user'], 'Bob Wilson', 'bob.wilson@startupxyz.com'),
                    (str(uuid.uuid4()), customer_ids[2], roles['customer_account_owner'], 'Carol White', 'carol.white@enterprise.com'),
                    (str(uuid.uuid4()), customer_ids[2], roles['admin_user'], 'David Lee', 'david.lee@enterprise.com'),
                    (str(uuid.uuid4()), customer_ids[3], roles['customer_account_owner'], 'Emma Garcia', 'emma.garcia@innovationlabs.com'),
                    (str(uuid.uuid4()), customer_ids[4], roles['customer_account_owner'], 'Frank Miller', 'frank.miller@digitalventures.com'),
                ]
                
                cursor.executemany("""
                    INSERT INTO users (id, customer_id, role_id, name, email) 
                    VALUES (%s, %s, %s, %s, %s)
                """, sample_users)
                logger.info("✓ Inserted sample users")
                
                # Insert sample touchpoints with realistic dates
                base_date = datetime.now() - timedelta(days=90)
                touchpoints = []
                
                for i, customer_id in enumerate(customer_ids):
                    # Generate realistic touchpoint dates
                    welcome_date = base_date + timedelta(days=i*10)
                    onboarding_date = welcome_date + timedelta(days=7) if i % 2 == 0 else None
                    followup_date = welcome_date + timedelta(days=21) if i % 3 != 0 else None
                    feedback_date = welcome_date + timedelta(days=45) if i % 4 == 0 else None
                    
                    touchpoints.append((
                        str(uuid.uuid4()),
                        customer_id,
                        welcome_date.date() if welcome_date else None,
                        onboarding_date.date() if onboarding_date else None,
                        followup_date.date() if followup_date else None,
                        feedback_date.date() if feedback_date else None
                    ))
                
                cursor.executemany("""
                    INSERT INTO touchpoints (id, customer_id, welcome_outreach, 
                                           technical_onboarding, follow_up_call, feedback_session) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, touchpoints)
                logger.info("✓ Inserted sample touchpoints")
                
            connection.commit()
            logger.info("Sample data insertion completed successfully!")
            
        except Exception as e:
            connection.rollback()
            logger.error(f"Error inserting sample data: {e}")
            raise
        finally:
            connection.close()
    
    def verify_schema(self):
        """Verify the created schema and display summary information."""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                logger.info("Verifying schema and displaying summary...")
                
                # Get table counts
                tables = ['corporate_customers', 'user_roles', 'users', 'touchpoints']
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logger.info(f"✓ {table}: {count} records")
                
                # Display some sample data
                logger.info("\nSample corporate customers:")
                cursor.execute("""
                    SELECT name, subscription_tier, created_at 
                    FROM corporate_customers 
                    ORDER BY created_at 
                    LIMIT 3
                """)
                
                for row in cursor.fetchall():
                    logger.info(f"  - {row[0]} ({row[1]}) - Created: {row[2]}")
                
                logger.info("\nSample users with roles:")
                cursor.execute("""
                    SELECT u.name, u.email, r.role_name, c.name as company
                    FROM users u
                    JOIN user_roles r ON u.role_id = r.id
                    JOIN corporate_customers c ON u.customer_id = c.id
                    ORDER BY c.name, r.role_name
                    LIMIT 5
                """)
                
                for row in cursor.fetchall():
                    logger.info(f"  - {row[0]} ({row[1]}) - {row[2]} at {row[3]}")
                
        except Exception as e:
            logger.error(f"Error verifying schema: {e}")
            raise
        finally:
            connection.close()
    
    def run(self):
        """Execute the complete database scaffolding process."""
        logger.info("Starting database scaffolding process...")
        
        try:
            self.create_schema()
            self.insert_sample_data()
            self.verify_schema()
            
            logger.info("\n🎉 Database scaffolding completed successfully!")
            logger.info("Your MySQL database now includes:")
            logger.info("  • Corporate customers with subscription tiers")
            logger.info("  • User roles and user accounts")
            logger.info("  • Customer relationship touchpoints")
            logger.info("  • Sample data for testing")
            
        except Exception as e:
            logger.error(f"Database scaffolding failed: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    scaffolder = DatabaseScaffolder()
    scaffolder.run()


if __name__ == "__main__":
    main()
