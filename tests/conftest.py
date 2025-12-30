import os
import sys
from pathlib import Path

# Add the src directory to the python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))
