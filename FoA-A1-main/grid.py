from __future__ import annotations
from data_structures.referential_array import ArrayR
import layer_store


class Grid:
    DRAW_STYLE_SET = "SET"
    DRAW_STYLE_ADD = "ADD"
    DRAW_STYLE_SEQUENCE = "SEQUENCE"
    DRAW_STYLE_OPTIONS = (
        DRAW_STYLE_SET,
        DRAW_STYLE_ADD,
        DRAW_STYLE_SEQUENCE
    )

    DEFAULT_BRUSH_SIZE = 2
    MAX_BRUSH = 5
    MIN_BRUSH = 0

    def __init__(self, draw_style, x, y) -> None:
        """
        Initialise the grid object.

        Args:
        - draw_style:
            The style with which colours will be drawn.
            Should be one of DRAW_STYLE_OPTIONS
            This draw style determines the LayerStore used on each grid square.
        - x, y: The dimensions of the grid.

        Should also intialise the brush size to the DEFAULT provided as a class variable.

        Raises:
            -None

        Returns:
            -None

        Complexity:
            -Worst Case: O(k*(n+(z*comp)), O(k*(n+(z*comp)) as self.create_layer_grid()'s complexity is O(k*(n+(z*comp)),
                         creating ArrayR for self.layer_choice is O(n) where n is len(draw_style) and self.grid is O(n)
                         where n is x. And self.identify_draw_style() is O(comp). and the rest is O(1). Hence overall the worst case
                         complexity is O(k*(n+(z*comp))

            -Best Case: O(k*(n+(z*comp)), same as worst case since we need to initialise all again
        """
        self.layer_choice = ArrayR(len(draw_style)) #create list for the draw_style options
        self.draw_style = draw_style
        self.brush_size = self.DEFAULT_BRUSH_SIZE
        self.grid = ArrayR(x) #create an array to store the self.grid
        #assign x and y
        self.x = x
        self.y = y
        self.identify_draw_style() #identify which draw_style to use for that grid
        self.create_layer_grid() #create layer_Store for every grid

    def identify_draw_style(self):
        """
        identify which draw style based on the grid object created

        Args:
            - None

        Raises:
            -None

        Returns:
            -choice of drawstyle

        Complexity:
            -Worst Case: O(comp), where comp is cost of comparison and maximum it will run 3 times as there are only 3 types of draw style
                         Hence overall worst case complexity is O(comp)

            -Best Case: O(comp) same as worst case even though it found at the first loop but the complexity is still O(comp)
        """
        #store type of draw_style
        self.layer_choice[0] = layer_store.SetLayerStore
        self.layer_choice[1] = layer_store.AdditiveLayerStore
        self.layer_choice[2] = layer_store.SequenceLayerStore

        chosen_layer = 0
        for i in range(len(self.DRAW_STYLE_OPTIONS)): #loop through all the draw style
            if self.draw_style == self.DRAW_STYLE_OPTIONS[i]: #comparison to find the draw style
                chosen_layer = i #assign i to chosen layer

        return self.layer_choice[chosen_layer] #return the chosen drawstyle

    def create_layer_grid(self):
        """
        create the type of layer store based on the drawStyle chosen
        for each grid

        Args:
            - None

        Raises:
            -None

        Returns:
            -None

        Complexity:
            -Worst Case: O(k*(n+(z*comp)), where k is log(self.x), n is self.y and z is log(self.y) and comp is
                         the complexity of chosen_draw_Style(). As self.x and self.y is numerical value. Hence is log(self.x)
                         and log(self.y). Overall the code's worst case complexity is O(k*(n+(z*comp))

            -Best Case: O(k*(n+(z*comp)), same as worst case as it needs to iterature all over again
        """
        chosen_draw_style = self.identify_draw_style() #identify the draw style
        for row in range(self.x): #loop through self.x
            self.grid[row] = ArrayR(self.y) #for every row create an column ArrayR
            for column in range(self.y):#for every column in that row
                self.grid[row][column] = chosen_draw_style() #create a layer_store for every column of that row


    def __getitem__(self, item):
        """
        magic method to get the grid based on the coordinate

        Args:
            - None

        Raises:
            -None

        Returns:
            -None

        Complexity:
            -Worst Case: O(1), constant all O(1)
            -Best Case: O(1), constant all O(1)
        """
        return self.grid[item]


    def increase_brush_size(self):
        """
        Increases the size of the brush by 1,
        if the brush size is already MAX_BRUSH,
        then do nothing.

        Args:
            - None

        Raises:
            -None

        Returns:
            -None

        Complexity:
            -Worst Case: O(1), constant all O(1)
            -Best Case: O(1), constant all O(1)
        """
        if self.brush_size < self.MAX_BRUSH: #if self.brush_size less than the maximum limit
            self.brush_size += 1 #then plus 1

    def decrease_brush_size(self):
        """
        Decreases the size of the brush by 1,
        if the brush size is already MIN_BRUSH,
        then do nothing.

        Args:
            - None

        Raises:
            -None

        Returns:
            -None

        Complexity:
            - Worst Case: O(1), constant all O(1)
            -Best case: O(1), constant all O(1)
        """
        if self.brush_size > self.MIN_BRUSH: #if self.brush_size more than the minimum limit
            self.brush_size -= 1 #then minus 1

    def special(self):
        """
        Activate the special affect on all grid squares.

        Args:
            - None

        Raises:
            -None

        Returns:
            -None

        Complexity:
            -Worst Case: O(k*z*(n)), where k is log(self.x) , z is log(self.y) and the complexity of special() in worst case is O(n)
                         when the layer_store is sequence ana additive. Hence, the worst case complexity of overall code is
                         O(k*z*(n)).

            -Best Case: O(k*z), where k is log(self.x) , z is log(self.y) and the complexity of special() in best case is O(1)
                         when the layer_store is SetLayerStore. Hence, the best case complexity of overall code is
                         O(x*y)
        """
        for i in range(self.x): #loop through all the grid
            for j in range(self.y):
                self.grid[i][j].special() #turn on special for the grids





