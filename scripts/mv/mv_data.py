import os, time, sys
import shutil
from projectdatatypes import Realm, Freq


def getInfoFromFileName(fname, project):
    """
    tos_Omon_CanCM4_historical_r10i1p1_196101-200512.nc


    project/model/experiment/fre/realm/variable/ensemble/ncfile

    Written By : Arulalan.T

    Date :

    Updated : 28.02.2013

    """

    if project in ['CMIP5']:
        fname = fname.split('_')
        var = fname[0]
        model = fname[2]
        experiment = fname[3]
        ensemble = fname[4]
        if fname[1].endswith('mon'):
            realm = fname[1].split('mon')[0]
            freq = 'mon'
        elif fname[1].endswith('day'):
            realm = fname[1].split('day')[0]
            freq = 'day'
        else:
            print "unknown frequency! Please add the frequcy to identify it !"
        # end of if fname.endswith('mon'):

        # temporary solution to get realm & freq
#        if fname[1] in ['Amon', 'Omon', 'LImon', 'OImon', 'Lmon', 'SImon']:
#            realm, freq = fr[0], 'mon'
#        elif fname[1] in ['Aday', 'Oday', 'LIday', 'OIday', 'Lday', 'SIday']:
#            realm, freq = fr[0], 'day'
#        else:
#            print "Couldnt split realm & freq from file name ", '_'.join(fname)
#            print "So skipping copy/move to the destination"
#            return None
#        print fname
#        print realm, freq
        if realm in Realm:
            realm = Realm[realm]
        else:
            raise ValueError("No realm index key found for %s in Realm Dictionary" % realm)

        if freq in Freq:
            freq = Freq[freq]
        else:
            raise ValueError("No frequency index key found for %s in Freq Dictionary" % freq)

        return [project, model, experiment, freq, realm, var, ensemble]
    else:
        pass
# end of def getInfoFromFileName(fname, project):


def moveFiles2ProperDir(project, inpath, outpath=None, action='move', overwrite=1,
                                                    extension=['.nc'], skip=None):

    if not os.path.isabs(inpath):
        inpath = os.path.abspath(inpath)

#    flag = 1
#    while flag:
#        if not os.path.isabs(inpath):
#            inpath = os.path.abspath(inpath)
#            useragree = raw_input("Inpath is %s. Do you procees [yes/no] ?")
#            if useragree in ['y', 'Y', 'yes']:
#                flag = 0
#            if useragree in ['n', 'N', 'no']:
#                inpath = raw_input('Then enter the Inpath : ')
#        else:
#            break

    fobj = open('mvstatus.csv', 'w')

    mv2samepath = False
    tmpdir = ''

    if outpath in [None, '']:

        if action == 'move':
            useragree = raw_input("Outpath is None. So Shall we  move the files in the same \
               input path '%s' itself to organize the directory structure [yes/no] ?" % inpath)
        elif action == 'copy':
            useragree = raw_input("Outpath is None. So you can not copy the files in to the same \
               input path itself to organize the directory structure. Would you like to move files \
               into the same inpath [yes/no] ?")
        # end of if action == 'move':

        if useragree in ['', 'y', 'Y', 'yes']:
            action = 'move'
        elif useragree in ['n', 'N', 'no']:
            action = 'copy'
            outpath = raw_input('Then enter the outpath to copy the files : ')
        # end of if useragree in ['y', 'Y', 'yes']:

        if action == 'move':
            tmpdir = project + '_tmp'

            tmpdirpath = os.path.abspath(os.path.join(inpath, '../' + tmpdir))
            if not os.path.isdir(tmpdirpath):
                os.mkdir(tmpdirpath)
                print "Created %s temporary folder in previous to inpath %s " % (tmpdir, tmpdirpath)
            else:
                print "Already exists %s temporary folder in previous to inpath %s " % (tmpdir, tmpdirpath)
            # end of if not os.path.isdir(tmpdir):
            os.system("mv " + inpath + " " + tmpdirpath)
            print "Moved the files from inpath %s to temporary path %s " % (inpath, tmpdirpath)

            mv2samepath = True
            # outpath is same as organal inpath
            outpath = inpath
            print "The outpath is ", outpath
            # assign the temporary path to inpath
            inpath = tmpdirpath
         # end of if action == 'move':
    # end of if outpath in [None, '']:

    for root, sub, files in os.walk(os.path.abspath(inpath)):
        if files:
            # Collect the list of extension binary files. eg : *.nc file
            bfiles = [f for f in files for ext in extension if f.endswith(ext)]
            for bfile in bfiles:
                if not skip in ['', None]:
                    if bfile.endswith(skip):
                        print "Skipping the source file '%s', since it is endswith '%s' " % (bfile, skip)
                        fobj.write("Skipping the source file," + bfile + ", since it is endswith," + skip)
                        continue
                    # end of if bfile.endswith(skip):
                # end of if not skip in ['', None]:
                # get the directory structure list
                dirstr = getInfoFromFileName(bfile, project)
                if not dirstr:
                    fobj.write("Couldnt split realm & freq from file name "
                      + bfile + "So skipping copy/move to the destination\n")
                    continue
                # end of if not dirstr:
                # make it as abspath
                destpath = os.path.join(outpath, *dirstr)

                if not os.path.isdir(destpath):
                    # create the directory structure if it not exists
                    os.makedirs(destpath)
                    print "Created the directory structure ", destpath
                # end of if not os.path.isdir(destpath):

                # get the extension file abspath
                srcpath = os.path.join(root, bfile)

                if not overwrite:
                    # checking either this same file is exists in the destpath
                    if os.path.isfile(os.path.join(destpath, bfile)):
                        print "Already file exists in ", destpath, '/', bfile
                        fobj.write(bfile + ', file is already exists in ,' +
                                        destpath + ', So skipping it' + '\n')
                        print
                        continue
                    # end of if os.path.isfile(os.path.join(destpath, bfile)):
                # end of if not overwrite:

                # copying/moving the extension binary file from source path to
                # destination path.
                try:
                    if action == 'copy':
                        shutil.copy2(srcpath, destpath)
                        print srcpath, ' is copied to ', destpath
                        fobj.write(srcpath + ', is copied to ,' + destpath + '\n')
                    elif action == 'move':
                        shutil.move(srcpath, destpath)
                        print srcpath, ' is moved to ', destpath
                        fobj.write(srcpath + ', is moved to ,' + destpath + '\n')
                except:
                    raise RuntimeError("An error occured while copying file \
                        from %s to %s" % (srcpath, destpath))
                # end of try:
            # end of for bfile in bfiles:
        # end of if files:
    # end of for root, sub, files in os.walk(os.path.abspath(inpath)):
    fobj.close()

    if mv2samepath:
        print "Successfully Organized the files within the same organal inpath", inpath
        fobj = os.popen("find %s -type f" % tmpdirpath)
        if not fobj.readlines():
            os.system("rm -rf " + tmpdirpath)
            print "Removed the empty temporary directory ", tmpdirpath
        else:
            useragree = raw_input("CAUTION : The temporary directory '%s' contains some files. \
                         Do you want to remove it including rest of the files [no/yes] ?" % tmpdir)
            if useragree in ['y', 'Y', 'yes']:
                os.system("rm -rf " + tmpdirpath)
                print "Removed the temporary directory ", tmpdirpath
            else:
                print "Not removed the temporary directory '%s' from path '%s'" % (tmpdir, tmpdirpath)
                print "Check this folder is there anything useful files which you may need ! "
        # end of if not fobj.readlines():
    # end of if mv2samepath:

    print "\n\nDone ... !"
# end of def def moveFiles2ProperDir(...):


if __name__ == '__main__':

    project = raw_input("Enter the Project name [CMIP5] : ")
    if project in ['', 'CMIP5']:
        project = 'CMIP5'
    srcpath = raw_input("Enter the source path : ")

    #destpath = raw_input("Enter the destination path : ")
    # Since this script is in server, it should know the destination path !
    destpath = os.path.abspath('../../CMIPs/')
    print "The destination path is '%s'" % destpath

    action = raw_input("Enter the action [copy/move] : ")
    if action in ['copy', 'COPY', '']:
        action = 'copy'
    elif action in ['move', 'MOVE']:
        action = 'move'

    overwrite = raw_input("Overwrite option [no/yes] : ")
    if overwrite in [0, '', 'no', 'NO', False]:
        overwrite = 0
    elif overwrite in [1, 'yes', 'YES', True]:
        overwrite = 1

    skip = raw_input("Enter the skip file extension : ")
    are_u_sure = raw_input("Are you sure about the above given details.\n  \
                           Shall we proceed to copy/move the data ? [yes/no] : ")
    if are_u_sure in [0, '', 'no', 'NO']:
        print "Going to exit the program without moving the data\nBye"
        sys.exit()
    # end of if are_u_sure in [0, '', 'no', 'NO']:

    f = open('done.log', 'w')
    f.write("move started at %s \n\n" % str(time.ctime()))
    f.close()
    moveFiles2ProperDir(project, srcpath, destpath, action, overwrite, skip=skip)
    f = open('done.log', 'a')
    f.write("move finished at %s \n\n" % str(time.ctime()))
    f.close()

