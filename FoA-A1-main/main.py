import arcade
import arcade.key as keys
import math
from grid import Grid
from layer_util import get_layers, Layer
from layers import lighten
from action import PaintAction, PaintStep
from undo import UndoTracker
from replay import ReplayTracker

class MyWindow(arcade.Window):
    """ Painter Window """

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 700
    SIDEBAR_WIDTH = 100
    BUTTONS_HEIGHT = 100
    SCREEN_TITLE = "Paint"

    REPLAY_TIMER_DELTA = 0.05

    GRID_SIZE_X = 32
    GRID_SIZE_Y = 32

    BG = [255, 255, 255]

    # SCAFFOLD PART
    # Unless you're adding new features, you shouldn't need to touch this.

    def __init__(self) -> None:
        """Initialise visual and logic variables."""
        super().__init__(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.SCREEN_TITLE)
        arcade.set_background_color(self.BG)
        self.grid: Grid = None
        self.draw_style = Grid.DRAW_STYLE_SET
        self.z_pressed = False
        self.y_pressed = False
        self.z_timer = 0
        self.y_timer = 0
        self.enable_ui = True
        self.replay_timer = 0
        self.on_init()

    def reset(self) -> None:
        """Reset the screen."""
        self.grid = Grid(self.draw_style, self.GRID_SIZE_X, self.GRID_SIZE_Y)
        self.timestamp = 0

        self.selected_layer_index = -1
        self.dragging = None
        self.prev_drawn = None
        self.prev_pos = None
        self.draw_size = 2

        # Visual calculations
        self.DRAW_PANEL = self.SCREEN_WIDTH - self.SIDEBAR_WIDTH
        self.GRID_SQ_WIDTH = self.DRAW_PANEL / self.GRID_SIZE_X
        self.GRID_SQ_HEIGHT = self.SCREEN_HEIGHT / self.GRID_SIZE_Y
        self.LAYER_BUTTON_SIZE = self.SIDEBAR_WIDTH / 2
        # Action button sprites
        self.action_buttons = arcade.SpriteList()
        self.draw_mode_button = arcade.Sprite(
            "img/on_off.png" if self.draw_style == Grid.DRAW_STYLE_SET else (
                "img/additive.png" if self.draw_style == Grid.DRAW_STYLE_ADD else "img/sequence.png"
            ),
            scale=50/48,
        )
        self.draw_mode_button.center_x = self.DRAW_PANEL + self.LAYER_BUTTON_SIZE / 2
        self.draw_mode_button.center_y = self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.draw_mode_button)
        self.replay_button = arcade.Sprite(
            "img/replay.png",
            scale=50/48,
        )
        self.replay_button.center_x = self.DRAW_PANEL + 3 * self.LAYER_BUTTON_SIZE / 2
        self.replay_button.center_y = self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.replay_button)
        self.brush_big_button = arcade.Sprite(
            "img/brush_up.png",
            scale=50/48,
        )
        self.brush_big_button.center_x = self.DRAW_PANEL + self.LAYER_BUTTON_SIZE / 2
        self.brush_big_button.center_y = 3 * self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.brush_big_button)
        self.brush_small_button = arcade.Sprite(
            "img/brush_down.png",
            scale=50/48,
        )
        self.brush_small_button.center_x = self.DRAW_PANEL + 3 * self.LAYER_BUTTON_SIZE / 2
        self.brush_small_button.center_y = 3 * self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.brush_small_button)
        self.special_button = arcade.Sprite(
            "img/special.png",
            scale=50/48,
        )
        self.special_button.center_x = self.DRAW_PANEL + self.LAYER_BUTTON_SIZE / 2
        self.special_button.center_y = 5 * self.LAYER_BUTTON_SIZE / 2
        self.action_buttons.append(self.special_button)

        self.on_reset()

    def setup(self) -> None:
        """Set up the game and initialize the variables."""
        self.reset()

    def on_draw(self) -> None:
        """Draw everything"""
        self.clear()
        # UI - Layers
        for i, layer in enumerate(get_layers()):
            if layer is None: break
            xstart = (i % 2) * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            xend = ((i % 2)+1) * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = self.SCREEN_HEIGHT - (i//2) * self.LAYER_BUTTON_SIZE
            yend = self.SCREEN_HEIGHT - (i//2+1) * self.LAYER_BUTTON_SIZE
            bg = lighten.apply(layer.bg or self.BG[:], 0, 0, 0) if self.selected_layer_index == i else (layer.bg or self.BG[:])
            if not self.enable_ui:
                bg = lighten.apply(bg, 0, 0, 0)
            arcade.draw_lrtb_rectangle_filled(xstart, xend, ystart, yend, bg)
            arcade.draw_lrtb_rectangle_outline(
                xstart, xend, ystart, yend, (0, 0, 0), border_width=1,
            )
            arcade.draw_text(str(i), xstart, (ystart+yend)/2, (0, 0, 0), 18, width=xend-xstart, align="center", bold=True, anchor_y="center")
        # UI - Draw Modes / Action buttons
        self.action_buttons.draw()
        # Grid
        for x in range(self.GRID_SIZE_X):
            for y in range(self.GRID_SIZE_Y):
                arcade.draw_lrtb_rectangle_filled(
                    self.GRID_SQ_WIDTH * x,
                    self.GRID_SQ_WIDTH * (x+1),
                    self.GRID_SQ_HEIGHT * (y+1),
                    self.GRID_SQ_HEIGHT * y,
                    self.grid[x][y].get_color(self.BG[:], self.timestamp, x, y),
                )

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Called when the mouse buttons are pressed."""
        if x > self.DRAW_PANEL:
            if not self.enable_ui:
                return
            # Buttons
            for i, layer in enumerate(get_layers()):
                if layer is None: break
                xstart = (i % 2) * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
                xend = ((i % 2)+1) * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
                ystart = self.SCREEN_HEIGHT - (i//2) * self.LAYER_BUTTON_SIZE
                yend = self.SCREEN_HEIGHT - (i//2+1) * self.LAYER_BUTTON_SIZE
                if xstart <= x < xend and yend <= y < ystart:
                    self.selected_layer_index = i
                    break
            # Actions
            xstart = self.DRAW_PANEL
            xend = self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = self.LAYER_BUTTON_SIZE
            yend = 0
            if xstart <= x < xend and yend <= y < ystart:
                self.change_draw_mode()
            xstart = self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            xend = 2 * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = self.LAYER_BUTTON_SIZE
            yend = 0
            if xstart <= x < xend and yend <= y < ystart:
                self.start_replay()
            xstart = self.DRAW_PANEL
            xend = self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = 2 * self.LAYER_BUTTON_SIZE
            yend = self.LAYER_BUTTON_SIZE
            if xstart <= x < xend and yend <= y < ystart:
                self.on_increase_brush_size()
            xstart = self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            xend = 2 * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = 2 * self.LAYER_BUTTON_SIZE
            yend = self.LAYER_BUTTON_SIZE
            if xstart <= x < xend and yend <= y < ystart:
                self.on_decrease_brush_size()
            xstart = self.DRAW_PANEL
            xend = 1 * self.LAYER_BUTTON_SIZE + self.DRAW_PANEL
            ystart = 3 * self.LAYER_BUTTON_SIZE
            yend = 2 * self.LAYER_BUTTON_SIZE
            if xstart <= x < xend and yend <= y < ystart:
                self.on_special()
        else:
            self.dragging = True
            self.try_draw(x, y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        """Called when the mouse buttons are released."""
        self.dragging = False
        self.prev_drawn = None
        self.prev_pos = None

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        """Called when the mouse moves."""
        if not self.dragging:
            return
        if not(0 <= self.selected_layer_index < len(get_layers())):
            return
        if x > self.DRAW_PANEL:
            return
        self.try_draw(x, y)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called when a keyboard key is pressed."""
        if not self.enable_ui:
            return
        self.z_pressed = keys.Z == symbol and (modifiers & keys.MOD_CTRL)
        self.y_pressed = keys.Y == symbol and (modifiers & keys.MOD_CTRL)
        if self.z_pressed:
            self.on_undo()
            self.z_timer = 0.5
        if self.y_pressed:
            self.on_redo()
            self.y_timer = 0.5

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when a keyboard key is released."""
        self.z_pressed = False
        self.y_pressed = False

    def try_draw(self, x, y) -> None:
        """Attempt to draw at a position, but safely fail if an invalid square."""
        if self.selected_layer_index == -1:
            return
        layer = get_layers()[self.selected_layer_index]
        if self.prev_pos is not None:
            # Try draw in increments of 0.5 to avoid skipping squares.
            mhat_dist = abs(x - self.prev_pos[0]) + abs(y - self.prev_pos[1])
            increment = 0.5
            points_to_draw = []
            for d in range(1, math.ceil(mhat_dist/increment)+1):
                distance = min(d * increment / mhat_dist, 1)
                nx = distance * (x - self.prev_pos[0]) + self.prev_pos[0]
                ny = distance * (y - self.prev_pos[1]) + self.prev_pos[1]
                nx_pos = int(nx // self.GRID_SQ_WIDTH)
                ny_pos = int(ny // self.GRID_SQ_HEIGHT)
                points_to_draw.append((nx_pos, ny_pos))
        else:
            x_pos = int(x // self.GRID_SQ_WIDTH)
            y_pos = int(y // self.GRID_SQ_HEIGHT)
            points_to_draw = [
                (x_pos, y_pos)
            ]
        for px, py in points_to_draw:
            if self.prev_drawn is None or (px, py) != self.prev_drawn:
                if 0 <= px < self.GRID_SIZE_X and 0 <= py < self.GRID_SIZE_Y:
                    self.on_paint(layer, px, py)
                    self.prev_drawn = (px, py)
        self.prev_pos = (x, y)

    def start_replay(self) -> None:
        """Begin the replay mode."""
        self.enable_ui = False
        self.grid = Grid(self.draw_style, self.GRID_SIZE_X, self.GRID_SIZE_Y)
        self.replay_timer = self.REPLAY_TIMER_DELTA
        self.on_replay_start()

    def on_update(self, delta_time) -> None:
        """Movement and game logic."""
        self.timestamp += delta_time
        if self.z_pressed:
            self.z_timer -= delta_time
            if self.z_timer <= 0:
                self.on_undo()
                self.z_timer += 0.05
        if self.y_pressed:
            self.y_timer -= delta_time
            if self.y_timer <= 0:
                self.on_redo()
                self.y_timer += 0.05
        if not self.enable_ui:
            self.replay_timer -= delta_time
            if self.replay_timer <= 0:
                self.replay_timer += self.REPLAY_TIMER_DELTA
                finished = self.on_replay_next_step()
                if finished:
                    self.enable_ui = True

    def change_draw_mode(self) -> None:
        """Changes the draw mode of the application, and resets the window."""
        if self.draw_style == Grid.DRAW_STYLE_SET:
            self.draw_style = Grid.DRAW_STYLE_ADD
        elif self.draw_style == Grid.DRAW_STYLE_ADD:
            self.draw_style = Grid.DRAW_STYLE_SEQUENCE
        elif self.draw_style == Grid.DRAW_STYLE_SEQUENCE:
            self.draw_style = Grid.DRAW_STYLE_SET
        self.reset()

    # STUDENT PART

    def on_init(self):
        """
        Initialisation that occurs after the system initialisation.

        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(1), constant

        -Best Case: O(1), constant

        """
        self.UndoTracker = UndoTracker()
        self.ReplayTracker = ReplayTracker()

    def on_reset(self):
        """
        Called when a window reset is requested.

        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(1), constant

        -Best Case: O(1), constant
        """
        self.UndoTracker = UndoTracker()
        self.ReplayTracker = ReplayTracker()

    def on_paint(self, layer: Layer, px, py):
        """
        Called when a grid square is clicked on, which should trigger painting in the vicinity.
        Vicinity squares outside of the range [0, GRID_SIZE_X) or [0, GRID_SIZE_Y) can be safely ignored.

        Args:
        -layer: The layer being applied.
        -px: x position of the brush.
        -py: y position of the brush.

        Raises:
        -None

        Returns:
        -None

        Complexity:
        Let i be max(px - d, 0), min(px + d + 1, self.grid.x)
        Let j be max(py - d, 0), min(py + d + 1, self.grid.y)
        Where d is the brush size and px and py are the coordinate

        -Worst Case: O(log(i)*(log(j)*(comp))), O(comp) is the worst case of add function when layer_Store is SetLayerStore
                     and the rest of the code is O(1). Hence, the overall complexity for worst case is O(log(i)*(log(j)*(comp)))

        -Best Case: O(log(i)*log(j)), O(1) is the best case of add function when layer_store is Addtive and sequence
                    and the rest of the code is O(1). Hence, the overall complexity for best case is O(log(i)*log(j))
        """

        d = self.grid.brush_size
        action_steps = PaintAction()
        for x in range(max(px - d, 0), min(px + d + 1, self.grid.x)):#output the horizontal based on the brush size
            for y in range(max(py - d, 0), min(py + d + 1, self.grid.y)): #output vertical based on the brush size
                if abs(px - x) + abs(py - y) <= d:  #if the grid is within the manhanttan distance
                    check = self.grid[x][y].add(layer) #if doesn't exist then add
                    if check:
                        All_Step = PaintStep((x, y), layer) #create all the steps for each grid
                        action_steps.add_step(All_Step) #then add steps to PaintAction list
        self.UndoTracker.add_action(action_steps) #push the PaintAction to the Undo_stack
        self.ReplayTracker.add_action(action_steps)#append PaintAction to replay

    def on_undo(self):
        """
        Called when an undo is requested.

        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(comp), as the undo function's worst case is O(comp) and cost comparison is also O(comp).
                    The add_action's complexity is O(1). Hence, the overall code's worst case is O(comp)

        -Best Case: O(comp), as the undo function's best case is O(1) and comp is the cost of complexity. The add_action's
                    complexity is O(1). Hence, the overall code's best case is O(1)
        """
        undo_action = self.UndoTracker.undo(self.grid) #do undo when on_undo is called
        if undo_action is not None: #if undo_action is not None
            self.ReplayTracker.add_action(undo_action, True) #then add to replayTracker


    def on_redo(self):
        """Called when a redo is requested.
        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(comp), as the redo function's worst case is O(n) and the cost of comparison is comp.
                    The add_action's complexity is O(1). Hence, the overall code's worst case is O(comp)

        -Best Case: O(comp), as the redo function's best case is O(1) and the cost of comparison is comp. The add_action's
                    complexity is O(1). Hence, the overall code's best case is O(1)
        """
        redo_action = self.UndoTracker.redo(self.grid) #do redo when on_redo is called
        if redo_action is not None: #if redo_action is not None
            self.ReplayTracker.add_action(redo_action) #then add action to replayTracker

    def on_special(self):
        """
        Called when the special action is requested.

        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(u*t*(k*z*(n)), where u is log(self.grid.x) , t is log(self.grid.y) and O(k*z*(n)), is special()'s
                     worst case complexity and the rest are all O(1). there are two loops hence u*t and special()
                     function is in the inner loop hence the overall complexity for worst case is O(u*t*(k*z*(n*comp))

        -Best Case: O(u*t*(k*z)), where u is log(self.grid.x) , y is log(self.grid.y), and the special()'s best case complexity is O(k*z)
                    and the rest are all O(1). Hence, the overall complexity for best case is O(u*t*(k*z))
        """
        special_action = PaintAction(is_special= True) #create a PaintAction obj for special
        for x in range(self.grid.x):  #loop through all the grid selected
            for y in range(self.grid.y):
                self.grid[x][y].special() #turn on special for all the grid selected
                All_step = PaintStep((x,y), self.grid[x][y]) #create steps for Special action
                special_action.add_step(All_step) #add all the steps to PaintAction obj
        self.ReplayTracker.add_action(special_action) #add the PaintAction to ReplayTracker


    def on_replay_start(self):
        """Called when the replay starting is requested.

        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: None

        -Best Case: None
        """
        pass

    def on_replay_next_step(self) -> bool:
        """
        Called when the next step of the replay is requested.
        Returns whether the replay is finished.

        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(comp), as the play_next_action()'s worst case is O(comp)

        -Best Case: O(1), as the play_next_action()'s best case is O(1)
        """
        return self.ReplayTracker.play_next_action(self.grid)

    def on_increase_brush_size(self):
        """Called when an increase to the brush size is requested."""
        self.grid.increase_brush_size()

    def on_decrease_brush_size(self):
        """Called when a decrease to the brush size is requested."""
        self.grid.decrease_brush_size()

def main():
    """ Main function """
    window = MyWindow()
    window.setup()
    arcade.run()

def run_with_func(func, pause=False):
    from threading import Thread
    window = MyWindow()
    window.setup()
    if pause:
        _ = input("Press enter to begin test.")
    t = Thread(target=func, args=(window,))
    t.start()
    arcade.run()


if __name__ == "__main__":
    main()
