def get_rank_from_xp(xp):
    if xp < 500:
        return "Cadete"
    if xp < 1500:
        return "Oficial"
    if xp < 3000:
        return "Tenente"
    if xp < 6000:
        return "Capitão"
    return "Comandante"
