#!/usr/bin/env python3
"""Setup script to create all backend files for CivicConnect."""

import os

BASE = "D:/Civic Issue Reporting System/civicconnect/backend"

# Create directories
os.makedirs(BASE, exist_ok=True)

# Write database.py
with open(os.path.join(BASE, "database.py"), "w") as f:
    f.write('''"""
CivicConnect - Database Configuration
SQLite database setup with SQLAlchemy for easy demo setup.
Author: CivicConnect Team
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# Database URL - SQLite file
SQLALCHEMY_DATABASE_URL = "sqlite:///./civicconnect.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create base class
Base = declarative_base()

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== USER MODEL ====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="citizen")
    phone = Column(String)
    address = Column(String)
    profile_image = Column(String, default="default_avatar.png")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    # Relationships
    issues = relationship("Issue", back_populates="user")
    supports = relationship("IssueSupport", back_populates="user")
    feedback = relationship("CitizenFeedback", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# ==================== DEPARTMENT MODEL ====================
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    issues = relationship("Issue", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name})>"

# ==================== ISSUE MODEL ====================
class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    title = Column(String, index=True)
    category = Column(String)
    description = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String)
    severity = Column(String, default="Medium")
    status = Column(String, default="Reported")
    priority_score = Column(Integer, default=0)
    priority_level = Column(String, default="Medium")
    photo_path = Column(String, default="")
    is_duplicate = Column(Boolean, default=False)
    duplicate_suggestion = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="issues")
    department = relationship("Department", back_populates="issues")
    supports = relationship("IssueSupport", back_populates="issue")
    updates = relationship("IssueUpdate", back_populates="issue")
    feedback = relationship("CitizenFeedback", back_populates="issue")

    def __repr__(self):
        return f"<Issue(id={self.id}, complaint_id={self.complaint_id}, title={self.title})>"

# ==================== ISSUE SUPPORT MODEL ====================
class IssueSupport(Base):
    __tablename__ = "issue_support"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    issue_id = Column(Integer, ForeignKey("issues.id"))
    support_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="supports")
    issue = relationship("Issue", back_populates="supports")

    def __repr__(self):
        return f"<IssueSupport(user_id={self.user_id}, issue_id={self.issue_id}, count={self.support_count})>"

# ==================== ISSUE UPDATE MODEL ====================
class IssueUpdate(Base):
    __tablename__ = "issue_updates"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    action = Column(String)
    details = Column(Text)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    issue = relationship("Issue", back_populates="updates")
    admin = relationship("User", foreign_keys=[admin_id])

    def __repr__(self):
        return f"<IssueUpdate(id={self.id}, issue_id={self.issue_id}, action={self.action})>"


# ==================== CITIZEN FEEDBACK MODEL ====================
class CitizenFeedback(Base):
    __tablename__ = "citizen_feedback"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    feedback_type = Column(String)
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    issue = relationship("Issue", back_populates="feedback")
    user = relationship("User", back_populates="feedback")

    def __repr__(self):
        return f"<CitizenFeedback(id={self.id}, issue_id={self.issue_id}, type={self.feedback_type})>"


# ==================== NOTIFICATION MODEL ====================
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, title={self.title})>"

# Create tables
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


# Insert demo data
def insert_demo_data():
    """Insert sample data for demonstration."""
    db = SessionLocal()

    # Check if demo data already exists
    admin_count = db.query(User).filter(User.role == "admin").count()
    if admin_count > 0:
        db.close()
        return

    # Create departments
    departments = [
        {"name": "Roads Department", "description": "Road, pothole, and infrastructure maintenance"},
        {"name": "Electrical Department", "description": "Streetlight and electrical issues"},
        {"name": "Sanitation Department", "description": "Garbage and waste management"},
        {"name": "Water Department", "description": "Water supply and leakage issues"},
        {"name": "Drainage Department", "description": "Drainage and flooding issues"},
        {"name": "Public Works Department", "description": "Public safety and other issues"},
    ]

    for dept in departments:
        existing = db.query(Department).filter(Department.name == dept["name"]).first()
        if not existing:
            new_dept = Department(name=dept["name"], description=dept["description"])
            db.add(new_dept)

    db.commit()

    # Create admin user
    admin = User(
        citizen_id="ADMIN001",
        name="Super Admin",
        email="admin@civicconnect.com",
        password_hash="$2b$12$LQv4N2L0J5xX.K8G7zKXMOYhqrLQIzMGk0.L0HhRz.jH1YzO8cLKu",
        role="admin",
        phone="1234567890",
        address="City Hall, Civic Connect"
    )
    db.add(admin)

    # Create citizen users
    citizens = [
        {"name": "John Doe", "email": "john@civicconnect.com", "password_hash": "$2b$12$LQv4N2L0J5xX.K8G7zKXMOYhqrLQIzMGk0.L0HhRz.jH1YzO8cLKu", "phone": "9876543210", "role": "citizen"},
        {"name": "Jane Smith", "email": "jane@civicconnect.com", "password_hash": "$2b$12$LQv4N2L0J5xX.K8G7zKXMOYhqrLQIzMGk0.L0HhRz.jH1YzO8cLKu", "phone": "8765432109", "role": "citizen"},
        {"name": "Mike Johnson", "email": "mike@civicconnect.com", "password_hash": "$2b$12$LQv4N2L0J5xX.K8G7zKXMOYhqrLQIzMGk0.L0HhRz.jH1YzO8cLKu", "phone": "7654321098", "role": "citizen"},
        {"name": "Sarah Wilson", "email": "sarah@civicconnect.com", "password_hash": "$2b$12$LQv4N2L0J5xX.K8G7zKXMOYhqrLQIzMGk0.L0HhRz.jH1YzO8cLKu", "phone": "6543210987", "role": "citizen"},
        {"name": "David Brown", "email": "david@civicconnect.com", "password_hash": "$2b$12$LQv4N2L0J5xX.K8G7zKXMOYhqrLQIzMGk0.L0HhRz.jH1YzO8cLKu", "phone": "5432109876", "role": "citizen"},
    ]

    for i, citizen in enumerate(citizens):
        citizen["citizen_id"] = f"CIT-{i+1:03d}"
        db.add(User(**citizen))

    db.commit()
    # Sample issues
    issues = [
        {
            "user_id": 1, "title": "Large Pothole on Main Street", "category": "Road & Pothole",
            "description": "Big pothole near the traffic signal on Main Street, danger to vehicles.",
            "latitude": 40.7128, "longitude": -74.0060, "location_name": "Main Street near Traffic Signal 1",
            "severity": "High", "status": "Reported", "priority_score": 85, "priority_level": "High",
            "photo_path": "uploads/road1.jpg", "is_duplicate": False, "duplicate_suggestion": "",
            "complaint_id": "CC-1001"
        },
        {
            "user_id": 2, "title": "Broken Streetlight on Oak Avenue", "category": "Streetlight",
            "description": "Streetlight near park is not working since last night.",
            "latitude": 40.7282, "longitude": -73.7949, "location_name": "Oak Avenue near Central Park",
            "severity": "Medium", "status": "In Progress", "priority_score": 60, "priority_level": "Medium",
            "photo_path": "uploads/streetlight1.jpg", "is_duplicate": False, "duplicate_suggestion": "",
            "complaint_id": "CC-1002"
        },
        {
            "user_id": 1, "title": "Garbage Accumulation Near School Zone", "category": "Garbage & Sanitation",
            "description": "Trash scattered around Lincoln High School grounds.",
            "latitude": 40.7345, "longitude": -73.8468, "location_name": "Lincoln High School grounds",
            "severity": "Low", "status": "Resolved", "priority_score": 45, "priority_level": "Low",
            "photo_path": "uploads/garbage1.jpg", "is_duplicate": False, "duplicate_suggestion": "",
            "complaint_id": "CC-1003"
        },
        {
            "user_id": 3, "title": "Water Leakage from Main Pipe", "category": "Water Supply",
            "description": "Water leaking from underground pipe near community center.",
            "latitude": 40.7180, "longitude": -74.0020, "location_name": "Community Center, 100 Main St",
            "severity": "Critical", "status": "Resolved", "priority_score": 95, "priority_level": "Critical",
            "photo_path": "uploads/water1.jpg", "is_duplicate": False, "duplicate_suggestion": "",
            "complaint_id": "CC-1004"
        },
        {
            "user_id": 4, "title": "Blocked Drainage Channel on Elm Street", "category": "Drainage",
            "description": "Drainage channel blocked by debris causing waterlogging.",
            "latitude": 40.7250, "longitude": -74.0100, "location_name": "Elm Street near School",
            "severity": "Medium", "status": "In Progress", "priority_score": 55, "priority_level": "Medium",
            "photo_path": "uploads/drainage1.jpg", "is_duplicate": False, "duplicate_suggestion": "",
            "complaint_id": "CC-1005"
        },
        {
            "user_id": 5, "title": "Broken Public Bench at Bus Stop", "category": "Public Safety",
            "description": "Bench at bus stop 5 is broken and poses safety risk.",
            "latitude": 40.7200, "longitude": -74.0080, "location_name": "Bus Stop 5, Oak Avenue",
            "severity": "Low", "status": "Reported", "priority_score": 30, "priority_level": "Low",
            "photo_path": "uploads/safety1.jpg", "is_duplicate": False, "duplicate_suggestion": "",
            "complaint_id": "CC-1006"
        },
        {
            "user_id": 2, "title": "Illegal Dumping at Empty Plot", "category": "Garbage & Sanitation",
            "description": "Multiple bags of garbage dumped at empty plot on 5th Street.",
            "latitude": 40.7400, "longitude": -74.0200, "location_name": "Empty Plot, 5th Street & Main St",
            "severity": "Medium", "status": "Reported", "priority_score": 40, "priority_level": "Medium",
            "photo_path": "uploads/garbage2.jpg", "is_duplicate": True,
            "duplicate_suggestion": "CC-1003 - Garbage Accumulation Near School Zone by John Doe",
            "complaint_id": "CC-1007"
        },
        {
            "user_id": 1, "title": "Streetlight Out on Pine Street", "category": "Streetlight",
            "description": "Streetlight near intersection is flickering and not working.",
            "latitude": 40.7150, "longitude": -74.0120, "location_name": "Pine Street near 100 Main St",
            "severity": "Low", "status": "In Progress", "priority_score": 35, "priority_level": "Low",
            "photo_path": "uploads/streetlight2.jpg", "is_duplicate": True,
            "duplicate_suggestion": "CC-1002 - Broken Streetlight on Oak Avenue by Jane Smith",
            "complaint_id": "CC-1008"
        },
        {
            "user_id": 3, "title": "Waterlogged Road After Rain", "category": "Drainage",
            "description": "Road flooded near intersection due to heavy rain.",
            "latitude": 40.7220, "longitude": -74.0050, "location_name": "Intersection of Main & 2nd Street",
            "severity": "High", "status": "Verified", "priority_score": 70, "priority_level": "High",
            "photo_path": "uploads/flood1.jpg", "is_duplicate": False, "duplicate_suggestion": "",
            "complaint_id": "CC-1009"
        },
    ]

    for issue in issues:
        existing = db.query(Issue).filter(Issue.complaint_id == issue["complaint_id"]).first()
        if not existing:
            new_issue = Issue(**issue)
            db.add(new_issue)
    # Add issue updates
    updates = [
        {"issue_id": 4, "action": "Status Changed", "details": "Issue marked as Resolved by Admin", "admin_id": 1},
        {"issue_id": 3, "action": "Status Changed", "details": "Issue Verified by Admin", "admin_id": 1},
        {"issue_id": 3, "action": "Status Changed", "details": "Issue Assigned to Sanitation Department", "admin_id": 1},
        {"issue_id": 2, "action": "Status Changed", "details": "Issue Verified by Admin", "admin_id": 1},
        {"issue_id": 2, "action": "Status Changed", "details": "Issue Assigned to Electrical Department", "admin_id": 1},
        {"issue_id": 5, "action": "Status Changed", "details": "Issue Verified by Admin", "admin_id": 1},
        {"issue_id": 5, "action": "Status Changed", "details": "Issue Assigned to Drainage Department", "admin_id": 1},
    ]

    for upd in updates:
        new_update = IssueUpdate(
            issue_id=upd["issue_id"],
            action=upd["action"],
            details=upd["details"],
            admin_id=upd["admin_id"]
        )
        db.add(new_update)

    # Add citizen feedback
    feedback = [
        {"issue_id": 4, "user_id": 1, "feedback_type": "Resolved", "comments": "Thank you, the issue is fixed!"},
        {"issue_id": 9, "user_id": 4, "feedback_type": "Not Resolved", "comments": "Still flooded after 2 days"},
        {"issue_id": 6, "user_id": 2, "feedback_type": "Resolved", "comments": "Bench is now fixed"},
    ]

    for fb in feedback:
        new_fb = CitizenFeedback(
            issue_id=fb["issue_id"],
            user_id=fb["user_id"],
            feedback_type=fb["feedback_type"],
            comments=fb["comments"]
        )
        db.add(new_fb)

    # Add notifications
    notifications = [
        {"user_id": 1, "title": "New Complaint", "message": "Complaint CC-1001 submitted for review"},
        {"user_id": 2, "title": "Complaint Verified", "message": "Your complaint CC-1002 has been verified"},
        {"user_id": 3, "title": "Complaint Assigned", "message": "Complaint CC-1004 assigned to Water Department"},
        {"user_id": 1, "title": "Complaint Resolved", "message": "CC-1001 has been resolved"},
        {"user_id": 1, "title": "Resolution Confirmed", "message": "Your complaint CC-1001 is confirmed resolved"},
    ]

    for notif in notifications:
        new_notif = Notification(
            user_id=notif["user_id"],
            title=notif["title"],
            message=notif["message"]
        )
        db.add(new_notif)

    db.commit()
    db.close()
    print("Demo data inserted successfully.")
''')
print("database.py written")


if __name__ == "__main__":
    print("Backend setup complete. database.py has been generated.")