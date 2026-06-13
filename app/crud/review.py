from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.review import Review, ReviewFrame, ReviewComment
from app.models.users import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewFrameCreate, ReviewFrameUpdate, ReviewCommentCreate
from fastapi import HTTPException, status

class CRUDReview:
    
    def _get_name(self, db: Session, user_id: int):
        u = db.query(User).filter(User.id == user_id).first()
        if not u: return "Unknown"
        return u.first_name or u.email

    def get_by_version(self, db: Session, version_id: int):
        reviews = db.query(Review).filter(Review.version_id == version_id).order_by(desc(Review.created_at)).all()
        for r in reviews:
            r.creator_name = self._get_name(db, r.created_by)
            for f in r.frames:
                f.creator_name = self._get_name(db, f.created_by)
                for c in f.comments:
                    c.creator_name = self._get_name(db, c.created_by)
            for c in r.comments:
                c.creator_name = self._get_name(db, c.created_by)
        return reviews

    def get(self, db: Session, review_id: int):
        review = db.query(Review).filter(Review.id == review_id).first()
        if review:
            review.creator_name = self._get_name(db, review.created_by)
            for f in review.frames:
                f.creator_name = self._get_name(db, f.created_by)
                for c in f.comments:
                    c.creator_name = self._get_name(db, c.created_by)
            for c in review.comments:
                c.creator_name = self._get_name(db, c.created_by)
        return review

    def create(self, db: Session, obj_in: ReviewCreate, user_id: int):
        db_obj = Review(
            version_id=obj_in.version_id,
            created_by=user_id,
            status=obj_in.status if obj_in.status and obj_in.status != 'pending' else 'draft'
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return self.get(db, db_obj.id)

    def update(self, db: Session, review_id: int, obj_in: ReviewUpdate):
        db_obj = db.query(Review).filter(Review.id == review_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Review not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return self.get(db, db_obj.id)
        
    def add_frame(self, db: Session, review_id: int, obj_in: ReviewFrameCreate, user_id: int):
        db_obj = ReviewFrame(
            review_id=review_id,
            media_type=obj_in.media_type,
            timecode=obj_in.timecode,
            annotation_data=obj_in.annotation_data,
            description=obj_in.description,
            image_data=obj_in.image_data,
            created_by=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_frame(self, db: Session, frame_id: int, obj_in: ReviewFrameUpdate):
        db_obj = db.query(ReviewFrame).filter(ReviewFrame.id == frame_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Review frame not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_frame(self, db: Session, frame_id: int):
        db_obj = db.query(ReviewFrame).filter(ReviewFrame.id == frame_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return True

    def add_comment(self, db: Session, review_id: int, frame_id: int | None, obj_in: ReviewCommentCreate, user_id: int):
        db_obj = ReviewComment(
            review_id=review_id,
            review_frame_id=frame_id,
            parent_comment_id=obj_in.parent_comment_id,
            comment=obj_in.comment,
            created_by=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

review = CRUDReview()
