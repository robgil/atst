import datetime
from enum import Enum
import secrets

from sqlalchemy import Column, ForeignKey, Enum as SQLAEnum, TIMESTAMP, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, types
from atst.models.mixins.timestamps import TimestampsMixin


class Status(Enum):
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    PENDING = "pending"
    REJECTED = "rejected"


class Invitation(Base, TimestampsMixin):
    __tablename__ = "invitations"

    id = types.Id()

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    user = relationship("User", backref="invitations", foreign_keys=[user_id])

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), index=True)
    workspace = relationship("Workspace", backref="invitations")

    inviter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    inviter = relationship("User", backref="sent_invites", foreign_keys=[inviter_id])

    status = Column(SQLAEnum(Status, native_enum=False, default=Status.PENDING))

    expiration_time = Column(TIMESTAMP(timezone=True))

    token = Column(String(), index=True, default=lambda: secrets.token_urlsafe())

    def __repr__(self):
        return "<Invitation(user='{}', workspace='{}', id='{}')>".format(
            self.user.id, self.workspace.id, self.id
        )

    @property
    def is_accepted(self):
        return self.status == Status.ACCEPTED

    @property
    def is_revoked(self):
        return self.status == Status.REVOKED

    @property
    def is_pending(self):
        return self.status == Status.PENDING

    @property
    def is_rejected(self):
        return self.status == Status.REJECTED

    @property
    def is_expired(self):
        return datetime.datetime.now(self.expiration_time.tzinfo) > self.expiration_time
