import enum
import uuid
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app import db


class UserRole(enum.Enum):
    field_executive = "field_executive"
    field_manager = "field_manager"
    senior_manager = "senior_manager"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole, native_enum=False), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    manager_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)
    login_failures = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime(timezone=True), nullable=True)

    manager = db.relationship("User", remote_side=[id], backref="subordinates")

    def set_password(self, password):
        from werkzeug.security import generate_password_hash

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash

        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        return self.role == role

    def is_senior_manager(self):
        return self.role == UserRole.senior_manager

    def is_field_manager(self):
        return self.role == UserRole.field_manager

    def can_view_farmer(self, farmer):
        if self.is_senior_manager():
            return True
        if self.is_field_manager():
            return farmer.created_by in {u.id for u in self.subordinates}
        return farmer.created_by == self.id

    def can_view_implementation(self, implementation):
        if self.is_senior_manager():
            return True
        if self.is_field_manager():
            return implementation.created_by in {u.id for u in self.subordinates}
        return implementation.created_by == self.id

    def user_scope_ids(self):
        if self.is_senior_manager():
            return None
        if self.is_field_manager():
            return [user.id for user in self.subordinates]
        return [self.id]


class Farmer(db.Model):
    __tablename__ = "farmers"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    village = db.Column(db.String(120), nullable=True)
    district = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    land_area_ha = db.Column(db.Float, nullable=True)
    gps_lat = db.Column(db.Float, nullable=True)
    gps_lng = db.Column(db.Float, nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now(), default=func.now())

    created_by_user = db.relationship("User", foreign_keys=[created_by], backref="farmers_created")


class Implementation(db.Model):
    __tablename__ = "implementations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)
    activity_type = db.Column(db.String(80), nullable=False)
    species_planted = db.Column(db.String(120), nullable=True)
    number_of_saplings = db.Column(db.Integer, nullable=True)
    date_of_activity = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="planned")
    photo_url = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now(), default=func.now())

    farmer = db.relationship("Farmer", backref="implementations")
    created_by_user = db.relationship("User", foreign_keys=[created_by], backref="implementations_created")


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(30), nullable=False)
    table_name = db.Column(db.String(80), nullable=False)
    record_id = db.Column(db.String(36), nullable=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    details = db.Column(JSONB, nullable=True)

    user = db.relationship("User", backref="audit_logs")


def log_audit(action, table_name, record_id, user_id, details=None):
    from app import db

    log = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        details=details or {},
    )
    db.session.add(log)
    db.session.commit()
