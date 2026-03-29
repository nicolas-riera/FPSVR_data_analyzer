import os
import ctypes
from ctypes import wintypes

CSIDL_PERSONAL = 5  
SHGFP_TYPE_CURRENT = 0

buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

documents_path = buf.value
HISTORY_DIR = os.path.join(documents_path, "fpsVR", "History")