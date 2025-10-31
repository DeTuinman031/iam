#!/usr/bin/env python3
"""
Quick script to test database connection without starting the full Flask app.
Usage: python test_connection.py
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Load config
from app.config import DevConfig

def test_connection():
    """Test database connection."""
    print("Testing IAM database connection...")
    print(f"Connection string: {DevConfig.SQLALCHEMY_DATABASE_URI.split('@')[1] if '@' in DevConfig.SQLALCHEMY_DATABASE_URI else 'hidden'}")
    
    try:
        engine = create_engine(DevConfig.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test, DATABASE() as db, USER() as user"))
            row = result.fetchone()
            if row:
                print(f"✅ Connection successful!")
                print(f"   Database: {row[1]}")
                print(f"   User: {row[2]}")
                
                # Check for IAM tables
                result = conn.execute(text("SHOW TABLES LIKE 'iam_%'"))
                tables = result.fetchall()
                if tables:
                    print(f"\n✅ Found {len(tables)} IAM tables:")
                    for table in tables:
                        print(f"   - {table[0]}")
                else:
                    print("\n⚠️  No IAM tables found.")
                    print("   Run: mysql -u root < db/iam_schema.sql")
                    print("   Or: flask db upgrade")
                return True
    except OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Start MySQL:")
        print("   - Docker: docker-compose up -d mysql")
        print("   - Local: mysql.server start")
        print("   - Homebrew: brew services start mysql")
        print("\n2. Create database:")
        print("   mysql -u root < db/iam_schema.sql")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

