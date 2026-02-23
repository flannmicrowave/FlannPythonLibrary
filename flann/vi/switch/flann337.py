from enum import Enum

from flann.vi import FlannProgrammable

class SwitchNumber(Enum):
    '''Enum for switch numbers'''
    SWITCH_1 = 1
    SWITCH_2 = 2


class Switch337(FlannProgrammable):
    '''Class for Flann's 337 Programmable Switch Box'''
    def __init__(self, switch: SwitchNumber, address: str, timeout: float, baudrate: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
            
        self._resource.port = address
        self._resource.timeout = timeout
        self._resource.baudrate = baudrate
        self._resource.open()

        self._switch_number = switch

        self.series_number = '337'

        # id_str = self.id()
        # assert(self.series_number in id_str)

    @property
    def switch(self) -> int | None:
        '''Current selected switch'''
        return self._switch_number
    
    @switch.setter
    def switch(self, switch: SwitchNumber | None) -> None:
        '''Select switch, allowed values 1 or 2'''
        self._switch_number = switch

    @property
    def timeout(self) -> float | None:
        return self._resource.timeout
    
    @timeout.setter
    def timeout(self, timeout: float | None) -> None:
        self._resource.timeout = timeout

    @property
    def baudrate(self) -> int | None:
        return self._resource.baudrate
    
    @baudrate.setter
    def baudrate(self, baurate: int | None) -> None:
        self._resource.baudrate = baurate

    @property
    def id(self):
        '''Instrument ID string'''
        self.write('IDENTITY?')
        return self.read
    
    @property
    def position(self):
        '''Current selected switch position'''
        self.write(f'SWITCH{int(self._switch_number)}_POS?')
        return self.read()
    
    def position1(self):
        '''Selected switch position 1'''
        self.write(f'SWITCH{int(self._switch_number)}_POS1')
        self.read

    def position2(self):
        '''Selected switch position 2'''
        self.write(f'SWITCH{int(self._switch_number)}_POS2')
        self.read

    def toggle(self):
        '''Toggle selected switch'''
        self.write(f'SWITCH{int(self._switch_number)}_TOGGLE')
        self.read

    def toggle_all(self):
        '''Toggle all switches in switch box'''
        self.write('POSITION_TOGGLE')
        self.read