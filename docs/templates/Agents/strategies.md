# Strategies

Strategies are the classes with common algorithms that can be shared among multiple
[agents](./agents). It makes easy to implement variances or combine diferent strategies when creating an new agent.

### Example
```python
# inheriting from two strategy classes
class AgentSimulationTL(AgentBase, SimulationStrategy, TimerStrategy):
    name = 'Simulation TL'
    description = 'Simple simulation strategy (simulates managing the time limit)'
    kind = 'simulation'
    clock_management = True

    # picking a single method from a strategy class
    childs = TreeSearchStrategy.childs

    def action(self, board):
        # applying the strategy method from TimerStrategy
        rule = lambda time_left: time_left/(25-self.turn)
        self.start_timer(rule, max=20)
        
        ...
```

{{autogenerated}}