import os
import math
from typing import List
from models.base import File

class Files():
    def __init__(self, path: str) -> None:
        self.path = path

    async def find_files(self, extension: str = ".blend") -> List[File]:
        files = os.listdir(self.path)
        
        blend_files = [
                {
                    "name": file,
                    "output_name": f"render_{os.path.splitext(file)[0]}",
                    "path": os.path.join(self.path, file),
                    "size": self.size_format(os.path.getsize(os.path.join(self.path, file)))
                }
                for file in files
                if file.endswith(extension)
            ]
        
        return {"files": blend_files}
    
    def size_format(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(round(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])