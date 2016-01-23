# Copyright (c) 2014-2016 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# Copyright (C) 2010 Jonathan Matthew (replay gain code)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gst

from lollypop.define import Lp


class ReplayGainPlayer:
    """
        Replay gain player
    """

    def __init__(self, playbin):
        """
            Init replay gain on playbin
            @param playbin as Gst play bin
        """
        rgfilter = Gst.ElementFactory.make("bin", "bin")

        rg_audioconvert1 = Gst.ElementFactory.make("audioconvert",
                                                   "audioconvert1")
        rg_audioconvert2 = Gst.ElementFactory.make("audioconvert",
                                                   "audioconvert2")

        self.rgvolume = Gst.ElementFactory.make("rgvolume",
                                                "rgvolume")
        rglimiter = Gst.ElementFactory.make("rglimiter",
                                            "rglimiter")
        rg_audiosink = Gst.ElementFactory.make("autoaudiosink",
                                               "autoaudiosink")

        if not rgfilter or not rg_audioconvert1 or\
           not rg_audioconvert2 or not self.rgvolume or\
           not rglimiter or not rg_audiosink:
            print("Replay Gain not available, ")
            print("please check your gstreamer installation...")
            return

        if self.rgvolume is not None:
            self.rgvolume.props.album_mode = 1
            self.rgvolume.props.pre_amp = Lp().settings.get_value(
                "replaygain").get_double()

        rgfilter.add(self.rgvolume)
        rgfilter.add(rg_audioconvert1)
        rgfilter.add(rg_audioconvert2)
        rgfilter.add(rglimiter)
        rgfilter.add(rg_audiosink)

        rg_audioconvert1.link(self.rgvolume)
        self.rgvolume.link(rg_audioconvert2)
        self.rgvolume.link(rglimiter)
        rg_audioconvert2.link(rg_audiosink)

        rgfilter.add_pad(Gst.GhostPad.new(
                               "sink",
                               rg_audioconvert1.get_static_pad("sink")))
        playbin.set_property("audio-sink", rgfilter)
