import comedi
import subprocess, datetime
from os.path import join
from pyoperant.interfaces import base_
from pyoperant import utils, InterfaceError



stbd_port_dir = "/sys/class/leds/"
stbd_port_dict = {
                    "0": "starboard\:center\:blue/"
                    "1": "starboard\:center\green/:"
                    "2": "starboard\:center\:red/"
                    "3": "starboard\:left\:blue/"
                    "4": "starboard\:left\green/:"
                    "5": "starboard\:left\:red/"
                    "6": "starboard\:right\:blue/"
                    "7": "starboard\:right\green/:"
                    "8": "starboard\:right\:red/"
                    "9": "starboard\:hopper\:left/"
                    "10": "starboard\:hopper\:right/"
                    "11": "starboard\::lights/"
}

class StarboardInterface(base_.BaseInterface):
    """docstring for ComediInterface"""
    def __init__(self,device_name,*args,**kwargs):
        super(StarboardInterface, self).__init__(*args,**kwargs)
        self.device_name = device_name
        self.read_params = ('channel')
        self.open()

    def open(self):
        pass

    def close(self):
        pass

    def _config_read(self,channel):
        return True

    def _config_write(self,channel):

        return True

    def _read_bool(self, channel):
        """ read from Starboard port
        """
        (s,v) = comedi.comedi_dio_read(self.device,subdevice,channel)
        if s:
            return (not v)
        else:
            raise InterfaceError('could not read from comedi device "%s", subdevice %s, channel %s' % (self.device,subdevice,channel))

    def _poll(self,subdevice,channel,timeout=None):
        """ runs a loop, querying for pecks. returns peck time or "GoodNite" exception """
        date_fmt = '%Y-%m-%d %H:%M:%S.%f'
        cmd = ['comedi_poll', self.device_name, '-s', str(subdevice), '-c', str(channel)]
        poll_command = utils.Command(cmd)
        status, output, error = poll_command.run(timeout=timeout)
        if status < 0:
            return None
        else:
            timestamp = output
            return datetime.datetime.strptime(timestamp.strip(),date_fmt)

    def _write_bool(self,channel,value):
        """Write to Starboard port
        """
        value  #invert the value for comedi
        fname = join(stbd_port_dir, stbd_port_dict[channel], 'brightness')
        try:
            with open(fname, 'w') as fd:
                fd.write(value)
                return True
        except IOError:
            raise InterfaceError('Could not write to Starboard Port "%s" with value %d' % (channel, value))
   



