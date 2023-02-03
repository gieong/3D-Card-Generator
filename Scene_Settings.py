import bpy

class Scene_Settings:

    # Variables (static)
    in_scene = None
    in_col = None
    
    out_col = None
    
    anim_fps = 60
    anim_secs = 5
    
    # Variables (dynamic)

    def __init__(self, anim_secs = 5, anim_fps = 60, in_scene_name = "Scene", in_col_name = "Input_Collection", out_col_name = "Output_Collection"):
        self.anim_fps = anim_fps
        self.anim_secs = anim_secs
        
        # Configure active Scene
        if in_scene_name in bpy.data.scenes:
            print("[Log] Scene '%s' selected." % (in_scene_name))
            self.in_scene = bpy.data.scenes[in_scene_name]
            
            print("'%s' Collections" % (self.in_scene.name)) 
            for key in self.in_scene.collection.children.keys():
                print("\t- '%s'" % (key))
        else:
            print("[Warning] Scene '%s' doesn't exist." % (in_scene_name))
            print("**Exit**")
            return
        
        # Configure animation settings in Scene
        self.in_scene.frame_start = 1
        self.in_scene.frame_end = self.anim_fps * self.anim_secs
        self.in_scene.render.fps = self.anim_fps
        
        # Read Input Collection
        if in_col_name in bpy.data.collections:
            print("[Log] Collection '%s' selected." % (in_col_name))
            self.in_col = bpy.data.collections[in_col_name]
            
            print("'%s' Collection" % (self.in_col.name)) 
            for key in self.in_col.all_objects.keys():
                if "Prefab" in key:
                    print("\t [%s]" % (key))
                else:
                    print("\t- '%s'" % (key))
        else:
            print("[Warning] Collection '%s' doesn't exist." % (in_col_name))
            print("**Exit**")
        
        # Configure Output Collection
        if out_col_name in bpy.data.collections:
            print("[Log] Collection '%s' selected." % (out_col_name))
            self.out_col = bpy.data.collections[out_col_name]
        else:
            print("[Log] Collection '%s' creation." % (out_col_name))
            self.out_col = bpy.data.collections.new(out_col_name)
            self.in_scene.collection.children.link(self.out_col)
            
            print("'%s' Collections" % (self.in_scene.name)) 
            for key in self.in_scene.collection.children.keys():
                print("\t- '%s'" % (key))
            
        return
