# Battleship-Solitaire

Project for CSC384 at UofT, 2024. Thus, source code, description, and tests were provided by the instructor.

Goal: given a starter board of the game, solve the Battleship Solitaire using AC-3 arc consistency.

Types of Ships:
- Submarines (1x1)
- Destroyers (1x2)
- Cruisers (1x3)
- Battleships (1x4)
- Carriers (1x5)

Rules:
1. A ship is either horizontal or vertical, never diagonal.
2. The input provides the number of each type of ship
3. The input provides the number of ship parts in each row and column
4. Each ship must be surrounded by at least one square of water on all sides and corners.
4. Some inputs will indicate whether some squares are water or a part of a ship. 



Example: </br>
Input </br>
    212212          <--- Number of ship parts in each row </br>
    040114          <--- Number of ship parts in each column </br>
    32100           <--- Number of each type of ship </br>
    000000 </br>
    000S00 </br>
    000000 </br>
    00000v </br>
    000000 </br>
    000000 </br>

- '0': unknown 
- ‘S’: submarine
- ‘.’: water
- ‘<’: left end of a horizontal ship
- ‘>’: right end of a horizontal ship
- ‘^’: top end of a vertical ship
- ‘v’: bottom end of a vertical ship
- ‘M’: middle segment of a ship

Output </br>
    .S...S </br>
    ...S.. </br>
    .^...^ </br>
    .M...v </br>
    .v.... </br>
    ....<> </br>




Command:

python3 battle.py --inputfile inputs/inputfile --outputfile outputs/outputfile

