class State:
    DIALOGUE = 0
    ACTION = 1

    def __init__(self, starting_state):
        self.state = starting_state
    