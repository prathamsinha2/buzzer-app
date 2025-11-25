from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import secrets
from app.database import get_db
from app.models.user import User
from app.models.group import Group, GroupMember
from app.schemas.group import GroupCreate, GroupJoin, GroupResponse, MemberResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.post("/create", response_model=GroupResponse)
def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new group."""
    # Generate unique invite code
    invite_code = secrets.token_urlsafe(10)

    # Create group
    group = Group(
        name=group_data.name,
        owner_id=current_user.id,
        invite_code=invite_code
    )
    db.add(group)
    db.flush()

    # Add owner as member
    member = GroupMember(
        group_id=group.id,
        user_id=current_user.id,
        role="owner"
    )
    db.add(member)
    db.commit()
    db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        invite_code=group.invite_code,
        owner_id=group.owner_id,
        members=[
            MemberResponse(
                id=current_user.id,
                email=current_user.email,
                full_name=current_user.full_name,
                role="owner"
            )
        ]
    )


@router.post("/join", response_model=GroupResponse)
def join_group(
    data: GroupJoin,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a group using invite code."""
    # Find group by invite code
    group = db.query(Group).filter(Group.invite_code == data.invite_code).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Check if already member
    existing_member = db.query(GroupMember).filter(
        GroupMember.group_id == group.id,
        GroupMember.user_id == current_user.id
    ).first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this group"
        )

    # Add user to group
    member = GroupMember(
        group_id=group.id,
        user_id=current_user.id,
        role="member"
    )
    db.add(member)
    db.commit()
    db.refresh(group)

    # Return group with all members
    members = []
    for gm in group.members:
        members.append(MemberResponse(
            id=gm.user.id,
            email=gm.user.email,
            full_name=gm.user.full_name,
            role=gm.role
        ))

    return GroupResponse(
        id=group.id,
        name=group.name,
        invite_code=group.invite_code,
        owner_id=group.owner_id,
        members=members
    )


@router.get("/", response_model=list[GroupResponse])
def get_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all groups for current user."""
    # Get groups where user is a member
    memberships = db.query(GroupMember).filter(GroupMember.user_id == current_user.id).all()

    groups = []
    for membership in memberships:
        group = membership.group
        members = []
        for gm in group.members:
            members.append(MemberResponse(
                id=gm.user.id,
                email=gm.user.email,
                full_name=gm.user.full_name,
                role=gm.role
            ))

        groups.append(GroupResponse(
            id=group.id,
            name=group.name,
            invite_code=group.invite_code,
            owner_id=group.owner_id,
            members=members
        ))

    return groups


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Check if user is member
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group.id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    members = []
    for gm in group.members:
        members.append(MemberResponse(
            id=gm.user.id,
            email=gm.user.email,
            full_name=gm.user.full_name,
            role=gm.role
        ))

    return GroupResponse(
        id=group.id,
        name=group.name,
        invite_code=group.invite_code,
        owner_id=group.owner_id,
        members=members
    )


@router.post("/{group_id}/leave")
def leave_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Check if owner - can't leave own group
    if group.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner cannot leave group"
        )

    # Find and delete membership
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group.id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a member of this group"
        )

    db.delete(membership)
    db.commit()

    return {"message": "Left group successfully"}
