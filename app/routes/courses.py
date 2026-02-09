from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.course import Course
from app.models.user import User
from app.schemas.courses import CourseRead, CourseCreate, CourseUpdate
from app.schemas.enroll import UserEnroll

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=list[CourseRead])
def get_all(
    db: Session = Depends(get_db),
) -> list[CourseRead]:
    return db.query(Course).all()


@router.post("/", response_model=CourseCreate)
def create(
    payload: CourseCreate,
    db: Session = Depends(get_db),
) -> CourseCreate:
    course = Course(
        title=payload.title,
        description=payload.description,
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


@router.post("/enroll", response_model=CourseRead)
def add_user(
    payload: UserEnroll,
    db: Session = Depends(get_db),
) -> CourseRead:
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    course = db.query(Course).get(id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if len(user.courses) >= 5:
        raise HTTPException(
            status_code=400, detail="User can`t have more than 5 courses"
        )
    if len(course.users) >= 20:
        raise HTTPException(
            status_code=400, detail="Course can`t have more than 20 courses"
        )
    user.courses.appen(course)
    db.commit()
    db.refresh(user)
    return course


@router.get("/{id}", response_model=CourseRead)
def get_by_id(
    id: int,
    db: Session = Depends(get_db),
) -> CourseRead:
    course = db.query(Course).get(id)

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return course


@router.patch("/{id}", response_model=CourseRead)
def update(
    id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
) -> CourseRead:
    course = db.query(Course).get(id)

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)

    return course


@router.delete("/{id}")
def delete(
    id: int,
    db: Session = Depends(get_db),
) -> dict:
    course = db.query(Course).get(id)

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()

    return {"detail": "Course deleted"}
