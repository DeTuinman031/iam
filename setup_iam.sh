#!/bin/bash
# IAM Quick Setup Script
# Makes IAM "plug and play" ready

set -e

echo "=========================================="
echo "IAM Service - Quick Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: Please run this script from the iam directory${NC}"
    exit 1
fi

# Step 1: Check Python
echo -e "${YELLOW}Step 1: Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 3: Check MySQL
echo -e "${YELLOW}Step 3: Checking MySQL...${NC}"
if command -v docker &> /dev/null && docker ps | grep -q mysql; then
    echo -e "${GREEN}✓ MySQL running in Docker${NC}"
    MYSQL_RUNNING=true
elif mysql -u root -e "SELECT 1" &> /dev/null 2>&1; then
    echo -e "${GREEN}✓ MySQL running locally${NC}"
    MYSQL_RUNNING=true
else
    echo -e "${YELLOW}! MySQL not running${NC}"
    read -p "Start MySQL with Docker Compose? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose up -d mysql
        echo "Waiting for MySQL to start..."
        sleep 5
        MYSQL_RUNNING=true
    else
        echo -e "${YELLOW}You'll need to start MySQL manually${NC}"
        MYSQL_RUNNING=false
    fi
fi
echo ""

# Step 4: Setup database
if [ "$MYSQL_RUNNING" = true ]; then
    echo -e "${YELLOW}Step 4: Setting up database...${NC}"
    if mysql -u root iam -e "SELECT 1" &> /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database 'iam' already exists${NC}"
        read -p "Recreate database? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mysql -u root -e "DROP DATABASE IF EXISTS iam;"
            echo -e "${GREEN}✓ Dropped existing database${NC}"
        fi
    fi
    
    if ! mysql -u root iam -e "SELECT 1" &> /dev/null 2>&1; then
        echo "Creating database and schema..."
        mysql -u root < db/iam_schema.sql
        echo -e "${GREEN}✓ Database and schema created${NC}"
    fi
else
    echo -e "${YELLOW}! Skipping database setup (MySQL not running)${NC}"
fi
echo ""

# Step 5: Test connection
if [ "$MYSQL_RUNNING" = true ]; then
    echo -e "${YELLOW}Step 5: Testing connection...${NC}"
    export FLASK_APP=app
    if python3 -c "from app import create_app; app = create_app(); app.app_context().push(); from app.extensions import db; db.session.execute(db.text('SELECT 1'))" 2>/dev/null; then
        echo -e "${GREEN}✓ Database connection successful${NC}"
    else
        echo -e "${RED}✗ Database connection failed${NC}"
    fi
    echo ""
fi

# Step 6: Create test user
if [ "$MYSQL_RUNNING" = true ]; then
    echo -e "${YELLOW}Step 6: Create test user...${NC}"
    USER_EXISTS=$(mysql -u root iam -s -N -e "SELECT COUNT(*) FROM iam_user_account WHERE username='testuser'" 2>/dev/null || echo "0")
    if [ "$USER_EXISTS" = "0" ]; then
        export FLASK_APP=app
        echo -e "testuser\ntestpass123\ntestuser@example.com" | python3 manage.py create-test-user 2>/dev/null
        echo -e "${GREEN}✓ Test user created${NC}"
    else
        echo -e "${GREEN}✓ Test user already exists${NC}"
    fi
    echo ""
fi

# Step 7: Run tests
echo -e "${YELLOW}Step 7: Running tests...${NC}"
python3 test_api.py 2>/dev/null && echo -e "${GREEN}✓ All tests passed${NC}" || echo -e "${YELLOW}! Some tests may have failed (check manually)${NC}"
echo ""

# Summary
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Start the server: python manage.py run"
echo "  2. Visit: http://localhost:5000/auth/login"
echo "  3. Login with: testuser / testpass123"
echo ""
echo "Documents:"
echo "  - README.md: Quick start guide"
echo "  - INTEGRATION_SUMMARY.md: Integration overview"
echo "  - docs/integration_guide.md: Detailed integration"
echo "  - docs/plug_and_play_requirements.md: Future improvements"
echo ""

