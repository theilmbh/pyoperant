import comedi
import base

class ComediError(Error):
    '''raised for problems communicating with the comedi driver'''
    pass


class ComediInterface(base.BaseInterface):
    """docstring for ComediInterface"""
    def __init__(self,device_name, *args,**kwargs):
        super(ComediInterface, self).__init__(*args,**kwargs)
        self.device_name = device_name
        self.device = None

    def open(self):
        self.device = comedi.comedi_open(self.device_name)
        if self.device < 0:
            raise ComediError('could not open device %s' % self.device_name)

    def close(self):
        s = comedi.comedi_close(self.device)
        if s < 0:
            raise ComediError('could not close device %s(%s)' % (self.device_name, self.device)

    def read(self,subdevice,channel):
        """ read from comedi port
        """
        (s,v) = comedi.comedi_dio_read(device,subdevice,channel)
        if s:
            return (not v)
        else:
            raise ComediError('could not read from device "%s", subdevice %s, channel %s' % (device,subdevice,channel))

    def write(self,subdevice,channel, value):
        """Write to comedi port
        """
        value = not value #invert the value for comedi
        s = comedi.comedi_dio_write(self.device,subdevice,channel,value)
        if s:
            return True
        else:
            raise ComediError('could not write to device "%s", subdevice %s, channel %s' % (device,subdevice,channel))

        


