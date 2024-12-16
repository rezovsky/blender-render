import os

class Files():
    def __init__(self, path: str) -> None:
        self.path = path

    async def find_files(self, extention: str = ".blend"):
        files = os.listdir(self.path)
        
        blend_files = [file for file in files if file.endswith(extention)]
            
        return {"files": blend_files}