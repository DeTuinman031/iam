# Testing Guide for IAM Service

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MySQL Database

**Option A: Using Docker (Recommended)**
```bash
docker-compose up -d mysql
```
This will:
- Start MySQL 8.4 in a container
- Create the `iam` database
- Run the schema from `db/iam_schema.sql` automatically
- Expose MySQL on port 3306

**Option B: Local MySQL**
```bash
# Start MySQL (macOS with Homebrew)
brew services start mysql
# OR
mysql.server start

# Create database and schema
mysql -u root -p < db/iam_schema.sql
```

### 3. Test Database Connection

**Quick test script:**
```bash
python test_connection.py
```

**Or using Flask CLI:**
```bash
flask test-db
```

### 4. Run Database Migrations (if using Flask-Migrate)
```bash
flask db init          # First time only
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Create a Test User
```bash
flask create-test-user
```

### 6. Start the Flask Application
```bash
flask run
# OR
python manage.py run
```

### 7. Test Endpoints

**Health Check (includes DB status):**
```bash
curl http://127.0.0.1:5000/healthz
```

Expected response:
```json
{
  "status": "ok",
  "service": "IAM",
  "database": "connected"
}
```

**Login Page:**
```bash
open http://127.0.0.1:5000/auth/login
```

## Testing Commands

All commands use `flask` CLI:

| Command | Description |
|---------|-------------|
| `flask test-db` | Test database connection and list tables |
| `flask create-test-user` | Interactive command to create a test user |
| `flask init-db` | Create all tables (alternative to migrations) |
| `flask db migrate -m "message"` | Generate migration |
| `flask db upgrade` | Apply migrations |
| `flask run` | Start development server |

## Troubleshooting

### Database Connection Fails

1. **Check if MySQL is running:**
   ```bash
   # Docker
   docker ps | grep mysql
   
   # Local MySQL
   mysql.server status
   ```

2. **Verify credentials in `app/config.py`:**
   - Default: `mysql+pymysql://iam_user:iam_pass@localhost:3306/iam`
   - Or set `DATABASE_URL` environment variable

3. **Test MySQL connection directly:**
   ```bash
   mysql -u iam_user -piam_pass -h localhost iam -e "SELECT 1"
   ```

4. **Check database exists:**
   ```bash
   mysql -u root -e "SHOW DATABASES LIKE 'iam'"
   ```

### Missing Tables

If `flask test-db` shows "No IAM tables found":

1. **Using SQL schema:**
   ```bash
   mysql -u root < db/iam_schema.sql
   ```

2. **Using Flask-Migrate:**
   ```bash
   flask db upgrade
   ```

### Port Already in Use

If port 5000 is taken:
```bash
flask run --port 5001
```

## Environment Variables

You can override defaults with environment variables:

```bash
export DATABASE_URL="mysql+pymysql://user:pass@localhost:3306/iam"
export FLASK_SECRET_KEY="your-secret-key-here"

flask run
```

