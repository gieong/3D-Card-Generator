import bpy
import sys
import os

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import importlib
import Scene_Settings
import Deck
import Action
import Dealer

importlib.reload(Scene_Settings)
importlib.reload(Deck)
importlib.reload(Action)
importlib.reload(Dealer)

from Scene_Settings import *
from Deck import *
from Action import *
from Dealer import *

def main():
    print("\n========= \n**Start** \n=========")
    
    in_scene_name = "Scene"
    in_col_name = "Input_Collection"
    out_col_name = "Output_Collection"
    anim_fps = 60
    anim_secs = 5

    # Can load other settings via constructor arguments
    my_scene = Scene_Settings(anim_secs = anim_secs)
    # print(my_scene.anim_fps)
    
    card_name = "Card_Base"
    suites_parent_name = "Prefab_Suites"
    values_parent_name = "Prefab_Values"
    templates_parent_name = "Prefab_Templates"
    template_suites = "Template_Pos_Suites"
    template_values = "Template_Pos_Values"
    
    # Can load other prefabs via Deck.loadPrefabs() arguments
    my_deck = Deck(my_scene)
    # my_deck.printDeck()
    
    # Timers
    time = 0
    time_step = (1 / my_scene.anim_fps)
    
    # Simulation(s)
    my_dealer = Dealer(my_deck)
    
    # ===============================
    # Begin Simulation(s) of Actions
    # ===============================
    while (time < my_scene.anim_secs):
        
        my_dealer.simulate(time, time_step)
        
        time += time_step
    # my_dealer.printPlacements()
    # End Simulation(s) 
    
    # =====================
    # Pre Keyframe Cleanup
    # =====================
    for obj in my_deck.deck_drawn:
        obj.animation_data_clear()
    
    # =========================
    # Process Action schedules
    # =========================
    dealer_schedule = my_dealer.action_schedule
    dealer_index_pending = {}
    dealer_index_complete = {}
    
    time_anim = 0
    time_sim = 0
    
    # Initialize indices 
    for key in dealer_schedule.keys():
        dealer_index_pending[key] = 0
    
    # Forward time in following loop
    while (time_anim <= my_scene.anim_secs):
        
        # Set the Frame according to time_anim
        current_frame = round(time_anim * my_scene.anim_fps)
        my_scene.in_scene.frame_set(current_frame)
        
        # ========================
        # Process step simulation
        # ========================
        dealer_index_keyremoval = []
        
        for card, action_index in dealer_index_pending.items():
            obj_action = dealer_schedule[card][action_index]
           
            # Keyframe according to local simulation time
            if (time_sim >= obj_action.time_start and time_sim <= obj_action.time_start + time_step):
                obj_action.on_awake(time_sim)
                continue

            if (time_sim >= obj_action.time_end):
                obj_action.on_finish(time_sim)
                
                if (action_index + 1 < len(dealer_schedule[card])):
                    # Increment to next valid action 
                    dealer_index_pending[card] = action_index + 1
                else:
                    # Queue after iteration: Move object to finished w/ last valid action index
                    dealer_index_keyremoval.append(card)
                continue
            
            # Keyframe final pending positions if animation time expires
            if (time_anim == my_scene.anim_secs and time_sim <= obj_action.time_end):
                obj_action.on_pause(time_sim)
                continue
       
        # Perform removals of completed keys from pending list
        for key in dealer_index_keyremoval:
            dealer_index_complete[key] = dealer_index_pending.pop(key)
        
        time_sim += time_step
        # ========================
        # End of step simulation
        # ========================
        
        time_anim += time_step
    # End Action Processing
    
    # ===============
    # Final Cleanup
    # ===============
    my_scene.in_scene.frame_set(my_scene.in_scene.frame_start)
    
    for obj in my_deck.deck_drawn:
        anim_data = obj.animation_data
        action = anim_data.action
        fcurves = action.fcurves

        for fcurve in fcurves:
            fcurve.extrapolation = 'CONSTANT'
            key_frames = fcurve.keyframe_points
            for key_frame in key_frames:
                key_frame.interpolation = 'BEZIER'
    
    print("\n========= \n **End** \n=========")
    return
