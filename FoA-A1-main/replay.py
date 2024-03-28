from __future__ import annotations

import time

from action import PaintAction
from grid import Grid
from data_structures.queue_adt import CircularQueue
from undo import UndoTracker

class ReplayTracker:
    MAX_CAPACITY = 10000
    def __init__(self):
        """
        Initialise ReplayTracker obj
        self.action representing the Queue that store the actions

        Args:
        - None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(n), the arrayR complexity is O(n) as it creates None based on self.MAX_CAPACITY. Hence it is O(n)

        -Best Case: O(n), the arrayR complexity is O(n) as it creates None based on self.MAX_CAPACITY. Hence it is O(n)

        """
        self.action = CircularQueue(self.MAX_CAPACITY) #CircularQueue is chosen for ReplayTracker because of its property
                                                       #it allows to pop the first layer that add to the Queue and this is
                                                       #benefial to replay as replay is to restart the whole drawing animation
                                                       #so we can just pop and apply

    def start_replay(self) -> None:
        """
        Called whenever we should stop taking actions, and start playing them back.
        Useful if you have any setup to do before `play_next_action` should be called.

        Args:
        - None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -None
        """
        pass

    def add_action(self, action: PaintAction, is_undo: bool=False) -> None:
        """
        Adds an action to the replay.
        `is_undo` specifies whether the action was an undo action or not.
        Special, Redo, and Draw all have this is False.

        Args:
        - action representing PaintAction obj
        - is_undo representing undo is that action an undo action

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(1), constant
        -Best Case: O(1), constant
        Explanation: append function's complexity is O(1)
        """
        self.action.append((action,is_undo)) #append the action and is_undo to self.action queue for replay

    def play_next_action(self, grid: Grid) -> bool:
        """
        Plays the next replay action on the grid.

        Args:
        - None

        Raises:
        -None

        Returns:
        -Return boolean
        - If there were no more actions to play, and so nothing happened, return True.
        - Otherwise, return False.

        Complexity:
        -Worst Case: O(comp), as the undo_apply and redo_apply worst case are O(comp) and the rest of the code  O(1). Hence, the overall
                     complexity is O(comp)
        -Best Case: O(1), the best case of undo_apply and redo_apply are O(1) and the rest of the code are all O(1). Hence,
                    the overall complexity is O(1)
        """
        if not self.action.is_empty(): #if the queue is not empty then
            action, undo = self.action.serve() #serve to get the action and undo
            if undo: #if the action is an undo action then
                action.undo_apply(grid) #apply undo the action
            else:
                action.redo_apply(grid) #if not undo then redo the action
            return False

        else: #if self.action is empty then return true to indicate nthg happened
           return True

if __name__ == "__main__":
    action1 = PaintAction([], is_special=True)
    action2 = PaintAction([])

    g = Grid(Grid.DRAW_STYLE_SET, 5, 5)

    r = ReplayTracker()
    # add all actions
    r.add_action(action1)
    r.add_action(action2)
    r.add_action(action2, is_undo=True)
    # Start the replay.
    r.start_replay()
    f1 = r.play_next_action(g) # action 1, special
    f2 = r.play_next_action(g) # action 2, draw
    f3 = r.play_next_action(g) # action 2, undo
    t = r.play_next_action(g)  # True, nothing to do.
    assert (f1, f2, f3, t) == (False, False, False, True)

