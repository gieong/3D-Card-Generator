from mathutils import *

from abc import ABC, abstractmethod
import math

class LerpAction(ABC):
    """
    Abstract class for lerp animations
    """
    anim_obj = None

    time_start = 0
    time_end = math.inf
    
    def __init__(self, anim_obj, time_start, time_end):
        self.anim_obj = anim_obj
        self.time_start = time_start
        self.time_end = time_end

    @abstractmethod
    def play(self, time):
        pass
        
    @abstractmethod
    def on_awake(self, time):
        pass
        
    @abstractmethod
    def on_pause(self, time):
        pass
           
    @abstractmethod
    def on_rewind(self, time):
        pass
        
    @abstractmethod
    def on_finish(self, time):
        pass

class LocationAction(LerpAction):
    """
    Move from from position a to position b 
    """
    
    pos_start = None
    velocity = None

    def __init__(self, anim_obj, time_start, time_end, pos_start, velocity):
        super().__init__(anim_obj, time_start, time_end)
        self.pos_start = pos_start
        self.velocity = velocity

    def play(self, time):
        time_diff = self.time - self.time_start
        pos_cur = self.pos_start + self.velocity * time_diff
        #print(f"\nTranslateCommand: Currently translating as follows ... {self.anim_obj.name}"
             # f"\nTime_Start = {self.time_start} Time_End = {self.time_end}"
             # f"\n{self.pos_start} + {pos_cur}")

    def on_awake(self, time):
        self.anim_obj.location = self.pos_start
        self.anim_obj.keyframe_insert(data_path="location")
        
        # print(f"\nTranslateCommand: Start translation ... {self.anim_obj.name}"
             # f"\nTime_Start = {self.time_start} Time_End = {self.time_end}"
             # f"\n{self.pos_start} + {self.velocity} units/sec")

    def on_pause(self, time):
        time_diff = self.time - self.time_start
        pos_cur = self.pos_start + self.velocity * time_diff
        self.anim_obj.location = pos_cur 
        self.anim_obj.keyframe_insert(data_path="location")
        
        # print(f"\nTranslateCommand: Pause translation ... {self.anim_obj.name}"
              # f"\nTime_Start = {self.time_start} Time_Cur = {self.time}"
              # f"\n{self.pos_start} --> {pos_cur}")

    def on_rewind(self, time):
        time_diff = self.time - self.time_start
        pos_cur = self.pos_start + self.velocity * time_diff
        self.anim_obj.location = pos_cur 
        self.anim_obj.keyframe_insert(data_path="location")
        
        # print(f"\nTranslateCommand: Rewind translation ... {self.anim_obj.name}"
              # f"\nTime_Start = {self.time_start} Time_Cur = {self.time}"
              # f"\n{pos_cur} --> {self.pos_start}")
        
    def on_finish(self, time):
        time_diff = self.time_end - self.time_start
        pos_end = self.pos_start + self.velocity * time_diff
        self.anim_obj.location = pos_end 
        self.anim_obj.keyframe_insert(data_path="location")
        
        # print(f"\nTranslateCommand: Finish translation ... {self.anim_obj.name}"
              # f"\nTime_Start = {self.time_start} Time_End = {self.time_end}"
              # f"\n{self.pos_start} --> {pos_end}")
              