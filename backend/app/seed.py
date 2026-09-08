from app.core.database import Base,SessionLocal,engine
from app.auth.security import hash_password
from app.models.models import User,Project,Environment,FeatureFlag,FlagRule
def run():
 Base.metadata.create_all(engine); db=SessionLocal()
 if db.query(User).filter_by(email="demo@featureflags.local").first(): return print("Seed already exists")
 u=User(email="demo@featureflags.local",name="Demo User",password_hash=hash_password("demo-password")); db.add(u); db.flush(); p=Project(name="E-Commerce",description="Demo storefront",owner_id=u.id); db.add(p); db.flush()
 envs={}
 for name,key in [("Development","development"),("Staging","staging"),("Production","production")]: envs[key]=Environment(project_id=p.id,name=name,key=key); db.add(envs[key])
 db.flush(); a=FeatureFlag(environment_id=envs["production"].id,key="new_checkout",name="New Checkout",enabled=True,default_value=False,rollout_percentage=25); d=FeatureFlag(environment_id=envs["production"].id,key="dark_mode",name="Dark Mode",enabled=False); r=FeatureFlag(environment_id=envs["production"].id,key="ai_recommendations",name="AI Recommendations",enabled=True,default_value=False); db.add_all([a,d,r]); db.flush(); db.add(FlagRule(flag_id=r.id,attribute="plan",operator="equals",value="premium",enabled_value=True)); db.commit(); print("Seeded demo@featureflags.local / demo-password")
if __name__=="__main__": run()
