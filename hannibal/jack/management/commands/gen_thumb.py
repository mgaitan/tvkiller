from django.core.management.base import BaseCommand, CommandError
from thumbs.models import Thumb, Channel

import inotify
import os
import re
import datetime

class Command(BaseCommand):
    args = '<vid_file>'
    help = 'Generates thumbnails for video'

    def handle(self, *args, **options):
        # srcpath = '/aaaaa/bbbb/cccc/ddd/eeeeeee_ffffffff_gggg.avi'
        # ffmpeg_bin = '/usr/bin/ffmpeg'

        srcpath, ffmpeg_bin = args[:2]
        print srcpath, ffmpeg_bin

        file_name = srcpath[srcpath.rindex('/')+1:-4]
        #file_path = srcpath[:srcpath.rindex('/')+1]

        searchObj = re.search(r'(.*)_(.*)_(.*)_(.*)', file_name, re.M|re.I)
        fdevice = searchObj.group(1)
        fcamera = searchObj.group(2)
        fdate = searchObj.group(3)
        ftime = searchObj.group(4)

        # If channel doesn't exist, let the command die
        chan = Channel.objects.get(device_name=fdevice, device_slot=fcamera)

        file_dtime = datetime.datetime(int(fdate[:4]), 
                                          int(fdate[4:6]), 
                                          int(fdate[6:]), 
                                          int(ftime[:2]), 
                                          int(ftime[2:4]),
                                          int(ftime[4:]))

        finalpath = os.path.join(chan.base_dir(), fdate, ftime[:-2])

        try:
            os.makedirs(finalpath)
        except:
            pass    # probably folders exists.

        cmd = "%s -i %s -f image2 -vf fps=fps=1 %s"
        cmd = cmd % (ffmpeg_bin, srcpath, os.path.join(finalpath, '%03d.jpg'))
        os.system(cmd)

        ###
        # Here database query.
        ###
        thumbs_data = []
        a_second = datetime.timedelta(seconds=1)

        for f in sorted(os.listdir(finalpath)):
            file_dtime += a_second
            thumbs_data.append((file_dtime , os.path.join(finalpath, f)))
        import ipdb; ipdb.set_trace()

        Thumb.objects.bulk_create(
                [Thumb(channel=chan, datetime=d, filename=f) for d, f in thumbs_data])

