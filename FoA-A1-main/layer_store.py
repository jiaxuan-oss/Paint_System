from __future__ import annotations
from abc import ABC, abstractmethod

import layer_util
from layer_util import *
from layers import *
from data_structures.queue_adt import CircularQueue
from data_structures.stack_adt import Stack, ArrayStack
from data_structures.array_sorted_list import ArraySortedList
from data_structures.sorted_list_adt import ListItem
from data_structures.bset import BSet
class LayerStore(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store.
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        """
        pass

    @abstractmethod
    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def special(self):
        """
        Special mode. Different for each store implementation.
        """
        pass

class SetLayerStore(LayerStore):
    """
    Set layer store. A single layer can be stored at a time (or nothing at all)
    - add: Set the single layer.
    - erase: Remove the single layer. Ignore what is currently selected.
    - special: Invert the colour output.
    """
    def __init__(self):
        """
        Initialise the SetLayerStore object.
        self.layer representing store the layer that apply
        self.count representing odd number indicates special on and even number indicates special off

        Args:
            - None

        Raises:
            -None

        Returns:
            -None

        Complexity:
            -Worst Case: O(1), constant
            -Best Case: O(1), constant
            -Explantion: all is constant thus O(1), Best case = worst case
        """
        LayerStore.__init__(self)
        self.layer = None
        self.count = 0

    def add(self, layer: Layer) -> bool:
        """
        Add layer to self.layer, for SetLayerStore it only has one layer
        Returns true if the LayerStore was actually changed.

        Args:
        -layer representing Layer object eg. rainbow, black etc

        Raises:
        -None

        Returns:
        -Boolean representing the layer is changed or not

        Complexity:
        -Worst Case: O(comp), comp representing comparison complexity
        -Best Case: O(comp), comp representing comparison complexity
        -Explanation: as it needs to compare the current layer with the layer applied before make any changes
                      hence best case = worst case
        """
        if self.layer == layer: #if the layer is the current layer
            return False #then return false
        else: #if not then
            self.layer = layer #set layer to self.layer
            self.count = 0 #count set to 0 to use special
        return self.layer == layer #then return true if it changed
    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Erasing a SetLayerStore just means having no layers applied.
        Returns true if the LayerStore was actually changed.

        Args:
        -layer representing Layer object eg. rainbow, black etc

        Raises:
        -None

        Returns:
        -Boolean representing the layer is erased or not

        Complexity:
        -Worst Case: O(comp), constant
        -Best Case: O(comp), constant
        Explanation: all is constant thus O(1), best case = worst Case
        """
        self.layer = None #erase set self.layer to None
        self.count = 0    #count set to 0 to use special
        return self.layer == None #return True if it erased

    def special(self):
        """
        turn on special mode, special mode for SetLayerStore is invert
        the current layer

        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(1), constant
        -Best Case: O(1), constant
        Explanation: all is constant thus O(1), best case = worst Case
        """
        self.count += 1

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.

        Args:
        -start representing the starting color
        -timestamp representing the time at which the get_color method being called
        -x representing the column grid
        -y representing the row grid

        Raises:
        -None

        Returns:
        -color representing the color after the layer applied

        Complexity:
        -Worst Case: O(1), constant
        -Best Case: O(1), constant
        Explanation: the apply function is O(1) as it is all arithmetic operation, thus best case = worst case
        """
        if self.layer: #if layer is not none
            color = self.layer.apply(start, timestamp, x, y) #then apply the color
            if self.count % 2 != 0: #if is odd then means special is on if is even then special is off
                color = invert.apply(color, timestamp, x,y)

        else: #if self.layer is none
            color = start #set color to the starting color
            if self.count % 2 != 0: #if is odd then means special is on if is even then special is off
                color = invert.apply(start, timestamp, x,y) #apply invert

        return color #return color
class AdditiveLayerStore(LayerStore):
    """
    Additive layer store. Each added layer applies after all previous ones.
    - add: Add a new layer to be added last.
    - erase: Remove the first layer that was added. Ignore what is currently selected.
    - special: Reverse the order of current layers (first becomes last, etc.)
    """

    def __init__(self):
        """
        Initialise the AdditiveLayerStore object.
        self.layer representing the layer that applied
        self.special_mode representing whether special_mode is on or off

        Args:
        - None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(n), create CircularQueue complexity is O(n) according to arrayR it creates None based on the length
                     of the len(LAYERS). Thus O(n)

        -Best Case: O(n), create CircularQueue complexity is O(n) according to arrayR it creates None based on the length
                     of the len(LAYERS). Thus O(n)
        """
        LayerStore.__init__(self)
        self.layer = CircularQueue(len(LAYERS)*100) #CircularQueue is chosen for storing layers because of its efficiency
        self.special_mode = False                   #as the way of storing layers suitable for CircularQueue
        self.start = None                           #for example, its erase function can be done by serve
                                                    #its add function can be done by add
    def add(self, layer: Layer) -> bool:
        """
        Add layer to self.layer Add a new layer to be added last.
        Returns true if the LayerStore actually changed.

        Args:
        -layer representing Layer object eg. rainbow, black etc

        Raises:
        -None

        Returns:
        -boolean representing the layer is changed or not

        Complexity:
        -Worst Case: O(1), where self.check_item() worst case is O(1) and the rest are all O(1)
        -Best Case: O(1),  where self.check_item() best case is O(1) and the rest are all O(1)
        """
        if self.layer.is_full(): #if is full then
            self.layer.serve() #serve

        self.layer.append(layer) #then append another layer
        return self.check_item(layer) #and return true if it actually changed

    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer by erasing the
        oldest layer and Returns true if the LayerStore was actually changed.

        Args:
        -layer representing Layer object eg. rainbow, black etc

        Raises:
        -None

        Returns:
        -boolean representing the layer is erased or not

        Complexity:
        -Worst Case: O(1), where self.check_item() worst case is O(1) and the rest are all O(1)
        -Best Case: O(1),  where self.check_item() best case is O(1) and the rest are all O(1)
        """
        if self.layer.is_empty(): #if the layer is empty then return False
            return False
        item = self.layer.serve() #erase the oldest item
        return not self.check_item(item) #return True if it is erased

    def special(self):
        """
        special mode for AdditiveLayerStore is reverse the layers

        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(n), where n is len(self.layer)
        -Best Case: O(n), where n is len(self.layer)
        Explanation: as it loop through self.layer hence the complexity is len(self.layer), best = worst
                     as it needs to reverse the list anyway
        """
        temp_stack = ArrayStack(len(self.layer)) #create an arrayStack with self.layer
        temp_queue = CircularQueue(len(self.layer.array)) #create circularQueue with self.layer.array
        for i in range(self.layer.front, self.layer.rear): #loop through the self.layer
            temp_stack.push(self.layer.array[i]) #and push into the stack

        for i in range(len(temp_stack)): #loop through the stack that pushed in
            temp_queue.append(temp_stack.pop()) #and append it back to queue to get reverse order
        self.layer = temp_queue #assign to self.layer

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.

        Args:
        -start representing the starting color
        -timestamp representing the time at which the get_color method being called
        -x representing the column grid
        -y representing the row grid

        Raises:
        -None

        Returns:
        -color representing the color after the layer applied

        Complexity:
        -Worst Case: O(n), where n is len(self.layer)
        -Best Case: O(n), where n is len(self.layer)
        Explanation: as it loop through self.layer and apply is O(1) hence the complexity is len(self.layer), best = worst
        """
        self.start = start #set the starting color to start
        if self.layer:#if layers is not none
            for i in range(self.layer.front, self.layer.rear): #loop through the queue
                color = self.layer.array[i].apply(self.start, timestamp, x, y) #apply all the layers
                self.start = color

        else:#if is none then
            self.start = start  #return starting color
        return self.start

    def check_item(self, layer: Layer)-> bool:
        """
        check whether the item in self.layer or not

        Args:
        layer representing Layer objects eg, rainbow, black etc

        Raises:
        -None

        Returns:
        -boolean representing the item exist in the queue

        Complexity:
        -Worst Case: O(1), as self.layer maximum capacity is 3 hence O(1)
        -Best Case: O(1), where it found the layer during the first loop
        """
        for i in range(self.layer.front, self.layer.rear): #loop through the queue
            if layer == self.layer.array[i]: #compare the layer
                return True #if exist then return true
        return False # if not return false

class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
    """
    def __init__(self):
        """
        Initialise the SequenceLayerStore object.
        self.layer representing the layer that applied
        self.start representing the starting color

        Args:
        - None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(1), constant
        -Best Case: O(1), constant
        Explanation: as creating a Bset the maximum len(LAYERS) is 20 hence it is constant, Best = worst
        """
        LayerStore.__init__(self)
        self.layer = BSet(len(LAYERS)) #BSet is used for SequenceLayerStore because it is more efficient and take less
                                       #memory compare to the others when implementing its function. eg add function
                                       #bset has the complexity of O(1) and remove function has complexity of O(1) as well
        self.start = None #for get_color

    def Create_List_Item(self, layer: Layer)-> ListItem:
        """
        Create a ListItem object for the layer argument

        Args:
        - layer representing Layer object eg rainbow, black etc

        Raises:
        -None

        Returns:
        -item representing ListItem of the layer argument

        Complexity:
        -Worst Case: O(1), constant
        -Best Case: O(1), constant
        Explanation: creating an ListItem obj is O(1), best = worst
        """
        item = ListItem(layer, layer.index)#create ListItem according to the layer
        return item

    def add(self, layer: Layer) -> bool:
        """
        Sequential Layer Store simply keeps tracking of every
        layer as either "applying" or "not applying".
        Returns true if the LayerStore was actually changed.

        Args:
        -layer representing Layer object eg. rainbow, black etc

        Raises:
        -None

        Returns:
        -boolean representing the layer is changed or not

        Complexity:
        -Worst Case: O(1), constant
        -Best Case: O(1),  constant
        Explanation: all O(1) , worst = best
        """
        #layer.index + 1 -> as bset cannot store 0
        check = layer.index + 1 in self.layer#check the layer exist or no
        if check: #if layer doesn't exist
            return False
        else:
            self.layer.add(layer.index + 1)# then add to the list
            return layer.index + 1 in self.layer #and return True

    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer by not applying the
        layer Returns true if the LayerStore was actually changed.

        Args:
        -layer representing Layer object eg. rainbow, black etc

        Raises:
        -None

        Returns:
        -boolean representing the layer is erased or not

        Complexity:
        -Worst Case: O(1), constant
        -Best Case: O(1), constant
        Explanation: All O(1) hence, worst = best
        """
        check = layer.index + 1 in self.layer #check the layer exist or not
        if check: #if exist
            self.layer.remove(layer.index + 1)#if exist, delete the layer according to the index
            return layer.index + 1 not in self.layer #return True if it removes
        else:
            return False #the layer doesn't exist thus return false

    def special(self):
        """
        special mode for SequenceLayerStore is delete the median of the
        layer in self.layer

        Args:
        -None

        Raises:
        -None

        Returns:
        -None

        Complexity:
        -Worst Case: O(n), where O(n) is len(self.layer) according to self.lexicographic_order() and erase() is O(1).
                     Hence overall is O(n)

        -Best Case: O(n), where O(n) is len(self.layer) according to self.lexicographic_order() and erase() is O(1).
                    Hence overall is O(n)
        """
        if len(self.layer) != 0:
            median = self.lexicographic_order() #call lexicographic order to get the layer to erase
            self.erase(median) #erase the layer

    def lexicographic_order(self)-> Layer:
        """
        Arrange all layers in self.layer in lexicographic order
        and return the middle layer if the existing layers are odd number
        whereas return the smaller one at the middle if it is even number

        Args:
        -None

        Raises:
        -None

        Returns:
        -returns a layer that should be deleted

        Complexity:
        -Worst Case: O(n), where n is len(self.layer)
        -Best Case: O(n), where n is len(self.layer)
        Explanation: as it loops through self.layer hence, O(n) where n is len(self.layer)
                     and the rest is O(1). Thus, the overall complexity is O(n). Best = worst
        """
        temp_array = ArraySortedList(len(self.layer))#create a temporary array
        for i in range(1,len(LAYERS) + 1):#loop through existing layer
            if i in self.layer:
                #i-1 -> to get back the original index
                lexi_list_item = ListItem(LAYERS[i-1], LAYERS[i-1].name) #create ListItem on all the existing layers with their obj and name
                temp_array.add(lexi_list_item) #add to the temporary array

        if len(self.layer) % 2 == 0: #if the number of existing layers are even
            median = (len(self.layer)-1) // 2  #then take the smaller one
        else:
            median = len(self.layer) // 2 #if is odd number then take the middle layer

        return temp_array[median].value #return the middle layer obj

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.

        Args:
        -start representing the starting color
        -timestamp representing the time at which the get_color method being called
        -x representing the column grid
        -y representing the row grid

        Raises:
        -None

        Returns:
        -color representing the color after the layer applied

        Complexity:
        -Worst Case: O(n), where n is len(self.layer)
        -Best Case: O(n), where n is len(self.layer)
        Explanation: it loops through len(self.layer) hence it has complexity of O(n) where
                     n is len(self.layer) and the rest is O(1) hence overall it has a complexity
                     of O(n), best = worst
        """
        color = start
        if self.layer: #if self.layer is not none then
            for i in range(1, len(LAYERS) + 1): #loop through all the existing layers
                if i in self.layer: #if the index exist in bset then
                    color = LAYERS[i-1].apply(color, timestamp, x, y) #apply the layers
        else:
            color = start #if self.layer is none then return the starting color
        return color  #return color

