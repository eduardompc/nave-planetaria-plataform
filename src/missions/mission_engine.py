from src.api.missions import add_mission, get_active_missions, update_mission_progress
from src.missions.mission_definitions import get_mission_by_code
from src.user.profile_manager import reward_user

def assign_mission(user_id, mission_code):
    mission_def = get_mission_by_code(mission_code)
    if not mission_def:
        return None

    add_mission(user_id, mission_code, mission_def["name"])
    return mission_def

def list_user_missions(user_id):
    missions = get_active_missions(user_id)
    return [
        {
            "id": m["id"],
            "name": m["mission_name"],
            "status": m["status"],
            "progress": m["progress"]
        }
        for m in missions
    ]

def complete_mission(user_id, mission_id, mission_code):
    mission_def = get_mission_by_code(mission_code)
    if not mission_def:
        return None

    # marca como concluída
    update_mission_progress(mission_id, 100, status="completed")

    # recompensa XP
    profile = reward_user(user_id, mission_def["xp_reward"])
    return {
        "mission": mission_def,
        "profile": profile
    }
