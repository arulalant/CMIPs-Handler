import os, re, datetime
from subprocess import Popen, PIPE


__OVERWRITE = 0


def isModifiedToday(path):
    # get the last modified timestamp of folder/file as seconds
    mod_sec = os.path.getmtime(path)
    mod_date = datetime.datetime.fromtimestamp(mod_sec).date()

    if mod_date.toordinal() == mod_date.today().toordinal():
        # folder/file is modified by today  
        return True
    else:
        # The folder/file is not modified by today
        return False
    # end of if mod_date.toordinal() == mod_date.today().toordinal():
# end of def isModifiedToday(path):


def doCdscan(datapath, extension='nc', logpath=None, **kwarg):
    """

    Written By : Arulalan.T

    Date : 07.09.2012

    """

    xmlfile = kwarg.get('xmlfile', None)
    modifiedToday = kwarg.get('modifiedToday', False)
    skipdirs = kwarg.get('skipdirs', ['Annual'])
    
    if not xmlfile:
        fsplit = ''
        fjoin = ''
        flen = 0
        if 'fsplit' in kwarg:
            fsplit = kwarg.get('fsplit')
        if 'fjoin' in kwarg:
            fjoin = kwarg.get('fjoin')
        if 'flen' in kwarg:
            flen = kwarg.get('flen')
    # end of if not xmlfile:

    if not logpath:
        logpath = os.path.join(os.path.abspath(os.curdir), 'cdscanlog')
    # end of if not logpath:
    for subdir in ['info', 'warning', 'error']:
        subpath = os.path.join(logpath, subdir)
        if not os.path.isdir(subpath):
            os.makedirs(subpath)
        # end of if not os.path.isdir(subpath):
    # end of for subdir in ['info', 'warning', 'error']:

    success = os.path.join(logpath, 'success.log')
    successfile = open(success, 'w')
    successfile.write("Successfully created xml files, \n\n")

    warning = os.path.join(logpath, 'warning.log')
    warningfile = open(warning, 'w')
    warningfile.write("Warning while creating xml files, \n\n")

    failure = os.path.join(logpath, 'failure.log')
    failurefile = open(failure, 'w')
    failurefile.write("Failured to create xml files, \n\n")

    for root, sub, files in os.walk(os.path.abspath(datapath)):
    
        # removing the skip directories without visting
        for skipdir in skipdirs:
            if skipdir in sub:
                sub.remove(skipdir)
            # end if skipdir in sub:
        # end of for skipdir in skipdirs:
        
        if files:
            if (modifiedToday and not isModifiedToday(root)):
                print "The path %s is not modified today, \
                        so skip it without doing cdscan" % root
                warningfile.write("The path %s is not modified today, \
                                so skip it without doing cdscan" % root)
                continue            
            # end of if (modifiedToday and ...):

            if xmlfile:
                outfile = xmlfile
                fname = xmlfile.split('.xml')[0]
            else:
                files = [f for f in files if f.endswith('.'+extension)]
                if fsplit:
                    # split the file by user defined
                    fname = files[0].split(fsplit)
                    # join the splitted filename by user defined
                    fname = fjoin.join(fname[:flen])
                else:
                    # split the file by its extension
                    fname = files[0].split('.' + extension)[0]
                # end of if fsplit:
                # generate the xml file name
                outfile = fname + '.xml'
            # end of if xmlfile:

            # change the current working directory path into this directory
            os.chdir(root)
            # remove the existing xml file for the purpose to find out the
            # cdscan problem while creating html table of the dataset.
            if os.path.isfile('./' + outfile) and __OVERWRITE:
                # remove all the xml files... why ? why there is unwanted xml
                # files inside the data directory ?
                os.system("rm -rf *.xml")
                print "Removed the xml files from ", root
            elif os.path.isfile('./' + outfile):
                print "xml file exists. so skipping the directory", root
                continue
            # end of if os.path.isfile('./' + outfile) and __OVERWRITE:

            # do the cdscan
            cmd = "%s -x %s  *.%s" % (cdscan, outfile, extension)
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
                                    stderr=PIPE, close_fds=True)
            stdout, stderr = p.communicate()
            logfile = fname + '.log'
            if stderr:
                logfpath = os.path.join(logpath, 'error', logfile)
                f = open(logfpath, 'w')
                f.write('cdscan error ...\n')
                f.write("datapath, " + root)
                f.write("INFO ... " + stdout)
                f.write("ERROR ... " + stderr)
                f.close()
                failurefile.write("%s, %s \n" % (outfile, root))
                print "error ", stderr
                continue
            # end of if stderr:

            if re.findall(r'[Ww]arnings?', stdout):
                logfpath = os.path.join(logpath, 'warning', logfile)
                f = open(logfpath, 'w')
                f.write('cdscan warning ...\n')
                f.write("datapath, " + root)
                f.write("WARNING ... " + stdout)
                f.close()
                warningfile.write("%s, %s \n" % (outfile, root))
                print "warning ", stdout
                continue

            elif stdout:
                logfpath = os.path.join(logpath, 'info', logfile)
                f = open(logfpath, 'w')
                f.write('cdscan error ...\n')
                f.write("datapath, " + root)
                f.write("INFO ... " + stdout)
                f.close()
                successfile.write("%s, %s \n" % (outfile, root))
                print "info ", stdout
            # end of if re.findall(r'[Ww]arnings?', stdout):
        # end of if files:
    # end of for root, sub, files in os.walk(os.path.abspath(datapath)):
    successfile.close()
    warningfile.close()
    failurefile.close()
    print "Created xml files by cdscan in the path ", datapath
    print "Done!"
# end of def doCdscan(datapath, extension='nc', logpath=None, **kwarg):

cdscan = raw_input("Enter your cdat/uvcdat bin path : ").strip()
print cdscan
cdscan = os.path.join(cdscan, 'cdscan')
print "Your cdscan cmd path is ", cdscan

datapath = raw_input("Enter the source data path : ")
print "The source data path is '%s'" % datapath

outpath = raw_input("Enter the log path : ")
d = datetime.date.today()
logdir = d.isoformat()
outpath = os.path.abspath('%s/cdlogs/%s' % (outpath,logdir))

if not os.path.isdir(outpath):
    os.makedirs(outpath)
# end of if not os.path.isdir(outpath):

print "The cdscan log path is '%s'" % outpath

modifiedTodayInput = raw_input("Do you want to do cdscan only for \
                  the directories which is modified today [N/y] : ").strip()

if modifiedTodayInput in ['y', 'Y', 'yes']:
    modifiedTodayInput = True
    __OVERWRITE = True
else:
    modifiedTodayInput = False
# end of if modifiedTodayInput in ['y', 'Y', 'yes']:

missingXmlInput = raw_input("Do you want to do cdscan only for \
                  the directories which is not having xml [N/y] : ").strip()

if missingXmlInput in ['y', 'Y', 'yes']:
    __OVERWRITE = False
# end of if missingXmlInput in ['y', 'Y', 'yes']:

if not __OVERWRITE:
    overwriteInput = raw_input("Do you want to enable overwrite option as True [N/y] : ").strip()
    if overwriteInput in ['y', 'Y', 'yes']:
        __OVERWRITE = True
# end of if __OVERWRITE == False:      

doCdscan(datapath, extension='nc', logpath=outpath, fsplit='_',
  fjoin='_', flen=5, skipdirs=['Annual'], modifiedToday=modifiedTodayInput)


