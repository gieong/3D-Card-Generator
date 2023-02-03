import bpy
from mathutils import *

import math
import random
random.seed(1337)

from Action import *

class Dealer:

    deck = ""
    action_schedule = {}

    draw_timer = 0
    draw_cooldown = 0.080
    draw_duration = 0.075
    
    flip_timer = 0
    flip_cooldown = 0.08
    flip_duration = 0.010
    
    # Playspace parameters
    card_placements = [[]]
    prefab_table = None
    
    rows = 6
    cols = 9
    row_padding = 1.45
    col_padding = 1.05
    row_counter = 0
    col_counter = 0
    z_padding = 0.01

    def __init__(self, deck):
        self.deck = deck
        self.card_placements = [["" for i in range(self.cols)] for j in range(self.rows)]
        
        self.loadPrefabs()

        return
        
    # Input(IDs) -> Set(listof Prefabs)
    # Configure prefabs from the current scene  
    def loadPrefabs(self, table_name = "Table_Surface" ):
        self.prefab_table = self.deck.scene_settings.in_col.objects[table_name]
        
        # + Dynamic model sizing of table via properties
        self.table_width = 9
        self.table_height = 7.15
        
        # + Empty Obj for deck_offset dealing position
        self.deck_offset = Vector((-1.2, -0.12, 0.5))
    
        return
    
    # Input(Float, Float) -> Modify(dict<String, listof Action>)
    # Generate the Action queue of objects through the simluation    
    def simulate(self, time, time_step):
        
        # Draw a card from deck's "new" pile
        if self.deck.deck_new and self.draw_timer <= 0:
            self.draw_timer = self.draw_cooldown
            my_card = self.deck.drawCard()
            # print("[Log] Drew Card %s" % (my_card.name))
            
            # Determine placement coordinates 
            x_offset = self.col_counter * self.col_padding
            y_offset = self.row_counter * self.row_padding
            z_offset = self.z_padding * (self.row_counter + 0.1 * self.col_counter)
            end_pos = Vector((x_offset - (self.table_width / 2 ), y_offset - (self.table_height / 2), z_offset ))
            
            # Determine velocity
            deck_pos = (self.deck.deck_obj.location + self.deck_offset) - Vector((self.table_width / 2, self.table_height / 2, 0))
            my_velocity = (end_pos - deck_pos) / self.draw_duration
            time_end = time + self.draw_duration
            
            # Place card on table
            self.card_placements[self.row_counter][self.col_counter] = my_card.name
            
            # Determine next row and column
            self.col_counter += 1
            self.row_counter += self.col_counter // self.cols
            self.col_counter = self.col_counter % self.cols
            self.row_counter = self.row_counter % self.rows
            
            # Queue animation
            my_action = LocationAction(my_card, time, time_end, deck_pos, my_velocity)
            
            if my_card.name in self.action_schedule:
                self.action_schedule[my_card.name] = self.action_schedule[my_card.name].append(my_action)
            else:
                self.action_schedule[my_card.name] = [my_action]
        # Flip cards drawn on the table once all placed
        elif not self.deck.deck_new and self.flip_timer <= 0:
            self.flip_timer = self.flip_cooldown
            # print("[Log] Flip Card %s" % ("TODO"))
            
        # Increment timers
        self.draw_timer -= time_step
        self.flip_timer -= time_step
        
        return 
        
    # Input(Void) -> Print(Float)
    # Print the current timers  
    def printTimers(self):
        print("[Log] Dealer DT '%d' DC '%d'." % (self.draw_timer, self.draw_cooldown))
    
    # Input(Void) -> Print(Float)
    # Print the current card placements  
    def printPlacements(self):
        for row in self.card_placements:
            print(row)
    