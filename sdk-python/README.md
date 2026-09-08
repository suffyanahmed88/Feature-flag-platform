# FeatureFlag Python SDK

```python
from featureflag import FeatureFlagClient
client = FeatureFlagClient(api_key="ff_production_xxx")
client.is_enabled("new_checkout", user_id="user_123")
client.is_enabled("ai_recommendations", user={"id":"u_123", "plan":"premium"})
```

Requests time out after five seconds by default and safely return `default=False` on network or API errors.
