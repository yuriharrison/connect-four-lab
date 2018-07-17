"""Time strategy"""
import time
from . import Strategy
from ...timer import Timer


class TimerStrategy(Strategy):
    """Timer strategy allow you to easily program
    a timer to control the time of each turn.

    Using the `start_timer` method you can set a rule
    which will determine the start point of the timer
    and when the time expires the `time_out` flag will
    be changed to `True`.

    # Example
    
    ```python
    from . import AgentBase
    from .strategies import TimerStrategy

    class AgentNew(AgentBase, TimerStrategy):

        def action(self, board):
            rule = lambda time_left: time_left/(25-self.turn)
            self.start_timer(rule, max=20)

            while not self.time_out:
                # loop process

            return column
    ```
    """
    clock = None
    clock_management = True

    def start_timer(self, rule, max):
        """Set the rule and starts the timer

        # Arguments
            rule: lambda, required, rule which will determine
                the time limit of the turn.
            max: float, required; maximum time allowed per turn.
        """
        self.time_out = False
        time_to_spend = None

        if self.clock:
            time_left = self.clock.time_left
            time_to_spend = rule(time_left)
            time_to_spend = time_to_spend if time_to_spend < max else max
        else:
            time_to_spend = max

        self.timer_thread = Timer(time_to_spend, self.time_out_callback)
        self.timer_thread.start()

    def time_out_callback(self):
        self.time_out = True