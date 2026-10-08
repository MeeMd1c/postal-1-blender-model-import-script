import struct
#import os
from pathlib import Path

output_vert = []
output_tri = []

exp_header = b"\x43\x48\x41\x4E" #CHAN

exp_ver = b"\x01\x00"

file_dir = input("File directory (.sop, .mesh): ")

file_name = Path(file_dir).stem

file_mesh = file_name+".mesh"
file_sop = file_name+".sop"

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
        anim_unkn1 = f.read(4)
        if anim_unkn1 != b"\x01\x00\x00\x00":
            print("animation unknown: ", anim_unkn1)
        anim_unkn2 = f.read(4)
        if anim_unkn2 != b"\x01\x00\x00\x00":
            print("animation unknown 2: ", anim_unkn2)
        frames = f.read(4)
        if frames != b"\x01\x00\x00\x00":
            for_frames = struct.unpack("<I", frames)[0]
            print("frames: ", struct.unpack("<I", frames)[0])
        vertcount = f.read(4)
        return frames, vertcount, for_frames

if Path(file_sop).is_file():
    with open(file_sop, 'rb') as sop:
        print("Opening .sop")
        frames, vertcount, for_frames = read_header(sop)
        print("verts: ", struct.unpack("<I", vertcount)[0])
        #if vertcount == b"\xFF\xFF\xFF\xFF":
        if Path(file_mesh).is_file():
            with open(file_mesh, 'rb') as mesh:
                print("Opening .mesh")
                frames_mesh, vertcount_mesh, for_frames_mesh = read_header(mesh)
                if vertcount_mesh != b"\xFF\xFF\xFF\xFF":
                    print("weird vertcount ", vertcount_mesh)
                tricount = mesh.read(2)
                for_tri = struct.unpack("<H", tricount)[0]
                print("tris: ", for_tri)
                for i in range(for_tri):
                    a = mesh.read(2)
                    b = mesh.read(2)
                    c = mesh.read(2)
                
                    a = struct.unpack("<H", a)
                    b = struct.unpack("<H", b)
                    c = struct.unpack("<H", c)
                    output_tri.append(f"{i+1} a = {a} b =  {b} c =  {c}")
                with open("output_tri.txt", "w", encoding="utf-8") as file_out:
                    file_out.writelines(line + "\n" for line in output_tri)
            sop.seek(-4, 1)
            for i in range(for_frames):
                #print("FRAME", i)
                vertcount = sop.read(4)
                for_verts = struct.unpack("<I", vertcount)[0]
                output_vert.append(f"FRAME {i} VERTCOUNT {for_verts}")
                for j in range(for_verts):
                    x = sop.read(4)
                    y = sop.read(4)
                    z = sop.read(4)
                    unk_vert = sop.read(4)

                    x = struct.unpack("<f", x)
                    y = struct.unpack("<f", y)
                    z = struct.unpack("<f", z)
                    #unk_vert = struct.unpack("<f", unk_vert)
                    #print("x = ", x, "y = ", y, "z = ", z)
                    output_vert.append(f"{j+1} x = {x} y =  {y} z =  {z}")
                    if unk_vert != b"\x00\x00\x80\x3F":
                        print("!!! unk vert = ", unk_vert)
        with open("output_vert.txt", "w", encoding="utf-8") as file_out:
            file_out.writelines(line + "\n" for line in output_vert)
        print(":)")
