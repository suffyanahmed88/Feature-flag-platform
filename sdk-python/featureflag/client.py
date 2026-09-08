from typing import Any
import httpx
class FeatureFlagError(Exception): pass
class FeatureFlagClient:
    def __init__(self,api_key:str,base_url:str="http://localhost:8000",timeout:float=5.0):
        self.api_key=api_key; self.base_url=base_url.rstrip("/"); self.timeout=timeout
    def is_enabled(self,flag_key:str,user_id:str|None=None,user:dict[str,Any]|None=None,default:bool=False)->bool:
        context=dict(user or {})
        if user_id: context["id"]=user_id
        # Environment is encoded in ff_<environment>_<secret> keys.
        parts=self.api_key.split("_",2)
        if len(parts)<3: return default
        try:
            r=httpx.post(f"{self.base_url}/api/v1/evaluate",json={"environment_key":parts[1],"flag_key":flag_key,"user":context or None},headers={"X-API-Key":self.api_key},timeout=self.timeout)
            r.raise_for_status(); return bool(r.json()["enabled"])
        except (httpx.HTTPError,KeyError,ValueError) as e:
            return default
