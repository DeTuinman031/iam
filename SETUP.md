# MySQL Setup Guide for IAM

**Version:** v1.1.1

## Quick Setup Options

### Option 1: Homebrew MySQL (Recommended for macOS)

```bash
# Install MySQL via Homebrew
brew install mysql

# Start MySQL service
brew services start mysql

# Create database and schema
mysql -u root < db/iam_schema.sql

# Test connection
FLASK_APP=app flask test-db
```

### Option 2: Use the Setup Script

```bash
# Run the automated setup script
./setup_mysql.sh
```

### Option 3: Manual Setup

1. **Start MySQL** (if you have it installed):
   ```bash
   mysql.server start
   # OR
   brew services start mysql
   ```

2. **Create the database:**
   ```bash
   mysql -u root -p < db/iam_schema.sql
   ```
   
   If you don't have a root password:
   ```bash
   mysql -u root < db/iam_schema.sql
   ```

3. **Verify it works:**
   ```bash
   FLASK_APP=app flask test-db
   ```

4. **Create a test user:**
   ```bash
   FLASK_APP=app flask create-test-user
   ```

## Troubleshooting

### MySQL Not Running

**Check if MySQL is installed:**
```bash
which mysql
mysql --version
```

**Start MySQL (Homebrew):**
```bash
brew services start mysql
```

**Start MySQL (Manual):**
```bash
mysql.server start
```

### Connection Issues

**Test MySQL connection:**
```bash
mysql -u root -e "SELECT 1"
```

**If you get "socket" errors**, MySQL might be installed but not running:
```bash
# Try to find MySQL socket
find /tmp /var/run -name mysql.sock 2>/dev/null

# Or start MySQL server
brew services start mysql
```

### Database Already Exists

If you need to recreate the database:
```bash
mysql -u root -e "DROP DATABASE IF EXISTS iam;"
mysql -u root < db/iam_schema.sql
```

## Next Steps

Once MySQL is running and the database is created:

1. ✅ Test connection: `FLASK_APP=app flask test-db`
2. ✅ Create test user: `FLASK_APP=app flask create-test-user`
3. ✅ Start Flask app: `python manage.py run`
4. ✅ Visit: http://127.0.0.1:5000/auth/login

