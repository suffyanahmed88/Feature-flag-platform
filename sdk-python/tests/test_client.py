from featureflag import FeatureFlagClient
def test_invalid_key_falls_back(): assert FeatureFlagClient("bad").is_enabled("flag",default=True) is True
