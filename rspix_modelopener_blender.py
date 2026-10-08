import struct
import bpy
import math
from pathlib import Path

output_vert = []
output_tri = []

exp_header = b"\x43\x48\x41\x4E" #CHAN

exp_ver = b"\x01\x00"

file_dir = "E:/Steam/steamapps/common/POSTAL1/res/game/main_idle.sop" #input("File directory (.sop, .mesh): ")

file_name = Path(file_dir).stem

file_mesh = Path(file_dir).with_suffix('.mesh')
file_sop = Path(file_dir).with_suffix('.sop')

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
        return frames, vertcount, for_frames, t_int

if Path(file_sop).is_file():
    with open(file_sop, 'rb') as sop:
        print("Opening .sop")
        frames, vertcount, for_frames, interval = read_header(sop)
        print("verts: ", struct.unpack("<I", vertcount)[0])
        #if vertcount == b"\xFF\xFF\xFF\xFF":
        if Path(file_mesh).is_file():
            with open(file_mesh, 'rb') as mesh:
                print("Opening .mesh")
                frames_mesh, vertcount_mesh, for_frames_mesh, interval = read_header(mesh)
                if vertcount_mesh != b"\xFF\xFF\xFF\xFF":
                    print("weird vertcount ", vertcount_mesh)
                tricount = mesh.read(2)
                for_tri = struct.unpack("<H", tricount)[0]
                print("tris: ", for_tri)
                for i in range(for_tri):
                    a = mesh.read(2)
                    b = mesh.read(2)
                    c = mesh.read(2)
                
                    a_val = struct.unpack("<H", a)[0]
                    b_val = struct.unpack("<H", b)[0]
                    c_val = struct.unpack("<H", c)[0]
                    
                    output_tri.append((a_val, b_val, c_val))

            sop.seek(-4, 1)
            
            obj = None 
            shape_keys = {}
            
            scene = bpy.context.scene
            scene.frame_start = 0
            scene.frame_current = 0
            scene.frame_end = for_frames - 1
            scene.render.fps = 1
            scene.render.fps_base = struct.unpack("<I", interval)[0] / 1000
            
            for i in range(for_frames):
                vertcount = sop.read(4)
                for_verts = struct.unpack("<I", vertcount)[0]
                
                for j in range(for_verts):
                    x = sop.read(4)
                    y = sop.read(4)
                    z = sop.read(4)
                    unk_vert = sop.read(4)
                    
                    x_val = struct.unpack("<f", x)[0]
                    y_val = struct.unpack("<f", y)[0]
                    z_val = struct.unpack("<f", z)[0]
                    
                    output_vert.append((x_val, y_val, z_val))
                    
                    if unk_vert != b"\x00\x00\x80\x3F":
                        print("!!! unk vert = ", unk_vert)
                
                if i == 0:
                    mesh_data = bpy.data.meshes.new(file_name)
                    mesh_data.from_pydata(output_vert, [], output_tri)
                    mesh_data.update()
                    
                    obj = bpy.data.objects.new(file_name, mesh_data)
                    bpy.context.collection.objects.link(obj)
                    
                    basis_key = obj.shape_key_add(name="Basis", from_mix=False)
                    shape_keys[0] = basis_key
                else:
                    if obj is not None:
                        new_key = obj.shape_key_add(name=f"Key_{i}", from_mix=False)
                        for v_idx, coords in enumerate(output_vert):
                            if v_idx < len(new_key.data):
                                new_key.data[v_idx].co = coords
                        shape_keys[i] = new_key
                
                output_vert.clear()
            
            if obj and obj.data.shape_keys:
                for frame_idx in range(for_frames):
                    scene.frame_set(frame_idx)
                    
                    for key_idx, skey in shape_keys.items():
                        if key_idx == 0:
                            continue

                        if key_idx == frame_idx:
                            skey.value = 1.0
                        else:
                            skey.value = 0.0
                            
                        skey.keyframe_insert(data_path="value", frame=frame_idx)

                obj.rotation_euler[0] = math.radians(90)
                obj.rotation_euler[2] = math.radians(-90)
                
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    print(":)")
