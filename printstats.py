#!/usr/bin/env python
"""
This is for testing execution time of the cclskim.py program.
"""

import pstats
import os

def goCprofile(profFN):
    profFN = os.path.expanduser(profFN)
    p = pstats.Stats(profFN)

#p.strip_dirs() #strip path names

#p.sort_stats('cumulative').print_stats(10) #print 10 longest function
#p.print_stats()

    p.sort_stats('time','cumulative').print_stats(20)
#p.print_stats()
