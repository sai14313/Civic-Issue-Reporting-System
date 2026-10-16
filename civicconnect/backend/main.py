"""
CivicConnect - FastAPI Backend
Main application with REST API routes for civic issue reporting.
"""

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import shutil, os, uuid

from database import (
    Base, engine, SessionLocal, get_db,
    User, Department, Issue, IssueSupport, IssueUpdate,
    CitizenFeedback, Notification, create_tables, insert_demo_data
)

# ==================== APP SETUP ====================
app = FastAPI(title="CivicConnect API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ==================== AUTH CONFIG ====================
SECRET_KEY = "civicconnect-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ==================== AUTH DEPENDENCIES ====================
def get_current_user(db: Session = Depends(get_db), token: str = None):
    from fastapi import Security
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    security = HTTPBearer()
    credentials: HTTPAuthorizationCredentials = security.__call__(None) if False else None
    # Simplified: we'll use a dependency that reads token from request
    return None


async def get_current_user_from_token(
    authorization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get current user from Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user_from_token)):
    return current_user


def get_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ==================== AUTH ROUTES ====================
@app.post("/api/auth/register")
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Register a new citizen user."""
    # Check if email exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate citizen ID
    count = db.query(User).filter(User.role == "citizen").count()
    citizen_id = f"CIT-{count + 1:03d}"

    hashed_password = get_password_hash(password)
    user = User(
        citizen_id=citizen_id,
        name=name,
        email=email,
        password_hash=hashed_password,
        role="citizen",
        phone=phone,
        address=address
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create welcome notification
    notif = Notification(
        user_id=user.id,
        title="Welcome to CivicConnect",
        message="Thank you for registering! Start reporting civic issues in your community."
    )
    db.add(notif)
    db.commit()

    return {"message": "Registration successful", "user_id": user.id, "citizen_id": citizen_id}


@app.post("/api/auth/login")
async def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "citizen_id": user.citizen_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "phone": user.phone,
            "address": user.address,
            "profile_image": user.profile_image
        }
    }
# ==================== ISSUE ROUTES ====================
@app.get("/api/issues")
async def get_issues(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of issues with optional filtering."""
    query = db.query(Issue)
    if status:
        query = query.filter(Issue.status == status)
    if category:
        query = query.filter(Issue.category == category)
    issues = query.offset(skip).limit(limit).all()
    return issues


@app.get("/api/issues/{issue_id}")
async def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a single issue by ID."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@app.post("/api/issues")
async def create_issue(
    title: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_name: str = Form(...),
    severity: str = Form("Medium"),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Report a new civic issue."""
    # Generate complaint ID
    count = db.query(Issue).count()
    complaint_id = f"CC-{1001 + count}"

    # Handle photo upload
    photo_path = ""
    if photo:
        file_ext = os.path.splitext(photo.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join("uploads", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_path = file_path

    # Calculate priority score based on severity
    severity_scores = {"Low": 25, "Medium": 50, "High": 75, "Critical": 95}
    priority_score = severity_scores.get(severity, 50)
    priority_level = severity

    # Check for duplicates (simple location-based)
    existing_issue = db.query(Issue).filter(
        Issue.latitude == latitude,
        Issue.longitude == longitude,
        Issue.is_duplicate == False
    ).first()

    duplicate_suggestion = ""
    is_duplicate = False
    if existing_issue:
        is_duplicate = True
        duplicate_suggestion = f"Possible duplicate: {existing_issue.complaint_id} - {existing_issue.title}"

    issue = Issue(
        complaint_id=complaint_id,
        user_id=current_user.id,
        title=title,
        category=category,
        description=description,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        severity=severity,
        status="Reported",
        priority_score=priority_score,
        priority_level=priority_level,
        photo_path=photo_path,
        is_duplicate=is_duplicate,
        duplicate_suggestion=duplicate_suggestion
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    # Create notification for admins
    admins = db.query(User).filter(User.role == "admin").all()
    for admin in admins:
        notif = Notification(
            user_id=admin.id,
            title="New Issue Reported",
            message=f"New complaint {complaint_id}: {title}"
        )
        db.add(notif)
    db.commit()

    return {
        "message": "Issue reported successfully",
        "complaint_id": complaint_id,
        "issue_id": issue.id,
        "is_duplicate": is_duplicate,
        "duplicate_suggestion": duplicate_suggestion
    }


@app.put("/api/issues/{issue_id}")
async def update_issue(
    issue_id: int,
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    severity: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    department_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an issue (admin or owner)."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Check permissions
    if current_user.role != "admin" and issue.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this issue")

    if title is not None:
        issue.title = title
    if category is not None:
        issue.category = category
    if description is not None:
        issue.description = description
    if severity is not None:
        issue.severity = severity
        severity_scores = {"Low": 25, "Medium": 50, "High": 75, "Critical": 95}
        issue.priority_score = severity_scores.get(severity, 50)
        issue.priority_level = severity
    if status is not None:
        issue.status = status
    if department_id is not None:
        issue.department_id = department_id

    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)

    # Create update record
    update_record = IssueUpdate(
        issue_id=issue.id,
        action="Issue Updated",
        details=f"Issue updated by {current_user.name}",
        admin_id=current_user.id if current_user.role == "admin" else None
    )
    db.add(update_record)
    db.commit()

    return {"message": "Issue updated successfully", "issue": issue}


@app.delete("/api/issues/{issue_id}")
async def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete an issue (admin only)."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(issue)
    db.commit()
    return {"message": "Issue deleted successfully"}
# ==================== UPVOTE/SUPPORT ROUTES ====================
@app.post("/api/issues/{issue_id}/support")
async def support_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upvote/support an issue."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Check if user already supported this issue
    existing = db.query(IssueSupport).filter(
        IssueSupport.issue_id == issue_id,
        IssueSupport.user_id == current_user.id
    ).first()

    if existing:
        existing.support_count += 1
        db.commit()
        return {"message": "Support count updated", "count": existing.support_count}

    support = IssueSupport(
        user_id=current_user.id,
        issue_id=issue_id,
        support_count=1
    )
    db.add(support)
    db.commit()
    db.refresh(support)

    # Boost priority score based on support count
    total_supports = db.query(func.sum(IssueSupport.support_count)).filter(
        IssueSupport.issue_id == issue_id
    ).scalar() or 0
    issue.priority_score = min(100, issue.priority_score + int(total_supports) * 5)
    db.commit()

    return {"message": "Issue supported", "count": support.support_count}


@app.get("/api/issues/{issue_id}/supports")
async def get_issue_supports(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get support count for an issue."""
    total = db.query(func.sum(IssueSupport.support_count)).filter(
        IssueSupport.issue_id == issue_id
    ).scalar() or 0
    return {"issue_id": issue_id, "total_support": int(total)}


# ==================== AI CLASSIFICATION ROUTE ====================
@app.post("/api/ai/classify")
async def ai_classify_image(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mock AI image classification for civic issues."""
    # Save uploaded file temporarily
    file_ext = os.path.splitext(photo.filename)[1]
    filename = f"ai_temp_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join("uploads", filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    # Mock AI classification based on filename keywords or random
    import random
    categories = [
        {"category": "Road & Pothole", "confidence": 0.92, "suggested_severity": "High"},
        {"category": "Streetlight", "confidence": 0.87, "suggested_severity": "Medium"},
        {"category": "Garbage & Sanitation", "confidence": 0.94, "suggested_severity": "Low"},
        {"category": "Water Supply", "confidence": 0.89, "suggested_severity": "Critical"},
        {"category": "Drainage", "confidence": 0.85, "suggested_severity": "High"},
        {"category": "Public Safety", "confidence": 0.81, "suggested_severity": "Low"},
    ]

    # Simple keyword matching from filename
    result = random.choice(categories)
    filename_lower = photo.filename.lower()
    if "pothole" in filename_lower or "road" in filename_lower:
        result = categories[0]
    elif "light" in filename_lower or "streetlight" in filename_lower:
        result = categories[1]
    elif "garbage" in filename_lower or "trash" in filename_lower:
        result = categories[2]
    elif "water" in filename_lower or "leak" in filename_lower:
        result = categories[3]
    elif "drain" in filename_lower or "flood" in filename_lower:
        result = categories[4]

    # Clean up temp file
    try:
        os.remove(file_path)
    except:
        pass

    return {
        "predicted_category": result["category"],
        "confidence": result["confidence"],
        "suggested_severity": result["suggested_severity"],
        "model": "CivicConnect-AI-v1.0 (Demo)",
        "note": "This is a mock AI classification for demonstration purposes"
    }
# ==================== ADMIN ROUTES ====================
@app.get("/api/admin/stats")
async def admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get dashboard statistics for admin."""
    total_issues = db.query(Issue).count()
    total_users = db.query(User).filter(User.role == "citizen").count()
    resolved_issues = db.query(Issue).filter(Issue.status == "Resolved").count()
    in_progress = db.query(Issue).filter(Issue.status == "In Progress").count()
    reported = db.query(Issue).filter(Issue.status == "Reported").count()
    verified = db.query(Issue).filter(Issue.status == "Verified").count()
    duplicates = db.query(Issue).filter(Issue.is_duplicate == True).count()

    # Issues by department
    dept_stats = db.query(
        Department.name,
        func.count(Issue.id)
    ).outerjoin(Issue, Department.id == Issue.department_id).group_by(Department.name).all()

    # Issues by category
    cat_stats = db.query(
        Issue.category,
        func.count(Issue.id)
    ).group_by(Issue.category).all()

    return {
        "total_issues": total_issues,
        "total_users": total_users,
        "resolved_issues": resolved_issues,
        "in_progress": in_progress,
        "reported": reported,
        "verified": verified,
        "duplicates": duplicates,
        "resolution_rate": round((resolved_issues / total_issues * 100) if total_issues > 0 else 0, 1),
        "department_stats": [{"department": d, "count": c} for d, c in dept_stats],
        "category_stats": [{"category": c, "count": n} for c, n in cat_stats]
    }


@app.get("/api/admin/issues")
async def admin_get_all_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all issues for admin management."""
    issues = db.query(Issue).order_by(desc(Issue.created_at)).all()
    return issues


@app.get("/api/admin/users")
async def admin_get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all users for admin management."""
    users = db.query(User).all()
    return users


@app.put("/api/admin/issues/{issue_id}/assign")
async def assign_issue(
    issue_id: int,
    department_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Assign issue to a department."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.department_id = department_id
    issue.status = "Verified"
    issue.updated_at = datetime.utcnow()
    db.commit()

    # Create update record
    update_record = IssueUpdate(
        issue_id=issue.id,
        action="Assigned",
        details=f"Issue assigned to department ID {department_id}",
        admin_id=current_user.id
    )
    db.add(update_record)

    # Notify the issue owner
    notif = Notification(
        user_id=issue.user_id,
        title="Issue Assigned",
        message=f"Your complaint {issue.complaint_id} has been assigned and verified"
    )
    db.add(notif)
    db.commit()

    return {"message": "Issue assigned successfully"}


@app.put("/api/admin/issues/{issue_id}/resolve")
async def resolve_issue(
    issue_id: int,
    resolution_notes: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Mark issue as resolved."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.status = "Resolved"
    issue.updated_at = datetime.utcnow()
    db.commit()

    # Create update record
    update_record = IssueUpdate(
        issue_id=issue.id,
        action="Resolved",
        details=resolution_notes,
        admin_id=current_user.id
    )
    db.add(update_record)

    # Notify the issue owner
    notif = Notification(
        user_id=issue.user_id,
        title="Issue Resolved",
        message=f"Your complaint {issue.complaint_id} has been resolved. {resolution_notes}"
    )
    db.add(notif)
    db.commit()

    return {"message": "Issue resolved successfully"}
# ==================== NOTIFICATION ROUTES ====================
@app.get("/api/notifications")
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notifications for current user."""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(desc(Notification.created_at)).all()
    return notifications


@app.put("/api/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}


# ==================== CITIZEN FEEDBACK ROUTES ====================
@app.post("/api/issues/{issue_id}/feedback")
async def submit_feedback(
    issue_id: int,
    feedback_type: str = Form(...),
    comments: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit feedback on an issue resolution."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    feedback = CitizenFeedback(
        issue_id=issue_id,
        user_id=current_user.id,
        feedback_type=feedback_type,
        comments=comments
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return {"message": "Feedback submitted successfully"}


@app.get("/api/issues/{issue_id}/feedback")
async def get_issue_feedback(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get feedback for an issue."""
    feedback = db.query(CitizenFeedback).filter(
        CitizenFeedback.issue_id == issue_id
    ).all()
    return feedback


# ==================== USER PROFILE ROUTES ====================
@app.get("/api/user/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile."""
    return {
        "id": current_user.id,
        "citizen_id": current_user.citizen_id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "phone": current_user.phone,
        "address": current_user.address,
        "profile_image": current_user.profile_image,
        "created_at": current_user.created_at
    }


@app.get("/api/user/issues")
async def get_user_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get issues reported by current user."""
    issues = db.query(Issue).filter(Issue.user_id == current_user.id).order_by(desc(Issue.created_at)).all()
    return issues
# ==================== STARTUP & ROOT ====================
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    create_tables()
    insert_demo_data()
    print("CivicConnect Backend started successfully!")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CivicConnect API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)