"""
Database initialization script
Run this to create all database tables
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import engine, Base
from app.models import Student, Attendance, Camera, Admin

def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
        
        # List created tables
        print("\nCreated tables:")
        for table in Base.metadata.tables.keys():
            print(f"  - {table}")
        
        print("\nDatabase initialization complete!")
        print("\nNext steps:")
        print("1. Start the FastAPI server: python main.py")
        print("2. Start the frontend: cd ../frontend && npm run dev")
        print("3. Open http://localhost:3000 in your browser")
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. Database 'attendance_db' exists")
        print("3. Database credentials in .env are correct")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Face Recognition Attendance System")
    print("Database Initialization")
    print("=" * 50)
    print()
    
    init_db()
