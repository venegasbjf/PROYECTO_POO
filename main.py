from data import GamesData

# 76561199104524520 <-- 4 juegos
# 76561199057466527 <-- 52 juegos
# 76561198176695149 <-- 55 juegos
# 76561198121699782 <-- 362 juegos
# 76561198086708374 <-- 733 juegos
# 76561198294650349 <-- 1240 juegos

def main():
    data = GamesData(76561199104524520)
    print(*data.games_data)
    


if __name__ == "__main__":
    main()