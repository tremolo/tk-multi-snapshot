"""
Copyright (c) 2013 Shotgun Software, Inc
----------------------------------------------------

"""
import os

import tank
from tank import Hook

import win32com
from win32com.client import Dispatch, constants
from pywintypes import com_error

Application = Dispatch("XSI.Application").Application

class SceneOperation(Hook):
    """
    Hook called to perform an operation with the 
    current scene
    """
    
    def execute(self, operation, file_path, **kwargs):
        """
        Main hook entry point
        
        :operation: String
                    Scene operation to perform
        
        :file_path: String
                    File path to use if the operation
                    requires it (e.g. open)
                    
        :returns:   Depends on operation:
                    'current_path' - Return the current scene
                                     file path as a String
                    'reset'        - True if scene was reset to an empty 
                                     state, otherwise False
                    all others     - None
        """
        
        if operation == "current_path":
            # return the current scene path
            
            # query the current scene 'name' and file path from the application:
            scene_filepath = Application.ActiveProject.ActiveScene.filename.value
            scene_name = Application.ActiveProject.ActiveScene.Name
                        
            # There doesn't seem to be an easy way to determin if the current scene 
            # is 'new'.  However, if the file name is "Untitled.scn" and the scene 
            # name is "Scene" rather than "Untitled", then we can be reasonably sure 
            # that we haven't opened a file called Untitled.scn
            if scene_name == "Scene" and os.path.basename(scene_filepath) == "Untitled.scn":
                return ""
            return scene_filepath

        elif operation == "open":
            # open the specified scene without any prompts
            # Application.OpenScene(path, Confirm, ApplyAuxiliaryData)
            Application.OpenScene(file_path, False, False)

        elif operation == "save":
            # save the current scene:
            Application.SaveScene()

        elif operation == "reset":
            # reset the current scene - for snapshot this is only ever
            # called when restoring from snapshot history prior to
            # opening the restored scene
            
            # If the Solid Angle Arnold renderer is installed, Softimage will 
            # crash if their OnEndNewScene event is not muted.  To avoid this 
            # problem, lets find and Mute the event whilst we do the new.
            arnold_event = None
            event_info = Application.EventInfos
            for event in event_info:
                if event.Type == "OnEndNewScene" and event.Name == "SITOA_OnEndNewScene" and not event.Mute:
                    arnold_event = event
                    break
            try:
                if arnold_event:
                    # Mute the arnold event
                    self.parent.log_debug("Muting %s event..." % arnold_event.Name)
                    arnold_event.Mute = True
                    
                # perform the new scene:
                Application.NewScene("", True)
            except:
                return False
            else:
                return True
            finally:
                if arnold_event:
                    self.parent.log_debug("Unmuting %s event..." % arnold_event.Name)
                    arnold_event.Mute = False
            
            
            
            
            
            
            
            
            
