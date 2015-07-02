from pyoperant import hwio, components, panels, utils
from pyoperant.interfaces import comedi_, pyaudio_
from pyoperant import InterfaceError
import time



dev_name_fmt = 'Adapter 1 (5316) - Output Stream %i'

class ZogAudioInterface(pyaudio_.PyAudioInterface):
    """docstring for ZogAudioInterface"""
    def __init__(self, *args, **kwargs):
        super(ZogAudioInterface, self).__init__(*args,**kwargs)
    def validate(self):
        super(ZogAudioInterface, self).validate()
        if self.wf.getframerate()==48000:
            return True
        else:
            raise InterfaceError('this wav file must be 48kHz')


class StarboardPanel(panels.BasePanel):
    """class for starboard boxes """
    def __init__(self,id=None, *args, **kwargs):
        super(StarboardPanel, self).__init__(*args, **kwargs)
        self.id = id

        # define interfaces
        self.interfaces['starboard'] = starboard.StarboardInterface(device_name=starboard_map)

        # define inputs
        for in_chan in range(4):
            self.inputs.append(hwio.BooleanInput(interface=self.interfaces['starboard'],
                                                 params = {'subdevice': _ZOG_MAP[self.id][1],
                                                           'channel': in_chan
                                                           },
                                                 )
                               )
        for out_chan in range(8):
            self.outputs.append(hwio.BooleanOutput(interface=self.interfaces['starboard'],
                                                 params = {'subdevice': _ZOG_MAP[self.id][3],
                                                           'channel': out_chan
                                                           },
                                                   )
                                )
        self.speaker = hwio.AudioOutput(interface=self.interfaces['pyaudio'])

        # assemble inputs into components
        self.left = components.PeckPort(IR=self.inputs[0],LED=self.outputs[0],name='l')
        self.center = components.PeckPort(IR=self.inputs[1],LED=self.outputs[1],name='c')
        self.right = components.PeckPort(IR=self.inputs[2],LED=self.outputs[2],name='r')
        self.house_light = components.HouseLight(light=self.outputs[3])
        self.hopper = components.Hopper(IR=self.inputs[3],solenoid=self.outputs[4])

        # define reward & punishment methods
        self.reward = self.hopper.reward
        self.punish = self.house_light.punish

    def reset(self):
        for output in self.outputs:
            output.write(False)
        self.house_light.on()
        self.hopper.down()
        # self.speaker.stop()

    def test(self):
        self.reset()
        dur = 2.0
        for output in self.outputs:
            output.write(True)
            utils.wait(dur)
            output.write(False)
        self.reset()
        self.reward(value=dur)
        self.punish(value=dur)
        self.speaker.queue('/usr/local/stimuli/test48k.wav')
        self.speaker.play()
        time.sleep(1.0)
        self.speaker.stop()
        return True



class Zog1(ZogPanel):
    """Zog1 panel"""
    def __init__(self):
        super(Zog1, self).__init__(id=1)



# define the panels with cue lights
class ZogCuePanel(ZogPanel):
    """ZogCuePanel panel"""
    def __init__(self,id=None):
        super(ZogCuePanel, self).__init__(id=id)

        for out_chan in [ii+_ZOG_MAP[self.id][4] for ii in range(5,8)]:
            self.outputs.append(hwio.BooleanOutput(interface=self.interfaces['comedi'],
                                                 params = {'subdevice': _ZOG_MAP[self.id][3],
                                                           'channel': out_chan
                                                           },
                                                   )
                                )
        self.cue = components.RGBLight(red=self.outputs[7],
                                       green=self.outputs[5],
                                       blue=self.outputs[6],
                                       name='cue')



# in the end, 'PANELS' should contain each operant panel available for use

PANELS = {
          "1": Zog1,

          }

BEHAVIORS = ['pyoperant.behavior',
             'glab_behaviors'
            ]

DATA_PATH = '/home/bird/opdat/'

# SMTP_CONFIG

DEFAULT_EMAIL = 'justin.kiggins@gmail.com'

SMTP_CONFIG = {'mailhost': 'localhost',
               'toaddrs': [DEFAULT_EMAIL],
               'fromaddr': 'Zog <bird@zog.ucsd.edu>',
               'subject': '[pyoperant notice] on zog',
               'credentials': None,
               'secure': None,
               }
