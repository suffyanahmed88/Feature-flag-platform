from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.auth.security import create_token, current_user, hash_password, key_hash, make_api_key, verify_password
from app.core.config import get_settings
from app.core.database import Base, engine, get_db
from app.evaluation.engine import evaluate
from app.models.models import ApiKey, AuditLog, Environment, FeatureFlag, FlagRule, Project, User
from app.schemas.schemas import *

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    yield
app=FastAPI(title="Feature Flag Platform API", version="1.0.0", description="A focused feature flag management API.", lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=get_settings().cors_origins.split(","),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
def audit(db,project_id,actor,action,detail={}): db.add(AuditLog(project_id=project_id,actor_id=actor,action=action,detail=detail))
def owned_project(db,pid,user):
 p=db.get(Project,pid)
 if not p or p.owner_id!=user.id: raise HTTPException(404,"Project not found")
 return p
def owned_env(db,eid,user):
 env=db.get(Environment,eid)
 if not env or env.project.owner_id!=user.id: raise HTTPException(404,"Environment not found")
 return env
def owned_flag(db,fid,user):
 f=db.get(FeatureFlag,fid)
 if not f or f.environment.project.owner_id!=user.id: raise HTTPException(404,"Flag not found")
 return f
@app.post("/api/v1/auth/register",response_model=Token,status_code=201,tags=["auth"])
def register(body:UserRegister,db:Session=Depends(get_db)):
 if db.scalar(select(User).where(User.email==body.email)): raise HTTPException(409,"Email already registered")
 u=User(email=body.email,name=body.name,password_hash=hash_password(body.password)); db.add(u); db.commit(); return Token(access_token=create_token(u.id))
@app.post("/api/v1/auth/login",response_model=Token,tags=["auth"])
def login(body:Login,db:Session=Depends(get_db)):
 u=db.scalar(select(User).where(User.email==body.email))
 if not u or not verify_password(body.password,u.password_hash): raise HTTPException(401,"Invalid email or password")
 return Token(access_token=create_token(u.id))
@app.get("/api/v1/projects",response_model=list[ProjectOut],tags=["projects"])
def list_projects(user:User=Depends(current_user),db:Session=Depends(get_db)): return db.scalars(select(Project).where(Project.owner_id==user.id).order_by(Project.created_at.desc())).all()
@app.post("/api/v1/projects",response_model=ProjectOut,status_code=201,tags=["projects"])
def create_project(body:ProjectIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 p=Project(**body.model_dump(),owner_id=user.id); db.add(p); db.flush(); audit(db,p.id,user.id,"project.created",{"name":p.name}); db.commit(); db.refresh(p); return p
@app.get("/api/v1/projects/{project_id}/environments",response_model=list[EnvironmentOut],tags=["environments"])
def list_envs(project_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)): return owned_project(db,project_id,user).environments
@app.post("/api/v1/projects/{project_id}/environments",response_model=EnvironmentOut,status_code=201,tags=["environments"])
def create_env(project_id:str,body:EnvironmentIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 owned_project(db,project_id,user); e=Environment(project_id=project_id,**body.model_dump()); db.add(e)
 try: db.commit()
 except Exception: db.rollback(); raise HTTPException(409,"Environment key already exists in this project")
 return e
@app.get("/api/v1/environments/{environment_id}/flags",response_model=list[FlagOut],tags=["flags"])
def list_flags(environment_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 owned_env(db,environment_id,user); return db.scalars(select(FeatureFlag).options(selectinload(FeatureFlag.rules)).where(FeatureFlag.environment_id==environment_id)).all()
@app.post("/api/v1/environments/{environment_id}/flags",response_model=FlagOut,status_code=201,tags=["flags"])
def create_flag(environment_id:str,body:FlagIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 e=owned_env(db,environment_id,user); f=FeatureFlag(environment_id=e.id,**body.model_dump()); db.add(f); db.flush(); audit(db,e.project_id,user.id,"flag.created",{"key":f.key});
 try: db.commit()
 except Exception: db.rollback(); raise HTTPException(409,"Flag key already exists in this environment")
 db.refresh(f); return f
@app.patch("/api/v1/flags/{flag_id}",response_model=FlagOut,tags=["flags"])
def update_flag(flag_id:str,body:FlagUpdate,user:User=Depends(current_user),db:Session=Depends(get_db)):
 f=owned_flag(db,flag_id,user)
 for k,v in body.model_dump(exclude_none=True).items(): setattr(f,k,v)
 audit(db,f.environment.project_id,user.id,"flag.updated",{"key":f.key}); db.commit(); db.refresh(f); return f
@app.delete("/api/v1/flags/{flag_id}",status_code=204,tags=["flags"])
def delete_flag(flag_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 f=owned_flag(db,flag_id,user); db.delete(f); db.commit()
@app.post("/api/v1/flags/{flag_id}/rules",response_model=RuleOut,status_code=201,tags=["rules"])
def create_rule(flag_id:str,body:RuleIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 f=owned_flag(db,flag_id,user); r=FlagRule(flag_id=f.id,**body.model_dump()); db.add(r); audit(db,f.environment.project_id,user.id,"rule.created",{"key":f.key}); db.commit(); db.refresh(r); return r
@app.delete("/api/v1/rules/{rule_id}",status_code=204,tags=["rules"])
def delete_rule(rule_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 r=db.get(FlagRule,rule_id)
 if not r or r.flag.environment.project.owner_id!=user.id: raise HTTPException(404,"Rule not found")
 db.delete(r); db.commit()
@app.get("/api/v1/environments/{environment_id}/keys",response_model=list[ApiKeyOut],tags=["api keys"])
def list_keys(environment_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)): return owned_env(db,environment_id,user).api_keys
@app.post("/api/v1/environments/{environment_id}/keys",response_model=ApiKeyCreated,status_code=201,tags=["api keys"])
def create_key(environment_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 e=owned_env(db,environment_id,user); raw,h=make_api_key(e.key); k=ApiKey(environment_id=e.id,key_hash=h,prefix=raw[:16]); db.add(k); audit(db,e.project_id,user.id,"api_key.generated",{"environment":e.key}); db.commit(); db.refresh(k); return ApiKeyCreated(id=k.id,prefix=k.prefix,created_at=k.created_at,revoked=k.revoked,key=raw)
@app.delete("/api/v1/keys/{key_id}",status_code=204,tags=["api keys"])
def revoke_key(key_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 k=db.get(ApiKey,key_id)
 if not k or k.environment.project.owner_id!=user.id: raise HTTPException(404,"API key not found")
 k.revoked=True; db.commit()
@app.get("/api/v1/projects/{project_id}/audit",tags=["audit"])
def logs(project_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 owned_project(db,project_id,user); return db.scalars(select(AuditLog).where(AuditLog.project_id==project_id).order_by(AuditLog.created_at.desc()).limit(50)).all()
@app.post("/api/v1/evaluate",response_model=EvaluateOut,tags=["evaluation"])
def evaluate_flag(body:EvaluateIn,x_api_key:str=Header(...,description="Environment API key"),db:Session=Depends(get_db)):
 """Evaluate a flag with an environment-scoped API key."""
 api_key=db.scalar(select(ApiKey).where(ApiKey.key_hash==key_hash(x_api_key),ApiKey.revoked==False))
 if not api_key or api_key.environment.key != body.environment_key: raise HTTPException(401,"Invalid environment API key")
 f=db.scalar(select(FeatureFlag).options(selectinload(FeatureFlag.rules)).join(Environment).where(Environment.key==body.environment_key,FeatureFlag.key==body.flag_key))
 if not f: raise HTTPException(404,"Flag not found")
 result=evaluate(f,body.user.model_dump() if body.user else None); return EvaluateOut(flag_key=f.key,enabled=result.enabled,reason=result.reason)
@app.get("/health")
def health(): return {"status":"ok"}
