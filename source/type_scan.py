import os
import io
import re

class IFCTypeScanner:
    curr_type = ""
    types = set()
        
    def read_chunks(self, directory, chunk_size=8*1024*1024):
        filenames = os.listdir(directory);
        for filename in filenames:
            with open(filename, "r") as ifc_file:
                while True:
                    chunk_data = ifc_file.read(chunk_size)
                    if not chunk_data:
                        break
                    yield chunk_data

    def record_ifc_types(self, chunk_data:str):
        self.types.add(set(re.findall("IFC[A-Z]+")))
        
        

