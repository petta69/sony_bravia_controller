import socket
import ipaddress
from typing import Optional

def validate_ipaddress(host_string):
    try:
        ip_object = ipaddress.ip_address(host_string)
        return ip_object
    except ValueError:
        print(f'ERROR: Could not validate ip: {host_string}')
        return 0
    
class bluray_player:
    def __init__(self, host_ip: str, port=3336, verbose=1) -> None:
        if validate_ipaddress:
            self._location = (host_ip, port)
        else:
            return False
        
    def _connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(30)
        self._sock.connect(self._location)
        ## When connection is made we will first get notification on power
        response_notify = self._receive_response()
        ## Next notification transmission is about AudioMute, AudioVol and PictureMute
        response_notify = self._receive_response()        

    def _close_connection(self):
        self._sock.close()
        
    def _send_command(self, command: dict) -> Optional[str]:
        ## First we make the connection
        self._connect()

        ## Now send command
        message = f'{command}\n'
        message_binary = str.encode(message, "utf-8")

        self._sock.send(message_binary)
        try:
            response = self._receive_response()
        except:
            response = []

        ## Close connection
        self._close_connection
        return response
        
    def _receive_response(self) -> Optional[dict]:
        response_payload = ""
        while True:
            try:
                # # We read 96 bytes at the time
                response = self._sock.recv(96)
                # # Now add to our response_payload
                response_payload = f"{response_payload}{response.decode('utf-8')}"
                if response_payload.endswith('\n'):
                    return response_payload
                else: 
                    return response_payload

            except socket.timeout:
                break    
            

    ##
    ## Defined commands
    ##

    def set_eject_disc(self):
        command = {
            "type": "set",
            "feature": "gui.ejectdisc",
            "value": "pulse"
        }
        self._send_command(command=command)

    def play(self):
        command = {
            "type": "set",
            "feature": "gui.play",
            "value": "pulse"
        }
        self._send_command(command=command)

    def pause(self):
        command = {
            "type": "set",
            "feature": "gui.pause",
            "value": "pulse"
        }
        self._send_command(command=command)


if __name__ == "__main__":
    player = bluray_player(host_ip="192.168.111.228", verbose=5)
    player.set_eject_disc()
    
    