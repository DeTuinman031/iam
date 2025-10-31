# app/__init__.py
"""
IAM Application Factory
Version: v1.1.1
"""
from flask import Flask
from flask_cors import CORS
from app.config import DevConfig  # or ProdConfig in production
from app.extensions import db, login_manager, migrate
from app.auth.models import IAMUserAccount  # make sure models are imported so SQLAlchemy sees them

# optional: import blueprints
from app.auth.routes_login import auth_bp
from app.auth.routes_admin import admin_bp
from app.auth.routes_api import api_bp


def create_app(config_object=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # 1. init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CORS for API access
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('ALLOWED_ORIGINS', ['*']),
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # 2. configure login manager user loader
    @login_manager.user_loader
    def load_user(user_id):
        # Flask-Login calls this with user_id from session
        return IAMUserAccount.query.get(int(user_id))

    login_manager.login_view = "auth.login_page"   # endpoint name for @login_required redirects

    # 3. register blueprints for IAM module
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp)  # No prefix, uses /api from blueprint

    # 4. healthcheck route that tests app boots + DB connectivity
    @app.route("/healthz")
    def healthcheck():
        try:
            # Test database connectivity
            db.session.execute(db.text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {
            "status": "ok",
            "service": "IAM",
            "database": db_status
        }, 200 if db_status == "connected" else 503

    # 5. Register CLI commands
    @app.cli.command("test-db")
    def test_db():
        """Test database connection."""
        try:
            result = db.session.execute(db.text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database connection successful!")
                # Try to query tables
                try:
                    tables = db.session.execute(
                        db.text("SHOW TABLES LIKE 'iam_%'")
                    ).fetchall()
                    if tables:
                        print(f"✅ Found {len(tables)} IAM tables")
                        for table in tables:
                            print(f"   - {table[0]}")
                    else:
                        print("⚠️  No IAM tables found. Run 'flask db upgrade' to create them.")
                except Exception as e:
                    print(f"⚠️  Could not check tables: {e}")
                return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print(f"\nConnection string: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
            print("\nTroubleshooting:")
            print("1. Ensure MySQL is running: mysql.server start (or brew services start mysql)")
            print("2. Check database exists: mysql -u root -e 'SHOW DATABASES'")
            print("3. Create database if needed: mysql -u root < db/iam_schema.sql")
            return False

    @app.cli.command("create-test-user")
    def create_test_user():
        """Create a test user for development."""
        from app.auth.models import IAMUserAccount, IAMRole
        from sqlalchemy.exc import OperationalError
        
        try:
            username = input("Username (default: testuser): ").strip() or "testuser"
            password = input("Password (default: testpass123): ").strip() or "testpass123"
            email = input(f"Email (default: {username}@example.com): ").strip() or f"{username}@example.com"
            
            # Check if user exists
            if IAMUserAccount.query.filter_by(username=username).first():
                print(f"❌ User '{username}' already exists!")
                return
            
            # Create user
            user = IAMUserAccount(
                username=username,
                email=email,
                display_name=username.title(),
                parent_id=1,  # Default tenant
                auth_provider='local',
                is_active=True,  # Explicitly set active
                is_locked=False  # Explicitly set not locked
            )
            user.set_password(password)
            
            # Try to assign admin role if it exists
            admin_role = IAMRole.query.filter_by(role_name='admin').first()
            if admin_role:
                user.roles.append(admin_role)
            
            db.session.add(user)
            db.session.commit()
            
            print(f"✅ Created user: {username}")
            print(f"   Email: {email}")
            print(f"   Roles: {[r.role_name for r in user.roles]}")
            print(f"\nYou can now login at: http://127.0.0.1:5000/auth/login")
        except OperationalError as e:
            print(f"❌ Database connection failed: {e}")
            print("\nMySQL is not running. Please start MySQL first:")
            print("   - Docker: docker-compose up -d mysql")
            print("   - Homebrew: brew services start mysql")
            print("   - Manual: mysql.server start")
            print("\nThen create the database:")
            print("   mysql -u root < db/iam_schema.sql")
            raise

    @app.cli.command("init-db")
    def init_db():
        """Initialize database tables."""
        db.create_all()
        print("Database tables created.")

    return app
