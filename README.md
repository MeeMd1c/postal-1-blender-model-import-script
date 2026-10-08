# postal-1-blender-model-import-script
Blender import script for Postal 1 (RSPiX) models

Features:
- Loads Sea of Points (.sop) with mesh (.mesh) files
- Loads time intervals (framerate)
- Loads bounding spheres (.bounds)
- Loads both static and animated models, animations are handled with shape keys

TODO:
- add loading palette based texture (.tex)
- add loading rigid transforms (.trans)
- add support for legacy models (models that lack a version short, like "simple")
- add exporting
