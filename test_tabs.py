from src.user.profile_manager import get_full_profile
from src.user.dashboard import _tab_sky, _tab_catalog, _tab_missions, _tab_settings

profile = get_full_profile(2) # comandante has user_id = 2
print("Profile:", profile)

try:
    print("Testing tab_sky...")
    res = _tab_sky(profile)
    print("tab_sky OK!")
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    print("Testing tab_catalog...")
    res = _tab_catalog(profile)
    print("tab_catalog OK!")
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    print("Testing tab_missions...")
    res = _tab_missions(profile)
    print("tab_missions OK!")
except Exception as e:
    import traceback
    traceback.print_exc()
    
try:
    print("Testing tab_settings...")
    res = _tab_settings(profile)
    print("tab_settings OK!")
except Exception as e:
    import traceback
    traceback.print_exc()
