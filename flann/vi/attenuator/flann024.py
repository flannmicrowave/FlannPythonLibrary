from flann.vi import FlannProgrammable


class Attenuator024(FlannProgrammable):
    '''Class for Flann's 024 Programmable Attenuator'''
    def __init__(self, address: str, timeout: float, baudrate: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._resource.port = address
        self._resource.timeout = timeout
        self._resource.baudrate = baudrate
        self._resource.open()

        self.series_number = '024'

        id_str = self.id()
        assert(self.series_number in id_str)

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
        self.write('CL_IDENTITY?#')
        return self.read
    
    @property
    def instrument_status(self):
        '''Instrument status'''
        self.write('CL_INST_STAT?#')
        return self.read
    
    def reset(self):
        '''Reset instrument.'''
        self.write('CL_RESET_INST#')

    @property
    def attenuation(self):
        '''Current attenuation [dB]'''
        self.write('CL_VALUE_SET?#')
        return self.read
    
    @attenuation.setter
    def attenuation(self, atten_db):
        '''Allowed values between 0-50 dB with 0.1 dB precision'''
        if 0 <= atten_db <= 50:
            self.write(f'CL_VALUE_SET {atten_db}#')
            self.read()
        else:
            raise(ValueError('Not an excepted attenuation'))
        
    @property
    def position(self):
        '''Current Step Position'''
        raise(NotImplementedError)
    
    @position.setter
    def position(self, steps):
        '''Allowed values between 0-8000'''
        if all([0<=steps<=8000,isinstance(steps,int)]):
            steps = str(steps)
            steps = steps.zfill(4)
            print(steps)
            self.write(f'CL_STEPS_SET {steps}#')
            # self.read  # Currently not implemented in the device
        else:
            raise(ValueError('Not an excepted steps position'))
        
    @property
    def increment_store(self):
        '''Current incremental value [dB]'''
        self.write('CL_INCR_SET?#')
        return self.read
    
    @increment_store.setter
    def increment_store(self, increment):
        '''Allowed values between 0-10 dB'''
        if 0 <= increment <= 10:
            self.write(f'CL_INCR_SET {increment}#')
            self.read
        else:
            raise(ValueError('Not an excepted incrementation'))
        
    def increment(self):
        self.write('CL_INCREMENT#')
        self.read

    def decrement(self):
        self.write('CL_DECREMENT#')
        self.read
