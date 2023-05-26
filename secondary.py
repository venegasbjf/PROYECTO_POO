from __future__ import annotations

from library import Library

# 76561199104524520 <-- 4 juegos
# 76561199057466527 <-- 52 juegos
# 76561198176695149 <-- 55 juegos
# 76561198121699782 <-- 362 juegos
# 76561198086708374 <-- 733 juegos
# 76561198294650349 <-- 1240 juegos

def secondary():
    
    library = Library("76561198941605330", "EA29ED634385FF016C0B0363F3F23D27", "da02ff927bc9816956aa864cf62ba4ba")
    user_data, games, categories, genres = library.create_user_library()
    

if __name__ == "__secondary__":
    secondary()