def compute_stats(telemetry_rows):
    if not telemetry_rows:
        return {
            "total_points": 0,
            "avg_altitude": 0,
            "avg_velocity": 0
        }

    total = len(telemetry_rows)
    avg_alt = sum(r["altitude"] for r in telemetry_rows) / total
    avg_vel = sum(r["velocity"] for r in telemetry_rows) / total

    return {
        "total_points": total,
        "avg_altitude": round(avg_alt, 2),
        "avg_velocity": round(avg_vel, 2)
    }
