'''
This script will remove the directories if that contains only xml files.
'''

import os

srcpath = raw_input("Enter the source path : ")

for root, sub, files in os.walk(os.path.abspath(srcpath)):
    if files:
        files = [f for f in files if not f.endswith('.xml')]
        if not files:
            fpath = os.path.join(root)
            os.system('rm -rf %s' % fpath)
            print "removed", fpath

         

