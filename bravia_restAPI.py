import requests
import ipaddress
import sys

from logger import Logger


requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


class BRAVIA_RESTAPI:
    def __init__(self, host_ip: str, psk: str):
        self.logger = Logger().get_logger()
        if self.validate_ipaddress(host_string=host_ip):
            self._host_ip = host_ip
            self._headers = {'X-Auth-PSK': f'{psk}'}
            self.logger.debug(f'Will use HOST IP: {self._host_ip}')
        else:
            self.logger.error(f'ERROR: {host_ip} is not a valid IP')
            return False
    
    def validate_ipaddress(self, host_string):
        try:
            ip_object = ipaddress.ip_address(host_string)
            return ip_object
        except ValueError:
            self.logger.error(f'ERROR: Could not validate ip: {host_string}')
            return 0
        
        
    ## Functions    
    def get_power_status(self):
        command_url = f'https://{self._host_ip}/sony/system'
        payload = {
                    "method": "getPowerStatus",
                    "id": 50,
                    "params": [],
                    "version": "1.0"
                }
        r = requests.post(command_url, json=payload, headers=self._headers, verify=False)
        self.logger.info(f'Trying: {r.url}')
        self.logger.info(f'Status: {r.status_code}')
        self.logger.info(f'Response: {r.text}')
        return r.json()
        
    def set_power(self, state: str):
        if state.lower() not in ['on', 'off']:
            state = True
        elif state.lower() == 'on':
            state = True
        elif state.lower() == 'off':
            state = False
        command_url = f'https://{self._host_ip}/sony/system'
        payload = {
                    "method": "setPowerStatus",
                    "id": 50,
                    "params": [{"status": state}],
                    "version": "1.0"
                }
        r = requests.post(command_url, json=payload, headers=self._headers, verify=False)
        self.logger.info(f'Trying: {r.url}')
        self.logger.info(f'Status: {r.status_code}')
        self.logger.info(f'Response: {r.text}')
        
        
        
        
    def set_brightness(self, brightness: int):
        command_url = f'https://{self._host_ip}/sony/video'
        payload = {
                    "method": "setPictureQualitySettings",
                    "id": 50,
                    "params": [{"settings": [{
                        "value": f"{brightness}",
                        "target": "brightness"
                        }]}],
                    "version": "1.0"
                }
        self.logger.info(payload)
        r = requests.post(command_url, json=payload, headers=self._headers, verify=False)
        self.logger.info(f'Trying: {r.url}')
        self.logger.info(f'Status: {r.status_code}')
        self.logger.info(f'Response: {r.text}')
        
    def get_brightness(self):
        command_url = f'https://{self._host_ip}/sony/video'
        payload = {
                    "method": "getPictureQualitySettings",
                    "id": 50,
                    "params": [{"target": "brightness"}],
                    "version": "1.0"
                }
        r = requests.post(command_url, json=payload, headers=self._headers, verify=False)
        self.logger.info(f'Trying: {r.url}')
        self.logger.info(f'Status: {r.status_code}')
        self.logger.info(f'Response: {r.text}')
        return r.json()

        
if __name__ == "__main__":
    bravia1 = BRAVIA_RESTAPI(host_ip='192.168.111.223', psk='sony123456789012')
    bravia2 = BRAVIA_RESTAPI(host_ip='192.168.111.96', psk='Sony1234!')
    
    br1_pwr = bravia1.get_power_status()
    br2_pwr = bravia2.get_power_status()

    print(f"Bravia1 Power Status: {br1_pwr}")
    print(f"Bravia2 Power Status: {br2_pwr}")
    