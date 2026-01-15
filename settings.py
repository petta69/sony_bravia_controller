import json
import os
from typing import Optional
from pydantic import BaseModel
       
##
## Module for reading settings.json file into a config object
##


class ModelConfig(BaseModel):
    bravia_host_01: Optional[str] = "192.168.111.96"
    bravia_use_https_01: Optional[bool] = False
    bravia_psk_01: Optional[str] = "Sony1234!"
    bravia_host_02: Optional[str] = "192.168.111.225"
    bravia_use_https_02: Optional[bool] = False
    bravia_psk_02: Optional[str] = "sony123456789012"
    bluray_host: Optional[str] = "192.168.111.10"
    bluray_port: Optional[int] = 3336
    verbose: Optional[int] = 5
    
    

class ReadSettings():
    ### Class for reading settings.json
    def __init__(self):
        self.filename = "settings.json"
    
    def read_data(self):
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
                return ModelConfig(**data)
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.filename}")
            return False
    
    def save_data(self, config):
        try:
            with open(self.filename, "+w") as outfile:
                data = {}
                for k,v in iter(config):
                    ## Transcode BaseModel object to dict
                    print(f"{k} -> {v}")
                    data[k] = v
                json.dump(data, outfile, indent=4)
                return ModelConfig(**data)
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.filename}")
            return False

def ReadConfig():
    reader = ReadSettings()
    return reader.read_data()

def SaveConfig(config):
    reader = ReadSettings()
    reader.save_data(config=config)
    return reader.read_data()

if __name__ == "__main__":
    conf = ReadConfig()    
    if not conf:
        SaveConfig(config=ModelConfig())
        conf = ReadConfig()
    print(conf)