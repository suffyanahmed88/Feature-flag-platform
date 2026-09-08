import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def uid(): return str(uuid.uuid4())
class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
class User(Base, Timestamped):
    __tablename__="users"; id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); email: Mapped[str]=mapped_column(String(255), unique=True, index=True); password_hash: Mapped[str]=mapped_column(String(255)); name: Mapped[str]=mapped_column(String(120)); projects=relationship("Project", back_populates="owner")
class Project(Base, Timestamped):
    __tablename__="projects"; id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); name: Mapped[str]=mapped_column(String(120)); description: Mapped[str|None]=mapped_column(Text, nullable=True); owner_id: Mapped[str]=mapped_column(ForeignKey("users.id"), index=True); owner=relationship("User", back_populates="projects"); environments=relationship("Environment", back_populates="project", cascade="all, delete-orphan")
class Environment(Base, Timestamped):
    __tablename__="environments"; __table_args__=(UniqueConstraint("project_id","key"),); id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); project_id: Mapped[str]=mapped_column(ForeignKey("projects.id")); name: Mapped[str]=mapped_column(String(120)); key: Mapped[str]=mapped_column(String(80), index=True); project=relationship("Project", back_populates="environments"); flags=relationship("FeatureFlag", back_populates="environment", cascade="all, delete-orphan"); api_keys=relationship("ApiKey", back_populates="environment", cascade="all, delete-orphan")
class FeatureFlag(Base, Timestamped):
    __tablename__="feature_flags"; __table_args__=(UniqueConstraint("environment_id","key"),); id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); environment_id: Mapped[str]=mapped_column(ForeignKey("environments.id"), index=True); key: Mapped[str]=mapped_column(String(120)); name: Mapped[str]=mapped_column(String(120)); description: Mapped[str|None]=mapped_column(Text, nullable=True); enabled: Mapped[bool]=mapped_column(Boolean, default=False); default_value: Mapped[bool]=mapped_column(Boolean, default=False); rollout_percentage: Mapped[int]=mapped_column(Integer, default=0); environment=relationship("Environment", back_populates="flags"); rules=relationship("FlagRule", back_populates="flag", cascade="all, delete-orphan")
class FlagRule(Base, Timestamped):
    __tablename__="flag_rules"; id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); flag_id: Mapped[str]=mapped_column(ForeignKey("feature_flags.id"), index=True); attribute: Mapped[str]=mapped_column(String(32)); operator: Mapped[str]=mapped_column(String(20)); value: Mapped[str]=mapped_column(String(255)); enabled_value: Mapped[bool]=mapped_column(Boolean, default=True); flag=relationship("FeatureFlag", back_populates="rules")
class ApiKey(Base, Timestamped):
    __tablename__="api_keys"; id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); environment_id: Mapped[str]=mapped_column(ForeignKey("environments.id"), index=True); key_hash: Mapped[str]=mapped_column(String(64), unique=True); prefix: Mapped[str]=mapped_column(String(20)); revoked: Mapped[bool]=mapped_column(Boolean, default=False); environment=relationship("Environment", back_populates="api_keys")
class AuditLog(Base):
    __tablename__="audit_logs"; id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); project_id: Mapped[str]=mapped_column(ForeignKey("projects.id"), index=True); actor_id: Mapped[str|None]=mapped_column(ForeignKey("users.id"), nullable=True); action: Mapped[str]=mapped_column(String(120)); detail: Mapped[dict]=mapped_column(JSON, default=dict); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())
