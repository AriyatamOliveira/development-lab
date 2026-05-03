import importlib
import pkgutil
import sys
from pathlib import Path

from core.style import info, error

def load_modules():
    """
    Dynamically loads all scripts from the modules/ directory.
    Returns a dictionary mapping module names to the imported module objects.
    """
    modules_dir = Path(__file__).resolve().parent.parent / "modules"
    if not modules_dir.exists():
        error(f"Modules directory not found at {modules_dir}")
        sys.exit(1)
        
    loaded = {}
    
    # Temporarily add the parent directory to sys.path if needed
    parent_path = str(modules_dir.parent)
    if parent_path not in sys.path:
        sys.path.insert(0, parent_path)

    for _, module_name, is_pkg in pkgutil.iter_modules([str(modules_dir)]):
        if is_pkg:
            continue
            
        full_module_name = f"modules.{module_name}"
        try:
            mod = importlib.import_module(full_module_name)
            loaded[module_name] = mod
        except Exception as e:
            error(f"Failed to dynamically load module {module_name}: {e}")
            
    info(f"Dynamically loaded {len(loaded)} modules.")
    return loaded
