from __future__ import annotations
from action import PaintAction
from grid import Grid
from data_structures.stack_adt import ArrayStack

class UndoTracker:
    MAX_CAPACITY = 10000
    def __init__(self):
        """
        Initialise UndoTracker object.
        self.undo_stack representing ArrayStack create for undo
        self.redo_stack representing ArrayStack create for redo

        Args:
        - None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(n), O(n) as according to arrayR it will create number of None based on self.MAX_CAPACITY
                     Hence it is O(n)

        -Best Case: O(n), O(n) as according to arrayR it will create number of None based on self.MAX_CAPACITY
                     Hence it is O(n)
        """
        self.undo_stack = ArrayStack(self.MAX_CAPACITY) #ArrayStack is chosen because of its functionality, as we need
        self.redo_stack = ArrayStack(self.MAX_CAPACITY) #LIFO(last in first out) to implement undo and redo
    def add_action(self, action: PaintAction) -> None:
        """
        Adds an action to the undo tracker.
        If your collection is already full,
        feel free to exit early and not add the action.

        Args:
        - action representing the PaintAction obj

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(1), constant
        -Best Case: O(1), constant
        Explanation: is_full(), clear(), push() are all O(1). Hence, the complexity is
                     O(1). Worst = Best
        """
        if self.undo_stack.is_full():#if the stack is full
            self.undo_stack.clear() #then clear the stack

        self.undo_stack.push(action) #then push the action to the stack

    def undo(self, grid: Grid) -> PaintAction|None:
        """
        Undo an operation, and apply the relevant action to the grid.
        If there are no actions to undo, simply do nothing.

        Args:
        - grid represent grid object

        Raises:
        -None

        Returns:
        -action representing the action that was undone, or None.

        Complexity:
        -Worst Case: O(comp), O(comp) when layer_store is SetLayerStore as the erase function for SetLayerStore is O(comp).
                     And the other codes is_empty(), pop(), push() are all O(1). Hence overall complexity for worst
                     case is O(comp)

        -Best Case: O(1), O(1) when the layer_store is sequence and additive as the erase function for sequence and additive
                    is O(1). And the other codes is_empty(), pop(), push() are all O(1). Hence overall complexity for
                    best case is O(1)
        """
        if self.undo_stack.is_empty(): #if the undo_stack is empty then
            return None #return None

        action = self.undo_stack.pop() #pop the stack if is not empty
        action.undo_apply(grid) #then undo the popped action
        self.redo_stack.push(action) #push it to redo_stack for redo
        return action


    def redo(self, grid: Grid) -> PaintAction|None:
        """
        Redo an operation that was previously undone.
        If there are no actions to redo, simply do nothing.

        Args:
        - grid represent grid object

        Raises:
        -None

        Returns:
        -action representing The action that was redone, or None.

        Complexity:
        -Worst Case: O(comp), when the layer_store is SetLayerStore as its add function's complexity is O(comp) And the
                     other codes is_empty(), pop() ,push() are all O(1). Hence, overall the complexity for worst case is O(comp)

        -Best Case: O(1), when the layer_store is Additive and Sequence as their add functions are O(1) And the other codes is_empty(), pop()
                     push() are all O(1). Hence, overall complexity for best case is O(1)
        """
        if self.redo_stack.is_empty():#if redo_stack is empty
            return None #then return None
        action = self.redo_stack.pop() #pop action from redo_stack
        action.redo_apply(grid) #redo the action
        self.undo_stack.push(action) #push it to undo_stack
        return action

