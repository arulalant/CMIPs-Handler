'''
This script will remove all the xml files from all the directories.
'''


import os

print "CAUTION : This script will remove / delete all the xml files from all the directories..."
srcpath = raw_input("Enter the source path : ")

for root, sub, files in os.walk(os.path.abspath(srcpath)):
    if files:
        for xml in files:
            if xml.endswith('xml'):
                fpath = os.path.join(root, xml)
                os.system('rm %s' % fpath)
                print "removed", fpath

         

