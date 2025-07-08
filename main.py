import chess
import chess.pgn
import chess.engine
import csv
import os
import time
from tqdm import tqdm
import multiprocessing

def analyze_time_pressure_games(pgn_path, player_name, output_csv, engine_path="stockfish", depth=20):
    """
    Analyze games to find moves made with <10 seconds on clock
    and evaluate their quality using centipawn loss
    """
    # Initialize chess engine
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    engine.configure({"Hash": 1300, "Threads" : 1})  # Set to 512 MB or more

    with open(pgn_path) as pgn_file, open(output_csv, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            'game_id', 'move_number', 'player', 'clock', 'move',
            'best_score','played_score', 'engine_depth'
        ])

        game_count = 0
        game = chess.pgn.read_game(pgn_file)

        pbar = tqdm(desc=f"Analyzing {player_name}'s games")
        while game:
            print("on game ",game_count)
            game_count += 1
            pbar.update(1)
            board = game.board()
            node = game

            # Initialize time tracking
            white_time = 180.0  # 3 minutes in seconds
            black_time = 180.0
            move_number = 0

            #print(node)
            while not node.is_end():
                node = node.variations[0]
                move = node.move
                comment = node.comment

                if '[%clk' in comment:
                    clock_str = comment.split('[%clk ')[1].split(']')[0]
                    parts = list(map(float, clock_str.split(':')))
                    total_seconds = parts[0]*3600 + parts[1]*60 + parts[2]
                    if board.turn == chess.WHITE:
                        start_time = white_time
                        white_time = total_seconds
                    else:
                        start_time = black_time
                        black_time = total_seconds
                else:
                    start_time = white_time if board.turn == chess.WHITE else black_time

                # Check if player was in time pressure at move start


                if board.turn == chess.WHITE:
                    is_target_player = (game.headers["White"] == player_name)
                else:
                    is_target_player = (game.headers["Black"] == player_name)


                if is_target_player and start_time < 10.0:
                    # Analyze position before move to get best score
                    #print("in radar")
                    moving_side = board.turn  # True = white, False = black

                    # Eval before move (position before actual move is made)
                    analysis_before = engine.analyse(board, chess.engine.Limit(depth=depth))
                    best_score = analysis_before["score"].white().score() if moving_side else analysis_before["score"].black().score()

                    # Make the move
                    board.push(move)

                    # Eval after move (current board)
                    analysis_after = engine.analyse(board, chess.engine.Limit(depth=depth))
                    played_score = analysis_after["score"].white().score() if moving_side else analysis_after["score"].black().score()

                    # Write results to CSV
                    csv_writer.writerow([
                        f"{game.headers.get('Site', '')}-{game.headers.get('Date', '')}",
                        move_number,
                        player_name,
                        round(start_time, 1),
                        move.uci(),
                        best_score,
                        played_score,
                        depth
                    ])
                else :
                    board.push(move)

                move_number += 1
                #print(move_number)

            game = chess.pgn.read_game(pgn_file)

    engine.quit()
    return game_count

def analyze_player_games(player_name, year=2024):
    """Analyze all games for a player"""
    pgn_path = f"all pgns/{player_name}_tt_{year}-01_{year}-12.pgn"
    output_csv = f"time_pressure_analysis/{player_name}_time_pressure_{year}.csv"

    os.makedirs("time_pressure_analysis", exist_ok=True)

    print(f"Analyzing {player_name}'s {year} games...")
    start_time = time.time()
    game_count = analyze_time_pressure_games(pgn_path, player_name, output_csv)
    elapsed = time.time() - start_time
    print(f"Analyzed {game_count} games in {elapsed:.1f} seconds. Results saved to {output_csv}")

# Players to analyze
PLAYERS = {
    "David navara": "FormerProdigy",
    "Magnus Carlsen": "MagnusCarlsen",
    "Hikaru Nakamura": "Hikaru",
    "Daniel Naroditsky": "DanielNaroditsky",
    "Alireza Firouzja": "Firouzja2003",
    "Fabiano Caruana": "FabianoCaruana",
    "Aleksander Grischuk" : "Grischuk",
    "Matthias Bluebam" : "Msb2",
    "Christopher Yoo" : "ChristopherYoo"
}

def worker(username):
    analyze_player_games(username)

usernames = list(PLAYERS.values())

with multiprocessing.Pool(processes=9) as pool:
    pool.map(worker, usernames)

