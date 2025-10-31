#!/bin/bash
# Setup script for IAM MySQL database

echo "🔍 Checking MySQL status..."

# Check if MySQL is running
if mysql -u root -e "SELECT 1" &>/dev/null; then
    echo "✅ MySQL is running!"
else
    echo "❌ MySQL is not running"
    echo ""
    echo "Please start MySQL using one of these methods:"
    echo ""
    echo "Option 1: Homebrew MySQL (recommended)"
    echo "  brew install mysql"
    echo "  brew services start mysql"
    echo ""
    echo "Option 2: If you have MySQL installed via Anaconda"
    echo "  Check MySQL installation: conda list mysql"
    echo "  Or install MySQL server separately"
    echo ""
    echo "Option 3: Docker (if you install Docker)"
    echo "  docker-compose up -d mysql"
    echo ""
    exit 1
fi

echo ""
echo "📦 Setting up IAM database..."

# Check if database exists
if mysql -u root -e "USE iam;" &>/dev/null; then
    echo "⚠️  Database 'iam' already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mysql -u root -e "DROP DATABASE IF EXISTS iam;"
        echo "✅ Dropped existing database"
    else
        echo "ℹ️  Keeping existing database"
        exit 0
    fi
fi

# Create database and schema
echo "Creating database and tables..."
if mysql -u root < db/iam_schema.sql; then
    echo "✅ Database and schema created successfully!"
    echo ""
    echo "You can now:"
    echo "  - Test connection: FLASK_APP=app flask test-db"
    echo "  - Create test user: FLASK_APP=app flask create-test-user"
else
    echo "❌ Failed to create database"
    echo "Try running manually: mysql -u root -p < db/iam_schema.sql"
    exit 1
fi

