import os, time, sys
import shutil
from projectdatatypes_auto import *


def getNeededOptions(name, listvar):
    print "\nAvailable %s : " % name
    for idx, val in enumerate(listvar):
        print idx+1, ' : ', val
    print 'all : select above all %s' % name    
    need_var = raw_input('Enter needed %s nos by comma sperated : ' % name)
    need_var = need_var.strip()
    if need_var in ['', 'None']:
        raise ValueError("You must type any one of above choices ! ")            
    elif need_var == 'all':
        print "Selected all above %s" % name
        return listvar
    elif ',' in need_var:
        need_var_idx = need_var.split(',')
        need_var = [listvar[int(idx)-1] for idx in need_var_idx]
        print "Selected the following %s" % name
        print need_var 
        return need_var 
    else:
        need_var_idx = int(need_var) - 1
        need_var = [listvar[need_var_idx]]
        print "Selected the '%s' %s only" % (need_var, name)
        return need_var
    # end of if need_var in ['', 'None']:
# end of def getNeededOptions(name, listvar):

    
def copyFilesFromProperDir(project, inpath, outpath, overwrite=1,
                                            extension=['.nc'], skip=None):

    if not os.path.isabs(inpath):
        inpath = os.path.abspath(inpath)
    
    cpstatus = os.path.join(outpath, 'cpstatus.csv')    
    print "Copy status will be going to store ", cpstatus
    
    if outpath in [None, '']:            
        raise ValueError("Outpath is None. So you can not copy the files in to the same \
               input path itself to organize the directory structure. So going to quit")
    # end of if outpath in [None, '']:
    
    outpath = os.path.join(outpath, 'CMIPs', project) 
    
    usr_models = getNeededOptions('models', list(all_models))
    usr_experiments = getNeededOptions('experiments', list(all_experiments))
    usr_frequencies = getNeededOptions('frequencies', list(all_frequencies)) 
    usr_vars = getNeededOptions('vars', list(all_vars))
    are_u_sure = raw_input("Are you sure about the above given details.\n  \
                           Shall we proceed to copy/move the data ? [yes/no] : ")
    if are_u_sure in [0, '', 'no', 'NO']:
        print "Going to exit the program without moving the data\nBye"
        sys.exit()
    # end of if are_u_sure in [0, '', 'no', 'NO']:

    for root, sub, files in os.walk(os.path.abspath(inpath)):   
        
        if not sub: continue   
       
        sub_sample = sub[0]
        # to copy the sub directories into another array, 
        # we must to use either sub[:], or list(sub) or copy.copy(sub) 
        subdirs = list(sub) # copy is very important 
        
        if sub_sample in all_models:
            # models directories
            del sub[:] # removed entire sub and 
            sub.extend(usr_models) # then added usr model list to sub 
        elif sub_sample in all_experiments:
            # experiments directories
            for sd in subdirs:
                if sd not in usr_experiments:
                    # removed unwanted experiment
                    sub.remove(sd)
        elif sub_sample in all_frequencies:
            # frequencies directories
            for sd in subdirs:
                if sd not in usr_frequencies:
                    # removed unwanted frequencies
                    sub.remove(sd)
        elif sub_sample in all_vars:
            # variables directories
            for sd in subdirs:
                if sd not in usr_vars:
                    # removed unwanted variables
                    sub.remove(sd)
            # end of for sd in subdirs:
            
            if len(sub) > 0:
                if sub[0] in usr_vars:
                    # copy the whole directories into destination
                    rpath = root.split(project)[1][1:]                           
                    for vardir in sub:
                        varpath = os.path.join(root, vardir)
                        print "copying going on ...,", varpath
                        fobj = open(cpstatus, 'a')
                        for run in os.listdir(varpath):
                            despath = os.path.join(outpath, rpath, run)
                            os.system('mkdir -p %s' % despath)
                            msg =  "destination path created, '%s'\n" % despath
                            fobj.write(msg)
                            print msg
                            runpath = os.path.join(varpath, run)
                            for lfile in os.listdir(runpath):
                                lfilepath = os.path.join(runpath, lfile)
                                shutil.copy2(lfilepath, despath)
                                msg = '%s, is copied to, %s\n' % (lfilepath, despath)
                                fobj.write(msg + '\n')
                                print msg
                            # end of for lfile in runpath:                            
                        # end of for run in os.listdir(varpath):
                        fobj.close()
                    # end of for vardir in usr_vars:
                # end of if sub[0] in usr_vars:
            # end of if len(sub) > 0:
        else:
            continue
            # end of if subdir in all_models:
        # end of for subdir in sub:
    # end of for root, sub, files in os.walk(os.path.abspath(inpath)):      
    print "\n\nDone ... !"
# end of def def moveFiles2ProperDir(...):


if __name__ == '__main__':

    srcpath = raw_input("Enter the source path : ")
        
    destpath = raw_input("Enter the destination path : ")
    
    if destpath in ['', '/']:
        raise ValueError("destination path can not be empty or /")
        
    if srcpath == destpath:
        raise ValueError("Both data sourcepath & destination path can not be same.")
    # end of if srcpath == destpath:
    
    print "The destination path is '%s'" % destpath
    
    project = raw_input("Enter the Project name [CMIP5] : ")
    if project in ['', 'CMIP5']:
        project = 'CMIP5'
  
    overwrite = raw_input("Overwrite option [no/yes] : ")
    if overwrite in [0, '', 'no', 'NO', False]:
        overwrite = 0
    elif overwrite in [1, 'yes', 'YES', True]:
        overwrite = 1

    skip = raw_input("Enter the skip file extension : ")
    
    done = os.path.join(destpath, 'cp_done.log')
    print "done status will be going to store ", done
    f = open(done, 'w')
    f.write("copy started at %s \n\n" % str(time.ctime()))
    f.close()
    copyFilesFromProperDir(project, srcpath, destpath, overwrite, skip=skip)
    f = open(done, 'a')
    f.write("copy finished at %s \n\n" % str(time.ctime()))
    f.close()

