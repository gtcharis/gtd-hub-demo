from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import User, CommunityDiscussion, CommunityReply
from app.auth_dependencies import require_permission
from app.schemas.community import DiscussionCreate, ReplyCreate, DiscussionUpdate, ModerationUpdate
router = APIRouter(prefix="/community", tags=["community"])
def scoped(query, user):
    if user.role != "Programme Administrator":
        if user.institution_id is None: raise HTTPException(403, "Institution scope is not assigned")
        query = query.filter(CommunityDiscussion.institution_id == user.institution_id)
    return query
def discussion_out(d, user_id=None):
    return {"id":d.id,"title":d.title,"category":d.category,"body":d.body,"status":d.status,"author_user_id":d.author_user_id,"author_name":d.author.full_name,"institution_id":d.institution_id,"institution_name":d.institution.name,"created_at":d.created_at,"updated_at":d.updated_at,"reply_count":sum(1 for r in d.replies if r.status == "visible"),"replies":[{"id":r.id,"author_user_id":r.author_user_id,"author_name":r.author.full_name,"body":r.body,"status":r.status,"created_at":r.created_at} for r in d.replies if r.status == "visible"]}
def load_query(db): return db.query(CommunityDiscussion).options(joinedload(CommunityDiscussion.author),joinedload(CommunityDiscussion.institution),joinedload(CommunityDiscussion.replies).joinedload(CommunityReply.author))
@router.get("/discussions")
def list_discussions(q:str=Query(default="",max_length=120),category:str=Query(default="",max_length=80),user:User=Depends(require_permission("community:read")),db:Session=Depends(get_db)):
    query=scoped(load_query(db),user).filter(CommunityDiscussion.status != "hidden")
    rows=query.order_by(CommunityDiscussion.updated_at.desc()).all(); q=q.strip().casefold(); category=category.strip().casefold()
    return [discussion_out(d,user.id) for d in rows if (not q or q in (d.title+" "+d.body+" "+d.author.full_name).casefold()) and (not category or category==d.category.casefold())]
@router.post("/discussions",status_code=201)
def create_discussion(payload:DiscussionCreate,user:User=Depends(require_permission("community:create")),db:Session=Depends(get_db)):
    if user.institution_id is None: raise HTTPException(403,"Institution scope is not assigned")
    d=CommunityDiscussion(institution_id=user.institution_id,author_user_id=user.id,title=payload.title.strip(),category=payload.category.strip(),body=payload.body.strip(),status="open",created_at=datetime.now(timezone.utc),updated_at=datetime.now(timezone.utc)); db.add(d); db.commit(); d=load_query(db).filter(CommunityDiscussion.id==d.id).one(); return discussion_out(d,user.id)
@router.patch("/discussions/{discussion_id}")
def update_discussion(discussion_id:int,payload:DiscussionUpdate,user:User=Depends(require_permission("community:manage_own")),db:Session=Depends(get_db)):
    d=scoped(load_query(db),user).filter(CommunityDiscussion.id==discussion_id).first()
    if d is None: raise HTTPException(404,"Discussion not found")
    if d.author_user_id!=user.id and user.role!="Programme Administrator": raise HTTPException(403,"You can only edit your own discussion")
    for key,value in payload.model_dump(exclude_unset=True).items():
        if value is not None: setattr(d,key,value.strip())
    d.updated_at=datetime.now(timezone.utc); db.commit(); d=load_query(db).filter(CommunityDiscussion.id==d.id).one(); return discussion_out(d,user.id)
@router.post("/discussions/{discussion_id}/replies",status_code=201)
def create_reply(discussion_id:int,payload:ReplyCreate,user:User=Depends(require_permission("community:create")),db:Session=Depends(get_db)):
    d=scoped(db.query(CommunityDiscussion),user).filter(CommunityDiscussion.id==discussion_id).first()
    if d is None: raise HTTPException(404,"Discussion not found")
    if d.status!="open": raise HTTPException(409,"This discussion is not open for replies")
    now=datetime.now(timezone.utc); r=CommunityReply(discussion_id=d.id,author_user_id=user.id,body=payload.body.strip(),status="visible",created_at=now,updated_at=now); d.updated_at=now; db.add(r); db.commit(); return {"id":r.id,"discussion_id":d.id,"author_user_id":user.id,"author_name":user.full_name,"body":r.body,"status":r.status,"created_at":r.created_at}
@router.patch("/replies/{reply_id}")
def update_reply(reply_id:int,payload:ReplyCreate,user:User=Depends(require_permission("community:manage_own")),db:Session=Depends(get_db)):
    r=db.query(CommunityReply).join(CommunityDiscussion).filter(CommunityReply.id==reply_id).first()
    if r is None: raise HTTPException(404,"Reply not found")
    if user.role != "Programme Administrator" and r.discussion.institution_id != user.institution_id: raise HTTPException(404,"Reply not found")
    if r.author_user_id!=user.id and user.role!="Programme Administrator": raise HTTPException(403,"You can only edit your own reply")
    r.body=payload.body.strip(); r.updated_at=datetime.now(timezone.utc); db.commit(); return {"id":r.id,"body":r.body,"status":r.status}
@router.patch("/discussions/{discussion_id}/moderation")
def moderate_discussion(discussion_id:int,payload:ModerationUpdate,user:User=Depends(require_permission("community:moderate")),db:Session=Depends(get_db)):
    d=scoped(db.query(CommunityDiscussion),user).filter(CommunityDiscussion.id==discussion_id).first()
    if d is None: raise HTTPException(404,"Discussion not found")
    d.status=payload.status; d.updated_at=datetime.now(timezone.utc); db.commit(); return {"id":d.id,"status":d.status}
@router.patch("/replies/{reply_id}/moderation")
def moderate_reply(reply_id:int,payload:ModerationUpdate,user:User=Depends(require_permission("community:moderate")),db:Session=Depends(get_db)):
    r=db.query(CommunityReply).join(CommunityDiscussion).filter(CommunityReply.id==reply_id).first()
    if r is None: raise HTTPException(404,"Reply not found")
    d=db.query(CommunityDiscussion).filter(CommunityDiscussion.id==r.discussion_id).first()
    if user.role!="Programme Administrator" and d.institution_id!=user.institution_id: raise HTTPException(404,"Reply not found")
    r.status="hidden" if payload.status=="hidden" else "visible"; r.updated_at=datetime.now(timezone.utc); db.commit(); return {"id":r.id,"status":r.status}
