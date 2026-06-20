from .core import generate_ai_briefing

def on_cockpit_open():
    return generate_ai_briefing()

def on_mission_tab_open():
    return generate_ai_briefing()
