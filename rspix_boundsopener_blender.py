import struct
import bpy
import math
from pathlib import Path

exp_header = b"\x43\x48\x41\x4E" #CHAN

exp_ver = b"\x01\x00"

file_dir = "E:/Steam/steamapps/common/POSTAL1/res/game/main_idle.bounds" #input("File directory (.bounds): ")

file_name = Path(file_dir).stem

file_bounds = Path(file_dir).with_suffix('.bounds')

def read_header(f):
        header = f.read(4)
        if header != exp_header:
            print("Header magic isn't equal to CHAR!")
            sys.exit()
        ver = f.read(2)
        if ver != exp_ver:
            print("Version is incorrect - legacy file?")
            sys.exit()
        filetype = f.read(2)
        print("filetype: ", filetype)
        flags = f.read(2)
        print("flags: ", flags)
        unkn = f.read(4)
        if unkn != b"\x00\x00\x00\x00":
            print("!!! unknown: ", unkn)
        t_total = f.read(4)
        if t_total != b"\x01\x00\x00\x00":
            print("total time: ", t_total)
        t_int = f.read(4)
        if t_int != b"\x01\x00\x00\x00":
            print("time interval: ", t_int)
        frames = f.read(4) #NumItems
        for_frames = struct.unpack("<I", frames)[0]
        print("frames: ", struct.unpack("<I", frames)[0])
        vertcount = f.read(4)
        return frames, for_frames, t_int

if Path(file_bounds).is_file():
    with open(file_bounds, 'rb') as bounds:
        print("Opening .bounds")
        frames, for_frames, interval = read_header(bounds)

        bounds.seek(-4, 1)
            
        scene = bpy.context.scene
        scene.frame_start = 0
        scene.frame_current = 0
        scene.frame_end = for_frames - 1
        scene.render.fps = 1
        scene.render.fps_base = struct.unpack("<I", interval)[0] / 1000

        empty_data = bpy.data.objects.new(file_name+"_bounds", None)

        current_collection = bpy.context.collection
        current_collection.objects.link(empty_data)

        empty_data.empty_display_type = 'SPHERE'
        
        empty_data.select_set(True)
        bpy.context.view_layer.objects.active = empty_data
        
        obj = bpy.context.active_object
        
        for i in range(for_frames):
                
            x = bounds.read(4)
            y = bounds.read(4)
            z = bounds.read(4)
            scale = bounds.read(4)

            x_val = struct.unpack("<f", z)[0] * -1
            y_val = struct.unpack("<f", x)[0] * -1
            z_val = struct.unpack("<f", y)[0]
            
            #x_val = struct.unpack("<f", x)[0]
            #y_val = struct.unpack("<f", z)[0]
            #z_val = struct.unpack("<f", y)[0]
            scale_val = struct.unpack("<f", scale)[0]

            empty_data.location = (x_val, y_val, z_val)
            empty_data.empty_display_size = scale_val
            obj.keyframe_insert(data_path="location")
            #obj.keyframe_insert(data_path="scale")
            obj.keyframe_insert(data_path="empty_display_size")
            scene.frame_current += 1
        