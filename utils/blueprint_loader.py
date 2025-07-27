# import os
# import importlib
# from flask import Blueprint

# def register_blueprints(app, base_package="resources"):
#     base_path = os.path.join(os.path.dirname(__file__), "..", base_package)

#     for root, _, files in os.walk(base_path):
#         for file in files:
#             if file.endswith(".py") and not file.startswith("__"):
#                 rel_path = os.path.relpath(os.path.join(root, file), base_path)
#                 module_path = (
#                     rel_path.replace(os.sep, ".").replace(".py", "")
#                 )

#                 full_module = f"{base_package}.{module_path}"
#                 try:
#                     module = importlib.import_module(full_module)
#                     bp = getattr(module, "bp", None)
#                     if isinstance(bp, Blueprint):
#                         app.register_blueprint(bp)
#                 except Exception as e:
#                     print(f"⚠️  Skipped {full_module}: {e}")
