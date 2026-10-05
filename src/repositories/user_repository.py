from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from src.repositories.models import UserModel, UserRoleAuditLogModel
from src.domain.entities.user import User, UserRole, UserStatus


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=UserRole(model.role),
            status=UserStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.email == email.lower().strip()).first()
        return self._to_entity(model) if model else None

    def create(self, email: str, password_hash: str, role: str = "CUSTOMER", status: str = "ACTIVE") -> User:
        model = UserModel(
            email=email.lower().strip(),
            password_hash=password_hash,
            role=role,
            status=status,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update_role(self, target_user_id: int, new_role: str, actor_admin_id: int) -> User:
        model = self.db.query(UserModel).filter(UserModel.id == target_user_id).first()
        if not model:
            return None
        prev_role = model.role
        model.role = new_role
        model.updated_at = datetime.now(timezone.utc)

        # AC-02: Create immutable role audit log record
        audit_log = UserRoleAuditLogModel(
            target_user_id=target_user_id,
            actor_admin_id=actor_admin_id,
            previous_role=prev_role,
            new_role=new_role,
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def list_all(self) -> List[User]:
        models = self.db.query(UserModel).all()
        return [self._to_entity(m) for m in models]

    def get_audit_logs(self, target_user_id: Optional[int] = None) -> List[dict]:
        q = self.db.query(UserRoleAuditLogModel)
        if target_user_id:
            q = q.filter(UserRoleAuditLogModel.target_user_id == target_user_id)
        logs = q.order_by(UserRoleAuditLogModel.timestamp.desc()).all()
        return [
            {
                "id": log.id,
                "target_user_id": log.target_user_id,
                "actor_admin_id": log.actor_admin_id,
                "previous_role": log.previous_role,
                "new_role": log.new_role,
                "timestamp": log.timestamp
            }
            for log in logs
        ]
