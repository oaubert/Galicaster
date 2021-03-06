# -*- coding:utf-8 -*-
# Galicaster, Multistream Recorder and Player
#
#       galicaster/recorder/bins/autoaudio
#
# Copyright (c) 2014, Teltek Video Research <galicaster@teltek.es>
#
# This work is licensed under the Creative Commons Attribution-
# NonCommercial-ShareAlike 3.0 Unported License. To view a copy of 
# this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California, 94105, USA.

import gobject
import gst
from os import path

from galicaster.recorder import base
from galicaster.recorder import module_register

pipestr = (" autoaudiosrc name=gc-autoaudio-src  ! queue ! audioamplify name=gc-autoaudio-amplify amplification=1 ! "
           " tee name=tee-aud  ! queue ! level name=gc-autoaudio-level message=true interval=100000000 ! "
           " volume name=gc-autoaudio-volume ! alsasink sync=false name=gc-autoaudio-preview  "
           " tee-aud. ! queue ! valve drop=false name=gc-autoaudio-valve ! "
           " audioconvert ! gc-autoaudio-enc ! "
           " queue ! filesink name=gc-autoaudio-sink async=false " )


class GCautoaudio(gst.Bin, base.Base):
    
    order = ["name", "flavor", "location", "file", 
             "vumeter", "player", "amplification", "audioencoder"]

    gc_parameters = {
        "name": {
            "type": "text",
            "default": "Autoaudio",
            "description": "Name assigned to the device",
            },
        "flavor": {
            "type": "flavor",
            "default": "presenter",
            "description": "Matterhorn flavor associated to the track",
            },
        "location": {
            "type": "device",
            "default": "default",
            "description": "Device's mount point of output",
            },
        "file": {
            "type": "text",
            "default": "sound.mp3",
            "description": "The file name where the track will be recorded.",
            },
        "vumeter": {
            "type": "boolean",
            "default": "True",
            "description": "Activate Level message",
            },
        "player": {
            "type": "boolean",
            "default": "True",
            "description": "Enable sound play",
            },
        "amplification": {
            "type": "float",
            "default": 1.0,
            "range": (0,10),
            "description": "Audio amplification",
            },
        "audioencoder": {
            "type": "text",
            "default": "lamemp3enc target=1 bitrate=192 cbr=true",
            "description": "Gstreamer audio encoder element used in the bin",
            },
        }

    is_pausable = True
    has_audio   = True
    has_video   = False
    
    __gstdetails__ = (
        "Galicaster Audio BIN",
        "Generic/Audio",
        "Plugin to capture raw audio through a default device",
        "Teltek Video Research"
        )

    def __init__(self, options={}): 
        base.Base.__init__(self, options)
        gst.Bin.__init__(self, self.options["name"])

        aux = (pipestr.replace("gc-autoaudio-preview", "sink-" + self.options["name"])
                      .replace("gc-autoaudio-enc", self.options["audioencoder"]))

        #bin = gst.parse_bin_from_description(aux, True)
        bin = gst.parse_launch("( {} )".format(aux))
        self.add(bin)

        if self.options['location'] != "default":
            sink = self.get_by_name("gc-autoaudio-src")
            sink.set_property("device", self.options['location'])


        sink = self.get_by_name("gc-autoaudio-sink")
        sink.set_property('location', path.join(self.options['path'], self.options['file']))

        if "player" in self.options and self.options["player"] == False:
            self.mute = True
            element = self.get_by_name("gc-autoaudio-volume")
            element.set_property("mute", True)
        else:
            self.mute = False

        if "vumeter" in self.options:
            level = self.get_by_name("gc-autoaudio-level")
            if self.options["vumeter"] == False:
                level.set_property("message", False) 
        if "amplification" in self.options:
            ampli = self.get_by_name("gc-autoaudio-amplify")
            ampli.set_property("amplification", float(self.options["amplification"]))


    def changeValve(self, value):
        valve1=self.get_by_name('gc-autoaudio-valve')
        valve1.set_property('drop', value)

    def getVideoSink(self):
        return self.get_by_name("gc-autoaudio-preview")

    def getAudioSink(self):
        return self.get_by_name("gc-autoaudio-preview")

    def getSource(self):
        return self.get_by_name("gc-autoaudio-src")

    def send_event_to_src(self, event):
        src1 = self.get_by_name("gc-autoaudio-src")
        src1.send_event(event)        

    def mute_preview(self, value):
        if not self.mute:
            element = self.get_by_name("gc-autoaudio-volume")
            element.set_property("mute", value)

    
gobject.type_register(GCautoaudio)
gst.element_register(GCautoaudio, "gc-alsa-bin")
module_register(GCautoaudio, 'alsa')
