import bpy
import bmesh
from mathutils import *

import math
import random
random.seed(1337)

class Deck:
    scene_settings = None
    
    deck_obj = None
    deck_new = []
    deck_drawn = []
    
    prefab_card = ""
    prefab_template_suites = ""
    prefab_template_values = ""
    
    prefab_suites = []
    prefab_values = []
    prefab_templates = []
    
    def __init__(self, scene_settings, deck_name = "Deck of Cards"):
        self.scene_settings = scene_settings
        
        self.loadPrefabs()
        
        # Create Deck Object  
        if deck_name in self.scene_settings.in_scene.objects:
            print("[Log] Object '%s' already exists." % (deck_name))
            self.deck_obj = self.scene_settings.in_scene.objects[deck_name]
        else:
            print("[Log] Object '%s' created." % (deck_name))
            self.deck_obj = bpy.data.objects.new(deck_name, None )
            self.scene_settings.out_col.objects.link(self.deck_obj)
        
        self.generateDeck()
        
        return
        
    # Input(IDs) -> Set(listof Prefabs)
    # Configure prefabs from the current scene  
    def loadPrefabs(self, card_name = "Card_Base", suites_parent_name = "Prefab_Suites", values_parent_name = "Prefab_Values", templates_parent_name = "Prefab_Templates", 
                        template_suites = "Template_Pos_Suites", template_values = "Template_Pos_Values"):
        print("=====================")
        print("   Loading Prefabs   ")
        print("=====================")
        # Find the card base object
        self.prefab_card = self.scene_settings.in_col.objects[card_name]
        
        # Load Suites from its parent container
        self.prefab_suites = self.scene_settings.in_col.objects[suites_parent_name].children
        
        # Load Values from its parent container
        self.prefab_values = self.scene_settings.in_col.objects[values_parent_name].children
        
        # Load Templates from its parent container
        self.prefab_templates = self.scene_settings.in_col.objects[templates_parent_name].children
        
        # Find the card corner templates object
        self.prefab_template_suites = [x for x in self.prefab_templates if template_suites == x.name][0]
        self.prefab_template_values = [x for x in self.prefab_templates if template_values == x.name][0]
        
        
        print('\n[Log] Prefab Card loaded.')
        print("\t- '%s'" % (self.prefab_card.name))
        print('\n[Log] Prefabs for Suites loaded.')
        for obj in self.prefab_suites:
            print("\t- '%s'" % (obj.name))
        print('\n[Log] Prefabs for Values loaded.')
        for obj in self.prefab_values:
            print("\t- '%s'" % (obj.name))  
        print('\n[Log] Prefabs for Templates loaded.')
        for obj in self.prefab_templates:
            print("\t- '%s'" % (obj.name))  
        print('\n[Log] Prefab Template Suites loaded.')
        print("\t- '%s'" % (self.prefab_template_suites.name))
        print('\n[Log] Prefab Template Values loaded.')
        print("\t- '%s'" % (self.prefab_template_values.name))

    # Input(Void) -> Set(listof Object)
    # Generates a collection of new card Objects into deck_new
    def generateDeck(self):
        print("=====================")
        print("Begin Deck Generation")
        print("=====================")
        
        self.deck_new = list(self.deck_obj.children)
        
        for suite_obj in self.prefab_suites:
            for value_obj in self.prefab_values:
                # Lookup template matching card value 
                value_id = value_obj.name.split('_')[-1]
                template_obj = [x for x in self.prefab_templates if value_id == x.name.split('_')[-1]][0]
                result_obj = self.generateCard(suite_obj, value_obj, template_obj)
                if not (result_obj is None):
                    self.deck_new.append(result_obj)
        
        self.shuffle()
        
        print("=====================")
        print(" End Deck Generation")
        print("=====================")
        
    # Input(Prefabs, Templates) -> Return(Object)
    # Generates a single card Objects
    def generateCard(self, suite_obj, value_obj, template_obj):
        card_obj = self.prefab_card
        
        card_material = card_obj.material_slots[0].material
        suite_material = suite_obj.material_slots[0].material
        
        template_suites_obj = self.prefab_template_suites 
        template_values_obj = self.prefab_template_values 
    
        final_obj = None 
        final_name = suite_obj.name + "_" + value_obj.name.split('_')[-1]
        
        mat_z180 = Matrix.Rotation(math.radians(180.0), 4, 'Z')
        
        # Skip if card (Object OR Mesh) already exists
        if final_name in self.scene_settings.in_scene.objects:
            print("[Log] Object '%s' already exists." % (final_name))
        elif final_name in self.scene_settings.in_scene.objects.data.objects:
            print("[Log] Mesh '%s' already exists." % (final_name))      
        else:
            # - Create Resultant Mesh Object
            mesh_data = bpy.data.meshes.new(final_name)
            
            # - Add the Materials
            mesh_data.materials.append(card_material)
            mesh_data.materials.append(suite_material)
            
            # - Build the Mesh
            bm = bmesh.new()
            temp_bm = bmesh.new()
            temp_bm_tp = bmesh.new()
            temp_mesh = bpy.data.meshes.new(".temp")
            
            # ===============================
            # Insert the Card Base Component
            # ===============================
            bm.from_mesh(card_obj.data)
            bm.faces.ensure_lookup_table()
            base_endIndex = bm.faces[-1].index
            
            for i in range(0, base_endIndex + 1):
                bm.faces[i].material_index = 0
            
            # ===============================
            # Insert the Suites Component
            # ===============================
            temp_bm_tp.clear()
            temp_bm_tp.from_mesh(template_suites_obj.data)
            
            # Apply from Template
            for vert_tp in temp_bm_tp.verts:
                # Configure translation based on template
                mat_loc = Matrix.Translation(vert_tp.co)
                
                # Apply Matrix Transformations
                temp_bm.clear()
                temp_bm.from_mesh(suite_obj.data)
                
                for vert in temp_bm.verts:
                    if vert_tp.co.y < 0:
                        vert.co = suite_obj.matrix_world.copy() @ mat_loc @ mat_z180 @ vert.co 
                    else:
                        vert.co = suite_obj.matrix_world.copy() @ mat_loc @ vert.co 
                
                # Then write to main BMesh
                temp_mesh.clear_geometry()
                temp_bm.to_mesh(temp_mesh)
                bm.from_mesh(temp_mesh)
            
            # Configure Materials
            bm.faces.ensure_lookup_table()
            suite_endIndex = bm.faces[-1].index
            
            for i in range(base_endIndex + 1, suite_endIndex + 1):
                bm.faces[i].material_index = 1
            
            # ===============================
            # Insert the Values Component
            # ===============================  
            temp_bm_tp.clear()
            temp_bm_tp.from_mesh(template_values_obj.data)
            
            # Apply from Template
            for vert_tp in temp_bm_tp.verts:
                # Configure translation based on template
                mat_loc = Matrix.Translation(vert_tp.co)
                
                # Apply Matrix Transformations
                temp_bm.clear()
                temp_bm.from_mesh(value_obj.data)
                
                for vert in temp_bm.verts:
                    if vert_tp.co.y < 0:
                        vert.co = value_obj.matrix_world.copy() @ mat_loc @ mat_z180 @ vert.co 
                    else:
                        vert.co = value_obj.matrix_world.copy() @ mat_loc @ vert.co 
                
                # Then write to main BMesh
                temp_mesh.clear_geometry()
                temp_bm.to_mesh(temp_mesh)
                bm.from_mesh(temp_mesh)
            
            # Configure Materials
            bm.faces.ensure_lookup_table()
            values_endIndex = bm.faces[-1].index
            
            for i in range(suite_endIndex + 1, values_endIndex + 1):
                bm.faces[i].material_index = 1                
            
            # ===============================
            # Apply the Template Component
            # ===============================
            temp_bm_tp.clear()
            temp_bm_tp.from_mesh(template_obj.data)
            
            # Apply from Template
            for vert_tp in temp_bm_tp.verts:
                # Configure translation based on template
                mat_loc = Matrix.Translation(vert_tp.co)
                
                # Apply Matrix Transformations
                temp_bm.clear()
                temp_bm.from_mesh(suite_obj.data)
                
                for vert in temp_bm.verts:
                    if vert_tp.co.y < 0:
                        vert.co = suite_obj.matrix_world.copy() @ mat_loc @ mat_z180 @ vert.co 
                    else:
                        vert.co = suite_obj.matrix_world.copy() @ mat_loc @ vert.co 
                
                # Then write to main BMesh
                temp_mesh.clear_geometry()
                temp_bm.to_mesh(temp_mesh)
                bm.from_mesh(temp_mesh)
            
            # Configure Materials
            bm.faces.ensure_lookup_table()
            template_endIndex = bm.faces[-1].index
            
            for i in range(values_endIndex + 1, template_endIndex + 1):
                bm.faces[i].material_index = 1
                
            # ===============================
            # Clean Up
            # ===============================
            
            # - Write the mesh and free the objects
            bm.to_mesh(mesh_data)
            bm.free()
            temp_bm.free()
            temp_bm_tp.free()
            bpy.data.meshes.remove(temp_mesh)
            
            # - Create new object from data, set to deck location
            final_obj = bpy.data.objects.new(mesh_data.name, mesh_data)
            final_obj.location = self.deck_obj.location

            # - Link object to scene.
            self.scene_settings.out_col.objects.link(final_obj)  
            final_obj.parent = self.deck_obj
            
            print("[Log] Object %s Created" % (final_name))
        
    
        return final_obj
    
    # Input(Void) -> Return(Object)
    # Return the first item from top of the deck
    def drawCard(self):
        card = self.deck_new.pop()
        self.deck_drawn.append(card)
        
        return card
        
    # Input(Object) -> Modify(listof Object)
    # Filter out the specified card from drawn pile and add to top of deck
    def returnCard(self, card):
        self.deck_drawn = [x for x in self.deck_drawn if x.name != card.name]
        self.deck_new.append(card)

    # Input(Object) -> Modify(listof Object)
    # Add a new card to top of deck    
    def insertCard(self, card):
        self.deck_new.append(card)

    # Input(Void) -> Modify(listof Object)
    # Randomize the order of cards in deck
    def shuffle(self):
        random.shuffle(self.deck_new)

    # Input(Void) -> Print(listof Object)
    # Print the current deck 
    def printDeck(self):
        
        print("\nDeck: '%s'" % (self.deck_obj.name))
        
        temp_arr = []
        row_count = 5
        str_format = '>> {0:^10} {1:^10} {2:^10} {3:^10} {4:^10}'
        for obj in self.deck_new:
            temp_arr.append(obj.name)
            
            if len(temp_arr) >= row_count:
                print(str_format.format(*temp_arr))
                temp_arr = []
                
        for x in range(len(temp_arr), row_count):
            temp_arr.append("--") 
        
        print(str_format.format(*temp_arr))
        
    
