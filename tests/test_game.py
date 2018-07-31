"""game.py test"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import time
from connectFourLab.game import RunGame
from connectFourLab.game import RunGame
from connectFourLab.game.agents.monteCarlo import AgentSimulation
from connectFourLab.game import helpers


def test_game():
    from connectFourLab.game import RunGame
    game = RunGame()
    assert not game.is_running

    game = RunGame(player_one=AgentSimulation, async=True)
    while game.is_running:
        time.sleep(.3)
    
    assert game.status is not game.GameStatus.exception

    game.start()
    game.kill()
    assert game.status is game.GameStatus.killed

