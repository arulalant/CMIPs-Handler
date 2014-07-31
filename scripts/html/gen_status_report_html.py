import os
import re
import time
from html import HTML
from projectdatatypes import *
from readHtml import getDateFromHtml
from timeutils import TimeUtility


timobj = TimeUtility()


def getDictOfProjDataStruct(project, datapath, skipdirs=['Annual'],
                 collectxml=0, has_missing_taxis=0, get_missing_taxis=0):
    """
    path - source directory path

    collectxml - option 1 gives the xml file name which available inside
                 the least directory
    has_missing_taxis - option 1 enable to just return True or False if the
                 xml time axis has missing time slice in between the
                 time axis series. Must enabled the collectxml option.

    get_missing_taxis - option 1 enable to return not only boolean for
                 has_missing_taxis, also return the missing time slice as
                 component time string. Must enabled the has_missing_taxis
                 option & collectxml options.

    return - table dictionary and available vardic as dictionary

    Date : 28.08.2012
    
    Updated Date : 11.12.2012

    """

    if not project in ['CMIP5']:
        # if some other project data directory structure is same as 'CMIP5'
        # means, then we can include that project name in the above if check
        # list.
        raise ValueError("'Method Not Implimented Yet' for other than 'CMIP5' Project Dataset!")
    # end of if not project in ['CMIP5']:

    # vardic = {ensemble: {realm: set(varnames)}}
    vardic = {}

    # tdic = {experiment: {frequency: {model: {ensemble: {realm: {varname: 'least-dir-size'}}}}}}
    tdic = {}

    datappath = os.path.join(datapath, project)
    # list out the all available model names from the 1st level directory
    # structure
    Model_list = os.listdir(datappath)
    errf = open('error_files.txt', 'w')
    for root, sub, files in os.walk(datappath):

        # removing the skip directories without visting
        for skipdir in skipdirs:
            if skipdir in sub:
                sub.remove(skipdir)
            # end if skipdir in sub:
        # end of for skipdir in skipdirs:

        # get the current looping directory name
        dirname = root.split('/')[-1]

        if dirname in Model_list:
            # get the model name
            model = dirname

        elif dirname in Exp_list:
            # get the experiment name
            experiment = dirname
            if not experiment in tdic:
                # assign the experiment as 1st-level dictionary-key in tdic.
                tdic[experiment] = {}
                # assign the experiment as 1st-level dictionary-key in vardic.
                vardic[experiment] = {}
            # end of if not experiment in tdic:
            expdic = tdic[experiment]

        elif dirname in Freq.values():
            # get the frequency name
            frequency = dirname
            if not frequency in expdic:
                # assign the frequency as 2nd-level dictionary-key in tdic.
                expdic[frequency] = {}
            # end of if not frequency in expdic:
            fredic = expdic[frequency]
            if not model in fredic:
                # assign the model as 3rd-level dictionary-key in tdic.
                fredic[model] = {}
            # end of if not model in fredic:
            modeldic = fredic[model]

        elif dirname in Realm.values():
            # get the realm name
            realm = dirname
            if not realm in vardic[experiment]:
                # assign the realm as key, empty set() as value in 2nd-level
                # dictionary in vardic.
                vardic[experiment][realm] = set()
            # end of if not realm in vardic[experiment]:

        elif dirname in Ensemble_list:
            # get the ensemble name
            ensemble = dirname
            if not ensemble in modeldic:
                # assign the ensemble as 4th-level dictionary-key in tdic.
                modeldic[ensemble] = {}
            # end of if not ensemble in modeldic:
            ensdic = modeldic[ensemble]
            if not realm in ensdic:
                # assign the realm as 5th-level dictionary-key in tdic.
                ensdic[realm] = {}
            # end of if not realm in ensdic:
            realmdic = ensdic[realm]
        else:
            # get the variable name
            varname = dirname
        # end of if dirname in Model_list:        
        
        if files and (not sub):
            leastValue = None

            # ensure that reached the least node/sub directory.
            # get the current directory size as human readable.
            fobj = os.popen("du -sh '%s' " % root)
            dirsize = fobj.readlines()[-1].split()[0]
            if dirsize == '0':
                dirsize = '0 B'
            else:
                suffix = re.findall(r'[A-Z]', dirsize)[0]
                dirsize = dirsize.split(suffix)[0] + ' ' + suffix + 'B'
            # end of if dirsize == '0':

            # assign the dirsize to the leastValue var.
            leastValue = dirsize

            if collectxml:
                xmlfile = [f for f in files if f.endswith('.xml')]
                if xmlfile:
                    # found xml file
                    xmlfile = xmlfile[0]
                    xmlTimeAxis = None
                    if has_missing_taxis:
                        # get the time axis of the varname from the xml file
                        try:
                            f = cdms2.open(os.path.join(root, xmlfile))
                        except Exception, e:
                            err = "\nProblem in accessing file " + xmlfile + '\n' 
                            err += str(e) +'\nSo skiping this file in html report'
                            print err
                            errf.write(err)
                            continue
                        # end of try:
                        if varname not in f.listvariable():
                            raise ValueError("varName '%s' not available.It could be Ensemble. \
                             Kindly add this into the projectdatatypes.py" % varname)
                        xmlTimeAxis = f[varname].getTime()
                        f.close()
                    # end of if has_missing_taxis:
                    if has_missing_taxis and get_missing_taxis:
                        # get the missing time slice value as component time
                        # string.
                        if len(xmlTimeAxis) == 1:
                            print root, xmlfile
                        get_miss = timobj.has_missing(xmlTimeAxis,
                                         deepsearch=1, missingYears=1)
                        # assign the current directory size & (xmlfile name &
                        # missing time slice of xml time axis)
                        leastValue = (dirsize, (xmlfile, get_miss))
                    elif has_missing_taxis:
                        # get the boolean value of either time axis has
                        # missing time slice or not
                        has_miss = timobj.has_missing(xmlTimeAxis,
                                                       deepsearch=0)
                        # assign the current directory size & (xmlfile name &
                        # boolean flag value either xml time series has
                        # missing time slice or not.
                        leastValue = (dirsize, (xmlfile, has_miss))
                    else:
                        # assign the current directory size & xmlfile name
                        leastValue = (dirsize, xmlfile)
                    # end of if has_missing_taxis and get_missing_taxis:
                else:
                    # xmlfile is not found. so make it as None
                    # assign the current directory size & None (because
                    # No xml file found in the current directory)
                    leastValue = (dirsize, None)
            # end of if collectxml:
            # assign the variable name as key & dirsize as value
            # in 6th-level dictionary in tdic.
            if not varname in realmdic:
                realmdic[varname] = leastValue
            # end of if not varname in realmdic:
            # add the variable name to the set() of realm key in
            # vardic[experiment].
            vardic[experiment][realm].add(varname)
        # end of if files and (not sub):        
    # end of for root, sub, files in os.walk(datapath):
    errf.close()
    return tdic, vardic
# end of getDictOfProjDataStruct(project, ...):


def genHtmlHeader(project='', csspath="css/data.css", js='js/data.js'):
    # created index object from HTML() class which should create open & close tags
    html = HTML('html')
    head = html.head()
    title = head.title('Data Status')
    css = head.link(rel="stylesheet", type="text/css", href=csspath)
    if js:
        js = head.script(type="text/javascript", src=js)
        js.text("")
    # end of if js:

    # created body tag
    body = html.body()
    b = body.div(name='body', klass='bodyCls')
    #load = body.p(id="loading", style = 'display:inline')
    #load.text("Loading . . .")
    b.br
    heading = b.div(name='heading', klass='headingCls')
    if project:
        heading.h1(project + ' Project Data Report Sheet')
    else:
        heading.h1(' Project Index Data Report Sheet')

    form = b.form()
    tdiv = form.div(id="contentdiv")
    return (html, b, tdiv, form)
# end of def genHtmlHeader(project='', csspath="css/data.css", js='js/data.js'):


def genHtmlProjectTable(project, tdic, vardic, latestPath, archiveDir,
                       xmlNotExistsWarning=0, xmlTAxisMissingWaring=0,
                                                showXmlTAxisMissing=0):
    """



    Future Enhancement :-
    --------------------

    project is single string as of now.
    But in future we have to change this as list.

    Already we designed this function to generate the index and sub html pages
    for only one project. But just by adding one top for loop of this function
    as projectList, it should loop through the project directories and make
    the top most index.html table with all the projects.

    For this we need to add the outermost key as project in tableDic/tdic
    in the function getDictOfProjDataStruct(...).

    Its all depends upon the project directory structure how we build it !

    Right now it is designed well only for the project 'CMIP5'.

    """

    if not project in ['CMIP5']:
        # if some other project data directory structure is same as 'CMIP5'
        # means, then we can include that project name in the above if check
        # list.
        raise ValueError("'Method Not Implimented Yet' for other than 'CMIP5' Project Dataset!")
    # end of if not project in ['CMIP5']:

    projPath = os.path.join(latestPath, project)
    if not os.path.isdir(projPath):
        os.makedirs(projPath)
    # end of if not os.path.isdir(projPath):

    # sorting the variable names
    for experiment in vardic:
        for realm in vardic[experiment]:
            varnames = list(vardic[experiment][realm])
            varnames.sort()
            vardic[experiment][realm] = varnames
        # end of for realm in vardic[experiment]:
    # end of for experiment in vardic:

    # sorting the experiments
    experiments = tdic.keys()
    experiments.sort()

    # get the index html page table div for all the project index table
    idx_html, idx_b, idx_tdiv, idx_form = genHtmlHeader()
    idx_t = idx_tdiv.table(border='1', klass='tableCls')
    idx_r = idx_t.tr(klass="idxHeaderCls")
    idx_r.th(" S. No. ")
    idx_r.th(" Project ")
    idx_r.th(" Experiment ")
    idx_r.th(" Frequency ")
    # need to increment through project loop
    idx_sno = 1

    preproject = ''
    # get the current time in seconds
    tsec = time.time()
    # Below string format gives as like '201209041637'
    latestdirctime = time.strftime('%Y%m%d%H%M', time.localtime(tsec))
    # Below string format gives as like '2012-09-04 16:37'
    strctime = time.strftime('%Y-%m-%d %H:%M', time.localtime(tsec))

    for experiment in experiments:
        # create the experiment directory to save each experiment, frequency html
        # page inside that.
        proj_path = os.path.join(projPath, experiment)
        if not os.path.isdir(proj_path):
            os.mkdir(proj_path)
        # end of if not os.path.isdir(proj_path):

        idx_rcls = 'oddCls' if idx_sno % 2 == 0 else 'evenCls'

        idx_r = idx_t.tr(klass=idx_rcls)
        if preproject == project:
            idx_r.td(" ")
            idx_r.td(" ")
        else:
            idx_r.td(str(idx_sno))
            idx_r.td(project)
        # end of if preproject == project:
        idx_r.td(experiment)
        preproject = project

        # get the experiment var dictionary of vardic
        expvardic = vardic[experiment]

        avlrealms = []
        # first 3 column (s.no, model, run)
        totalcol = 3
        # get the remaining var column count
        for realm in expvardic:
            totalcol += len(expvardic[realm])
            avlrealms.append(realm)
        # end of for realm in expvardic:
        avlrealms.sort()

        # sort the frequencies
        frequencies = tdic[experiment].keys()
        frequencies.sort()

        for frequency in frequencies:
            # new html page for each experiment & each frequency
            proj_html, proj_b, proj_tdiv, proj_form = genHtmlHeader(project,
                                       csspath="../../css/data.css", js=None)

            t = proj_tdiv.table(border='1', klass='tableCls')
            r = t.tr
            r.th("Experiment = " + experiment.upper(),
                    colspan=str(totalcol), klass="expCls")

            r = t.tr(klass="secondHeaderRowCls")
            r.th("Frequency = " + frequency, rowspan="2", colspan="3")
            r.th("Variables", colspan=str(totalcol - 3))

            # next row
            r = t.tr(klass="secondHeaderRowCls")
            # write realm names in the table header
            for realm in avlrealms:
                # get the variable count
                varcount = len(expvardic[realm])
                r.th(realm, colspan=str(varcount))
            # end of for realm in avlrealms:

            # next row
            r = t.tr(klass="finalHeaderRowCls")
            r.th("S. No.")
            r.th("Model")
            r.th("Run/ Realization")

            # write variable names in the table header subset of realm header
            for realm in avlrealms:
                avlvars = list(expvardic[realm])
                avlvars.sort()
                expvardic[realm] = avlvars
                for varname in expvardic[realm]:
                    r.th(varname)
                # end of for varname in expvardic[realm]:
            # end of for realm in avlrealms:

            # sort the models
            models = tdic[experiment][frequency].keys()
            models.sort()
            sno = 0
            for model in models:
                sno += 1
                rcls = 'oddCls' if sno % 2 == 0 else 'evenCls'
                # next row. Actual data row begins
                r = t.tr(klass=rcls)
                # write sno
                r.td(str(sno))
                # write model name
                r.td(model)

                ensembles = tdic[experiment][frequency][model]
                avlensembles = ensembles.keys()
                avlensembles.sort()

                for ensemble in avlensembles:
                    r.td(ensemble)
                    for realm in avlrealms:
                        for varname in expvardic[realm]:
                            myCls = ''
                            myTitle = ''
                            xmlfile = True
                            missing = False
                            missingValue = None

                            realmdic = ensembles[ensemble].get(realm)
                            size = realmdic.get(varname, 'to do') if realmdic else 'to do'

                            if isinstance(size, tuple):
                                # split the size and xmlfile from tuple
                                size, xmlfile = size
                                if isinstance(xmlfile, tuple):
                                    xmlfile, missing = xmlfile
                                    if isinstance(missing, tuple):
                                        missing, missingValue = missing
                                    # end of if isinstance(missing, tuple):
                                # end of if isinstance(xmlfile, tuple):
                            # end of if isinstance(size, tuple):

                            if xmlNotExistsWarning:
                                if xmlTAxisMissingWaring:
                                    myCls = 'xmlTAxisMissingWaringCls' if missing else ''
                                    myTitle = 'Xmlfile taxis has missing time slice'
                                else:
                                    myCls = 'xmlNotExistsWarningCls' if not xmlfile else ''
                                    myTitle = 'No Xmlfile found'
                                # end of if xmlTAxisMissingWaring:
                            # end of if xmlNotExistsWarning:

                            if (xmlTAxisMissingWaring and showXmlTAxisMissing
                                                            and missingValue):
                                missingValueStr = 'Missing Time Slice : '
                                missingValue = str(missingValue)
                                missingValue = missingValue.split('[')[1]
                                missingValue = missingValue.split(']')[0]
                                missingValueStr += missingValue
                                myTitle = missingValueStr
                            # end of if (xmlTAxisMissingWaring and
                            #         showXmlTAxisMissing and missingValue):

                            if size == '0 B':
                                myCls = 'zeroByteWarningCls'
                                myTitle = 'Zero Byte Files'
                            # end of if size == '0 B':

                            if myCls:
                                r.td(size, klass=myCls, title=myTitle)
                            else:
                                r.td(size)
                            # end of if myCls and myTitle:
                        # end of for varname in expvardic[realm]:
                    # end of for realm in expvardic:

                    if ensemble != avlensembles[-1]:
                        # empty sno, empty model name (because same model)
                        r = t.tr(klass=rcls)
                        r.td()
                        r.td()
                    # end of if ensemble != avlensembles[-1]:
                # end of for ensemble in avlensembles:
            # end of for model in models:
        # add the frequency to the index page
        # add the footer to the project page
        foot = proj_b.div(id='footDiv')
        foot.text('Table Created On ' + strctime)
        #credits
        credit = foot.p(id='author', name='credits')
        credit.text('Author : ')
        author_link = credit.a(href='http://tuxcoder.wordpress.com', target='_blank', klass='')
        author_link.text('Arulalan.T')
        credit.text(' <arulalant@gmail.com> Source : ')
        source_link = credit.a(href='https://github.com/arulalant/CMIPs-Handler', target='_blank', klass='')
        source_link.text('Repo')
        credit.text(' License : GPL V3')
        # save into html
        proj_page_name = frequency + '.html'
        proj_page_path = os.path.join(proj_path, proj_page_name)
        proj_page = open(proj_page_path, 'w')
        proj_page.write(str(proj_html))
        proj_page.close()

        # add the above project html file as link into the main index html page
        idx_freq = idx_r.td()
        proj_page_link = os.path.join(project, experiment, proj_page_name)
        proj_link = idx_freq.a(href=proj_page_link, target='_blank', klass='')
        proj_link.text(frequency)
        # end of for frequency in frequencies:
    # end of for experiment in experiments:

    foot = idx_form.div(id='footDiv')
    footp = foot.p(id='crdate', name=latestdirctime)
    footp.text('Table Created On ' + strctime)
    # set the name of p tag as archive directory name
    archp = foot.p(id='archdate', name=archiveDir)

    # make the relative archiveIndexPath to archiveDir's index.html
    archiveIndexPath = os.path.join('..', archiveDir, 'index.html')
    archp.text('To View Previous Archive  ')
    arch_link = archp.a(href=archiveIndexPath, target='_blank', klass='')
    arch_link.text('click here')
    
    #credits
    credit = foot.p(id='author', name='credits')
    credit.text('Author : ')
    author_link = credit.a(href='http://tuxcoder.wordpress.com', target='_blank', klass='')
    author_link.text('Arulalan.T')
    credit.text(' <arulalant@gmail.com> Source : ')
    source_link = credit.a(href='https://github.com/arulalant/CMIPs-Handler', target='_blank', klass='')
    source_link.text('Repo')
    credit.text(' License : GPL V3')
    # save into index.html
    outfilepath = os.path.join(latestPath, 'index.html')
    index = open(outfilepath, 'w')
    index.write(str(idx_html))
    index.close()
# end of def genHtmlProjectTable(project, ...):


def main(datapath, outpath, project='CMIP5', cdscanWarning=0,
              xmlTAxisMissingWaring=0, showXmlTAxisMissing=0):

    outpath = os.path.join(outpath, 'CMIPs_Data_Status_Report')
    latestPath = os.path.join(outpath, 'latest')

    # get the both available dataset structure & available vardic as dictionary
    tableDic, varDic = getDictOfProjDataStruct(project, datapath,
                                        collectxml=cdscanWarning,
                          has_missing_taxis=xmlTAxisMissingWaring,
                            get_missing_taxis=showXmlTAxisMissing)

    # cleanup the previous latest folder
    htmlcrdate = ''
    if os.path.isdir(latestPath):
        idxhtmlfile = os.path.join(latestPath, 'index.html')
        if os.path.isfile(idxhtmlfile):
            # get the html created date(crdate) from the index.html file
            htmlcrdate = getDateFromHtml(idxhtmlfile)
            htmlcrdatedir = os.path.join(outpath, htmlcrdate)
            os.system("mv %s %s" % (latestPath, htmlcrdatedir))
            print "Renamed the previous 'latest' directory as %s (previous html created date)" % htmlcrdate
        else:
            print "No 'index.html' file found in the latest directory", latestPath
        # end of if os.path.isfile(idxhtmlfile):
    # end of if os.path.isdir(latestPath):

    # generate the index & sub html pages and write it into proper directory
    genHtmlProjectTable(project, tableDic, varDic, latestPath, htmlcrdate,
                                     cdscanWarning, xmlTAxisMissingWaring,
                                                      showXmlTAxisMissing)

    for folder in os.listdir(outpath):
        if folder in ['latest', htmlcrdate]:
            # just dont touch the latest & previous archieve folders
            continue
        else:
            oldarchieve = os.path.join(outpath, folder)
            os.system("rm -rf %s" % oldarchieve)
            print "Removed the old archieve directory", oldarchieve
        # end of if folder in ['latest', htmlcrdate]:
    # end of for folder in os.listdir(outpath):

    if os.path.isdir('./css'):
        print "css folder is copied to the ", latestPath
        os.system("cp -r ./css '%s' " % latestPath)
    # end of if os.path.isdir('./css'):

    if os.path.isdir('./js'):
        print "js folder is copied to the ", latestPath
        os.system("cp -r ./js '%s' " % latestPath)
    # end of if os.path.isdir('./js'):

    print "Written the 'index.html' into the path ", latestPath
    print "Kindly check 'error_files.txt' file also in script/html path"  
# end of def main(datapath, outpath, project='CMIP5', ...):


if __name__ == '__main__':

    project = raw_input("Enter the project name [CMIP5] : ")
    #datapath = raw_input("Enter the source project path : ")
    # Since this script is in server, it should know the source path !
    datapath = os.path.abspath('../../CMIPs/') 
    print "The obtained data path is '%s'" % datapath
    
    #outpath = raw_input("Enter the outpath : ")
    outpath = os.path.abspath('../../')
    print "The index.html path will be ", outpath
    
    cdwarn = raw_input("Do you want to enable cdscan warning [Y/n] : ")
    missing = raw_input("Do you want to enable xml time axis missing time slice warning [Y/n] : ")

    if project in ['CMIP5', '']:
        project = 'CMIP5'
    # end of if project in ['CMIP5', '']:

    if outpath in ['', None]:
        outpath = os.path.abspath(os.curdir)
    # end of if outpath in ['', None]:

    if cdwarn in ['', 'y', 'Y', 'yes']:
        # default enter takes 'yes'
        cdwarn = True
    else:
        cdwarn = False
    # end of if cdwarn in ['', 'y', 'Y', 'yes']:

    if missing in ['', 'y', 'Y', 'yes']:
        # default enter takes 'Yes'
        try:
            import cdms2
        except Exception, e:
            raise ValueError("Try to run the program via CDAT Python. %s" % str(e))
        # end of try:

        missing = True
        get_missing = raw_input("Do you want to show missing time slice [Y/n] : ")
        if get_missing in ['', 'y', 'Y', 'yes']:
            # default enter takes 'Yes'
            get_missing = True
        else:            
            get_missing = False
        # end of if get_missing in ['y', 'Y', 'yes']:
    else:        
        missing = False
        get_missing = False
    # end of if missing in ['y', 'Y', 'yes']:

    # call the main function
    main(datapath, outpath, project, cdscanWarning=cdwarn,
         xmlTAxisMissingWaring=missing, showXmlTAxisMissing=get_missing)

# end of if __name__ == '__main__':

