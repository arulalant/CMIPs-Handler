'''
This script will remove all the empty directories.
'''

import os

srcpath = raw_input("Enter the source path : ")

for root, sub, files in os.walk(os.path.abspath(srcpath)):
    
    if not sub and not files:
        fpath = os.path.join(root)
        os.system('rmdir %s' % fpath)
        print "removed", fpath

         

