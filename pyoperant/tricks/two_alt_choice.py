#!/usr/bin/python

# from psychopy import core, data, logging, sound
from pyoperant.tricks import base
from pyoperant

class TwoAltChoiceExp(base.BaseExp):
    """docstring for Experiment"""
    def __init__(self,summaryDAT, *args, **kwargs):
        super(Experiment,  self).__init__(self, *args, **kwargs)

        # assign stim files full names
        for name, filename in self.parameters['stims'].items():
            filename_full = os.path.join(self.parameters['stim_path'], filename)
            self.parameters['stims'][name] = filename_full

        self.req_panel_attr.append(['speaker',
                                    'left',
                                    'center',
                                    'right',
                                    'reward',
                                    'punish',
                                    ])

                # configure csv file for data
        
        self.fields_to_save = ['index',
                               'type',
                               'trial_start',
                               'class',
                               'stim_string',
                               'response',
                               'response_time',
                               'feed',
                               'timeout',
                               ]

        self.trials = []

        self.data_csv = os.path.join(self.parameters['subject_path'], 
                                     self.parameters['subject_id']+'_trialdata_'+self.exp_timestamp+'.csv')
        self.session_index = 0

        if 'reinforcement' in self.parameters.keys():
            reinf = self.parameters['reinforcement']
            if reinf['schedule'] == 'variable_ratio':
                self.reinf_sched = reinf.VariableRatioSchedule(ratio=reinf['ratio'])
            elif reinf['schedule'] == 'fixed_ratio':
                self.reinf_sched = reinf.FixedRatioSchedule(ratio=reinf['ratio'])
            else:
                self.reinf_sched = reinf.ReinforcementSchedule()

        else:
            self.reinf_sched = reinf.ReinforcementSchedule()

    def make_data_csv(self):
        with open(self.data_csv, 'wb') as data_fh:
            trialWriter = csv.writer(data_fh)
            trialWriter.writerow(self.fields_to_save)

    ## session flow
    def check_session_schedule(self):
        return not self.check_light_schedule()

    def session_main(self):
        try:
            self._trial_flow()
            return 'main'
        except utils.GoodNite:
            return 'post'

    ## trial flow
    def new_trial(self):
        '''create a new trial and append it to the trial list'''
        try:
            last_trial = self.trials[-1]
            index = last_trial.index
        except IndexError:
            last_trial = None
            index = 0

        do_correction = False
        if last_trial is not None:
            if self.correction_trials and last_trial.response and last_trial.correct:
                do_correction = True
                    
        if do_correction:
            trial = Trial(tr_type='correction',
                          index=last_trial.index+1,
                          tr_class=last_trial.tr_class)
            for ev in last_trial.events:
                if ev.label is 'wav':
                    trial.events.append(ev[:])
                    trial.stimulus = correction.events[-1]
                elif ev.label is 'motif':
                    correction.events.append(ev[:])
            exp.log.debug("correction trial: class is %s" % trial.tr_class)
        else:
            trial = Trial(index=index)
            trial.tr_class = random.choice(exp.models.keys())
            trial_stim, trial_motifs = exp.get_stimuli(trial['class'])
            trial.events.append(trial_stim)
            trial.stimulus = trial.events[-1]
            for mot in trial_motifs:
                trial.events.append(mot)

        self.trials.append(trial)
        self.this_trial = self.trials[-1]
        self.this_trial_index = self.trials.index(self.this_trial)
        self.log.debug("trial %i: %s, %s" % (trial['index'],trial['type'],trial['class']))

        return True

    def get_stimuli(self,trial_class):
        # TODO: default stimulus selection
        pass

    def analyze_trial(self,trial_class):
        # TODO: calculate reaction times
        pass

    def save_trial(self,trial_dict):
        '''write trial results to CSV'''
        with open(self.data_csv,'ab') as data_fh:
            trialWriter = csv.DictWriter(data_fh,fieldnames=self.fields_to_save,extrasaction='ignore')
            trialWriter.writerow(trial_dict)

    def trial_pre(self):
        ''' this is where we initialize a trial'''
        # make sure lights are on at the beginning of each trial, prep for trial

        self.new_trial()

        self.this_trial = self.trials[-1]

        trial.min_epoch = trial_motifs[self.strlen_min-1]
        trial.min_wait = min_epoch.time + min_epoch.duration

        trial.max_wait = trial_stim.time + trial_stim.duration + self.response_win
        return 'main'

    def trial_main(self):
        self._stimulus_flow()
        self._response_flow()
        self._consequence_flow()
        return 'post'

    def trial_post(self):
        '''things to do at the end of a trial'''

        self.analyze_trial()
        self.save_trial(trial)
        self.write_summary()
        utils.wait(self.intertrial_min)
        return None

    def _trial_flow(self):
        try: 
            do_flow(pre=self.trial_pre,
                    main=self.trial_main,
                    post=self.trial_post)

        except hwio.CriticalError as err:
            self.log.critical(str(err))
            self.trial_post()

        except hwio.Error as err:
            self.log.error(str(err))
            self.trial_post()


    ## stimulus flow
    def stimulus_pre(self):
        # wait for bird to peck
        self.log.debug('waiting for peck...')
        self.panel.center.on()
        self.this_trial.time = panel.center.poll()
        self.panel.center.off()

        # record trial initiation
        self.summary['trials'] += 1
        self.summary['last_trial_time'] = self.this_trial.time.ctime()
        self.log.info("trial started at %s" % self.this_trial.time.ctime())
        return 'main'

    def stimulus_main(self):
        ## 1. play stimulus
        stim_start = dt.datetime.now()
        self.this_trial.stimulus.time = (stim_start - self.this_trial.time).total_seconds()
        self.wave_stream = panel.speaker.play_wav(trial.stimulus.file_origin)
        return 'post'

    def stimulus_post(self):
        utils.wait(self.min_wait)
        return None

    def _stimulus_flow(self):
        return do_flow(pre=self.stimulus_pre,
                       main=self.stimulus_main,
                       post=self.stimulus_post)

    #response flow
    def response_pre(self):
        self.panel.left.on()
        self.panel.right.on()
        return 'main'

    def response_main(self):
        while True:
            elapsed_time = (dt.datetime.now() - stim_start).total_seconds()
            if elapsed_time > self.max_wait:
                trial['response'] = 'none'
                break
            elif panel.left.status():
                trial['response_time'] = trial['stim_start'] + elapsed_time
                wave_stream.close()
                trial['response'] = 'L'
                self.summary['responses'] += 1
                break
            elif panel.right.status():
                trial['response_time'] = trial['stim_start'] + elapsed_time
                wave_stream.close()
                trial['response'] = 'R'
                self.summary['responses'] += 1
                break
        return 'post'

    def response_post(self):
        self.panel.left.off()
        self.panel.right.off()
        return None

    def response_flow(self):
        return do_flow(pre=self.response_pre,
                       main=self.response_main,
                       post=self.response_post)

    ## consequence flow
    def consequence_pre(self):
        return 'main'

    def consequence_main(self):
        # correct trial
        if self.this_trial.response is self.this_trial.tr_class:
            self.this_trial.correct = True
            
            if self.parameters['reinforcement']['secondary']:
                secondary_reinf_event = self.secondary_reinforcement()
                self.this_trial.events.append(secondary_reinf_event)

            if self.trial.type == 'correction':
                pass

            elif self.reinf_sched.consequate(trial=self.this_trial):
                self._reward_flow()
        # no response
        elif self.trial.response is 'none':
            pass

        # incorrect trial
        else:
            self.this_trial.correct = False
            if self.reinf_sched.consequate(trial=self.this_trial):
                self._punish_flow()
        return 'post'

    def consequence_post(self):
        self.this_trial.duration = (dt.datetime.now() - self.this_trial.time).total_seconds()
        return None

    def _consequence_flow(self):
        return do_flow(pre=self.consequence_pre,
                       main=self.consequence_main,
                       post=self.consequence_post)


    def secondary_reinforcement(self,value=1.0):
        return self.panel.center.flash(dur=value)

    ## reward flow
    def reward_pre(self):
        return 'main'

    def reward_main(self):
        self.summary['feeds'] += 1
        try:
            feed_event = self.panel.reward(value=self.feed_dur[trial['class']])
            self.this_trial.events.append(feed_event)

        # but catch the feed errors

        except components.HopperActiveError as err:
            trial['feed'] = 'Error'
            self.summary['hopper_already_up'] += 1
            self.log.warning("hopper already up on panel %s" % str(err))
            utils.wait(exp.feed_dur[trial['class']])
            self.panel.reset()

        except components.HopperInactiveError as err:
            trial['feed'] = 'Error'
            self.summary['hopper_failures'] += 1
            self.log.error("hopper didn't come up on panel %s" % str(err))
            utils.wait(exp.feed_dur[trial['class']])
            self.panel.reset()

        # except components.ResponseDuringFeedError as err:
        #     trial['feed'] = 'Error'
        #     exp.summary['responses_during_feed'] += 1
        #     exp.log.error("response during feed on panel %s" % str(err))
        #     utils.wait(exp.feed_dur[trial['class']])
        #     panel.reset()

        # except components.HopperDidntDropError as err:
        #     trial['feed'] = 'Error'
        #     exp.summary['hopper_wont_go_down'] += 1
        #     exp.log.warning("hopper didn't go down on panel %s" % str(err))
        #     panel.reset()

        finally:
            self.panel.house_light.on()

            # TODO: add errors as trial events

        return 'post'

    def reward_post(self):
        return None

    def _reward_flow(self):
        return do_flow(pre=self.reward_pre,
                       main=self.reward_main,
                       post=self.reward_post)

    ## punishment flow
    def punish_pre(self):
        return 'main'

    def punish_main(self):
        punish_event = self.panel.punish(value=self.timeout_dur[trial['class']])
        self.this_trial.events.append(punish_event)
        self.this_trial.punish = True
        return 'post'

    def punish_post(self):
        return None

    def _punish_flow(self):
        return do_flow(pre=self.punish_pre,
                       main=self.punish_main,
                       post=self.punish_post)

            


