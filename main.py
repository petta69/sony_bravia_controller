#!/bin/python3

import sys
import os
import time
import timeit

from enum import Enum
from fastapi import FastAPI, Request, Form, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

## Get settings and store in dict
from settings import ReadConfig, ModelConfig, SaveConfig
config = ReadConfig()

## Configure logger object
from logger import Logger
logger = Logger(name=__name__, level=config.verbose, file_path="/tmp/rsony_bravia_controller.txt").get_logger()

from bravia_restAPI import BRAVIA_RESTAPI
from lib.system import reboot_rpi


app = FastAPI(title="RPI5 Control")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")


flood_oldfunction = "none"
flood_oldtime = timeit.default_timer()
clients = []

class ModelBRAVIA(str, Enum):
     '''
     Valid functions for the BRAVIA class
     '''
     SetBrightness10 = "SetBrightness10"
     SetBrightness25 = "SetBrightness25"
     SetBrightness49 = "SetBrightness49"
     SetPowerOn = "SetPowerOn"
     SetPowerOff = "SetPowerOff"


class ModelBluRay(str, Enum):
    '''
    Valid functions for the BluRay class
    '''
    SetPowerOn = "SetPowerOn"
    SetPowerOff = "SetPowerOff"
    Play = "Play"
    Pause = "Pause"
    Stop = "Stop"

class ModelSystem(str, Enum):
    '''
    Valid functions for the system class
    '''
    Restart = "Restart"

def check_flooding(flood_function, flood_timeout=5):
    global flood_oldfunction
    global flood_oldtime
    now = timeit.default_timer()
    if flood_function == flood_oldfunction:
        if now - flood_oldtime < flood_timeout:
            flood_oldtime = now
            return True
        else:
            flood_oldtime = now
            return False
    else:
        flood_oldfunction = flood_function
        flood_oldtime = now
        return False
    

##
## API calls
##

## BRAVIA
@app.get("/api/bravia/{function}")
async def bravia_api_function(function: ModelBRAVIA):
    result = []
    if check_flooding(function.value):
        return {'Error': 'Flooding'}
    try:
        config = ReadConfig()
        bravia1 = BRAVIA_RESTAPI(host_ip=config.bravia_host_01, psk=config.bravia_psk_01)
        bravia2 = BRAVIA_RESTAPI(host_ip=config.bravia_host_02, psk=config.bravia_psk_02)
    except:
        return {"ERROR": "Could not connect to host"}
    if function is ModelBRAVIA.SetBrightness10:
        result.append(srgcgi_controller.srg_start_autoframing())
    elif function is ModelSRGCGI.AutoFramingStop:
        result.append(srgcgi_controller.srg_stop_autoframing())
    elif function is ModelSRGCGI.Preset1:
        result.append(srgcgi_controller.srg_stop_autoframing())
        result.append(srgcgi_controller.srg_recall_preset(presetpos=1))
    elif function is ModelSRGCGI.Preset2:
        result.append(srgcgi_controller.srg_stop_autoframing())
        result.append(srgcgi_controller.srg_recall_preset(presetpos=2))
    return result





## TemplateResponse
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    config = ReadConfig()
    return templates.TemplateResponse(
        request=request, name="index.html"
    )



@app.get("/zrct300", response_class=HTMLResponse)
async def zrct300(request: Request, function: ModelADCP | None=None):
    ## If we get a function we need to execute that action. Result is used to print status.
    config = ReadConfig()
    context = {}
    if function:
        result = await adcp_api_function(function)
        ## Create context to pass to bootstrap
        context["status"] = result

    return templates.TemplateResponse(
        request=request, name="zrct300.html", context=context
    )

@app.get("/srg", response_class=HTMLResponse)
async def srg(request: Request, function: ModelSRGCGI | None=None):
    ## If we get a function we need to execute that action. Result is used to print status.
    config = ReadConfig()
    context = {}
    if function:
        result = await srgcgi_api_function(function)
        ## Create context to pass to bootstrap
        context["status"] = result

    return templates.TemplateResponse(
        request=request, name="srg.html", context=context
    )

@app.get('/settings', response_class=HTMLResponse)
async def settings(request: Request):
    ## Uses settings.json to print all valid keys and values
    config = ReadConfig()
    settings = {}
    context = {}
    for k,v in iter(config):
        ## Transcode BaseModel object to dict
        print(f"{k} -> {v}")
        settings[k] = v
    context['config'] = settings
    ## Read schedule
    cron_read = read_crontab(cron_user=current_user)
    context['config'].update(cron_read)
    return templates.TemplateResponse(
        request=request, name="settings.html", context=context
    )

@app.post('/settings')
async def settings_update(request: Request, 
                          vlc_default_videodir: str = Form(config.vlc_default_videodir),
                          vlc_custom_usb_videodir: str = Form(config.vlc_custom_usb_videodir),
                          adcp_host: str = Form(config.adcp_host),
                          adcp_port: int = Form(config.adcp_port),
                          adcp_password: str = Form(config.adcp_password),
                          adcp_use_schedule: bool = Form(False),
                          srgcgi_host: str = Form(config.srgcgi_host),
                          srgcgi_port: int = Form(config.srgcgi_port),
                          srgcgi_username: str = Form(config.srgcgi_username),
                          srgcgi_password: str = Form(config.srgcgi_password),
                          deconz_active: bool = Form(config.deconz_active),
                          deconz_min_lux: str = Form(config.deconz_min_lux),
                          deconz_max_lux: str = Form(config.deconz_max_lux),
                          deconz_cled_type: str = Form(config.deconz_cled_type),
                          verbose: int = Form(config.verbose),
                          monday_active: bool = Form(False),
                          tuesday_active: bool = Form(False),
                          wednesday_active: bool = Form(False),
                          thursday_active: bool = Form(False),
                          friday_active: bool = Form(False),
                          saturday_active: bool = Form(False),
                          sunday_active: bool = Form(False),
                          monday_on: str = Form(...),
                          monday_off: str = Form(...),
                          tuesday_on: str = Form(...),
                          tuesday_off: str = Form(...),
                          wednesday_on: str = Form(...),
                          wednesday_off: str = Form(...),
                          thursday_on: str = Form(...),
                          thursday_off: str = Form(...),
                          friday_on: str = Form(...),
                          friday_off: str = Form(...),
                          saturday_on: str = Form(...),
                          saturday_off: str = Form(...),
                          sunday_on: str = Form(...),
                          sunday_off: str = Form(...)
                          ):
        
    ## Process for crontab
    if adcp_use_schedule:
        settings_cron = {
            'monday_active': monday_active,
            'monday_on': monday_on,
            'monday_off': monday_off,
            'tuesday_active': tuesday_active,
            'tuesday_on': tuesday_on,
            'tuesday_off': tuesday_off,
            'wednesday_active': wednesday_active,
            'wednesday_on': wednesday_on,
            'wednesday_off': wednesday_off,
            'thursday_active': thursday_active,
            'thursday_on': thursday_on,
            'thursday_off': thursday_off,
            'friday_active': friday_active,
            'friday_on': friday_on,
            'friday_off': friday_off,
            'saturday_active': saturday_active,
            'saturday_on': saturday_on,
            'saturday_off': saturday_off,
            'sunday_active': sunday_active,
            'sunday_on': sunday_on,
            'sunday_off': sunday_off
        }
        remove_crontab(cron_user=current_user)
        write_crontab(cron_user=current_user, cron_dict=settings_cron)
    else:
        remove_crontab(cron_user=current_user)

    ## After pressing submit we need to save dict to settings.json
    data = {
        'vlc_default_videodir': vlc_default_videodir,
        'vlc_custom_usb_videodir': vlc_custom_usb_videodir,
        'adcp_host': adcp_host,
        'adcp_port': adcp_port,
        'adcp_password': adcp_password,
        'adcp_use_schedule': adcp_use_schedule,
        'srgcgi_host': srgcgi_host,
        'srgcgi_port': srgcgi_port,
        'srgcgi_username': srgcgi_username,
        'srgcgi_password': srgcgi_password,
        'deconz_active': deconz_active,
        'deconz_min_lux': deconz_min_lux,
        'deconz_max_lux': deconz_max_lux,
        'deconz_cled_type': deconz_cled_type,
        'verbose': verbose
    }
    data_config = ModelConfig(**data)
    ## This save also read out the updated config
    config = SaveConfig(data_config)

    settings = {}
    context = {}
    for k,v in iter(config):
        ## Transcode BaseModel object to dict
        print(f"{k} -> {v}")
        settings[k] = v
    context['config'] = settings
    cron_read = read_crontab(cron_user=current_user)
    context['config'].update(cron_read)

    return templates.TemplateResponse(
        request=request, name="settings.html", context=context
    )

## WebSocket connection
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        clients.remove(websocket)
        
async def notify_clients(status_text):
    logger.debug(f"Sending updated status: {status_text}")
    for client in clients:
        await client.send_text(str(status_text))
        time.sleep(2)
        

if(__name__) == '__main__':
        import uvicorn
        uvicorn.run(
        "main:app",
        host    = "0.0.0.0",
        port    = 5000, 
        reload  = True
    )