from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
class UserRegister(BaseModel): email: EmailStr; password: str=Field(min_length=8); name: str=Field(min_length=2,max_length=120)
class Login(BaseModel): email: EmailStr; password: str
class Token(BaseModel): access_token: str; token_type: str="bearer"
class ProjectIn(BaseModel): name: str=Field(min_length=2,max_length=120); description: str|None=None
class EnvironmentIn(BaseModel): name: str; key: str=Field(pattern=r"^[a-z0-9_-]+$")
class RuleIn(BaseModel): attribute: str=Field(pattern=r"^(user_id|email|country|plan)$"); operator: str=Field(pattern=r"^(equals|not_equals)$"); value: str; enabled_value: bool=True
class FlagIn(BaseModel): key: str=Field(pattern=r"^[a-z][a-z0-9_]*$"); name: str; description: str|None=None; enabled: bool=False; default_value: bool=False; rollout_percentage: int=Field(default=0, ge=0,le=100)
class FlagUpdate(BaseModel): name: str|None=None; description: str|None=None; enabled: bool|None=None; default_value: bool|None=None; rollout_percentage: int|None=Field(default=None,ge=0,le=100)
class UserContext(BaseModel): id: str|None=None; email: str|None=None; country: str|None=None; plan: str|None=None
class EvaluateIn(BaseModel): environment_key: str; flag_key: str; user: UserContext|None=None
class EvaluateOut(BaseModel): flag_key: str; enabled: bool; reason: str
class ORM(BaseModel): model_config=ConfigDict(from_attributes=True)
class ProjectOut(ORM): id:str; name:str; description:str|None; created_at:datetime
class EnvironmentOut(ORM): id:str; name:str; key:str; created_at:datetime
class RuleOut(ORM): id:str; attribute:str; operator:str; value:str; enabled_value:bool
class FlagOut(ORM): id:str; key:str; name:str; description:str|None; enabled:bool; default_value:bool; rollout_percentage:int; environment_id:str; created_at:datetime; updated_at:datetime; rules:list[RuleOut]=[]
class ApiKeyOut(BaseModel): id:str; prefix:str; created_at:datetime; revoked:bool
class ApiKeyCreated(ApiKeyOut): key:str
