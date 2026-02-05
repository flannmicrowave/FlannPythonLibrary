import serial
import serial.serialwin32

import socket

import time

class FlannProgrammable:
    '''Default class for all Flann programmable instruments'''
    def __init__(self, timedelay: float=0, is_serial: bool=True):
        if is_serial:
            self._resource = serial.Serial(stopbits=1, parity=serial.PARITY_NONE, bytesize=8, xonxoff=True)  # Windows COM port
        else:
            self._resource = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 and TCP

        self._timedelay = timedelay

    @property
    def timedelay(self) -> float | None:
        return self._timedelay
    
    @timedelay.setter
    def timedelay(self, timedelay: float | None) -> None:
        self._timedelay = timedelay

    def close(self):
        self._resource.close()

    def read(self):
        time.sleep(self._timedelay)
        if isinstance(self._resource, serial.serialwin32.Serial):
            fn = self._resource.readline().decode()
        elif isinstance(self._resource, socket.socket):
            fn = self._resource.recv(1024).decode(errors='ignore')
        else:
            raise RuntimeError("read unreachable")
        return fn.rstrip()

    def write(self, cmd: str):
        time.sleep(self._timedelay)
        if isinstance(self._resource, serial.serialwin32.Serial):
            fn = self._resource.write
        elif isinstance(self._resource, socket.socket):
            fn = self._resource.sendall
        else:
            raise RuntimeError("write unreachable")
        return fn(cmd.encode())


    