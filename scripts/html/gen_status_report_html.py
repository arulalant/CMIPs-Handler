# -*- coding: utf-8 -*-
import os
import re
import time
from html import HTML
from projectdatatypes import *
from projectdatatypes_auto import all_experiments, all_ensembles
from readHtml import getDateFromHtml
from timeutils import TimeUtility


timobj = TimeUtility()

dirsize_chars = ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']

def __convert2BigSize(previous_dirsize, dirsize_no):
    '''
    previous_dirsize : must be string with human readable suffix
    dirsize_no : must be in KBs float type
    return : previous_dirsize + dirsize_no as string with human 
             readable suffix
    '''
    
    suffix = re.findall(r'[A-Z]', previous_dirsize)[0]
    previous_dirsize_no = float(previous_dirsize.split(suffix)[0])        
    suffix = suffix[0]        
    # convert previous_dirsize_no into KBs
    if suffix in dirsize_chars:
        power = dirsize_chars.index(suffix)
        if power: # i.e > 0
            # convert bigsize into KBs
            previous_dirsize_no *= (1024 ** power)
    # end of if suffix in dirsie_chars:
    
    # add previous_dirsize_no and dirsize_no (both are in KBs)        
    current_size_no = previous_dirsize_no + dirsize_no
    
    # convert current_size_no into string with human readable suffix
    power = 0
    while (current_size_no > 1024):
        current_size_no /= 1024.
        power += 1
        if power == 7: break # i.e. going beyond dirsize_chars length
    # end of while (current_size_no > 1024):
    suffix = dirsize_chars[power]
    current_size = str(current_size_no) + ' ' + suffix + 'B'
    # return current_size
    return current_size
# end of def __convert2BigSize(previous_dirsize, dirsize_no):


def __getSizeInKBs(dirsize):
    '''
    Input : dirsize in string with human readable suffix 
    
    returns : tuple contains dirsize_no in float KBs and 
              dirsize in string with human readable suffix 
    
    '''
    
    suffix = re.findall(r'[A-Z]', dirsize)[0]
    dirsize_no = dirsize.split(suffix)[0]
    # current dirsize in string with human readable suffix
    dirsize = dirsize_no + ' ' + suffix + 'B'
    # convert current dirsize into KBs float 
    dirsize_no = float(dirsize_no)
    if suffix in dirsize_chars:
        power = dirsize_chars.index(suffix)
        if power: # i.e > 0
            # convert big size into KBs
            dirsize_no *= (1024 ** power)
    # end of if suffix in dirsie_chars:
    return (dirsize_no, dirsize)
# end of def __getSizeInKBs(dirsize):
                
                
def getDictOfProjDataStruct(project, datapath, skipdirs=['Annual'],
                           get_taxis=0, get_grid=0, collectxml=0, 
                          has_missing_taxis=0, get_missing_taxis=0):
    """
    path - source directory path
    
    get_taxis - option 1 enable to return time axis begin and end of each
                and every variables
    get_grid - option 1 enable to return grid type and resolution
    
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
    
    # esize = {experiment: {frequency: {model: {ensemble: 'full-size-of-all-variables-of-all-realms'}}}}
    esize = {}
    # vsize = {experiment: {frequency: {varname: 'full-size-of-all-realms-of-all-models'}}}
    vsize = {}
    
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

        elif dirname in Exp_list + list(all_experiments):
            # get the experiment name
            experiment = dirname
            if not experiment in tdic:
                # assign the experiment as 1st-level dictionary-key in tdic.
                tdic[experiment] = {}
                # assign the experiment as 1st-level dictionary-key in vardic.
                vardic[experiment] = {}
                # assign the experiment as 1st-level dictionary-key in esize.
                esize[experiment] = {}
                # assign the experiment as 1st-level dictionary-key in vsize.
                vsize[experiment] = {}
            # end of if not experiment in tdic:
            expdic = tdic[experiment]
            exp_es_dic = esize[experiment]
            exp_vs_dic = vsize[experiment]

        elif dirname in Freq.values():
            # get the frequency name
            frequency = dirname
            if not frequency in expdic:
                # assign the frequency as 2nd-level dictionary-key in tdic.
                expdic[frequency] = {}
                # assign the frequency as 2nd-level dictionary-key in esize.
                exp_es_dic[frequency] = {}
                # assign the frequency as 2nd-level dictionary-key in vsize.
                exp_vs_dic[frequency] = {}
            # end of if not frequency in expdic:
            fredic = expdic[frequency]
            fre_es_dic = exp_es_dic[frequency]
            fre_vs_dic = exp_vs_dic[frequency]
            if not model in fredic:
                # assign the model as 3rd-level dictionary-key in tdic.
                fredic[model] = {}
                # assign the model as 3rd-level dictionary-key in esize.
                fre_es_dic[model] = {}
            # end of if not model in fredic:
            modeldic = fredic[model]
            # store all the full-size-of-all-variables-of-all-realms here
            model_es_dic = fre_es_dic[model]

        elif dirname in Realm.values():
            # get the realm name
            realm = dirname
            if not realm in vardic[experiment]:
                # assign the realm as key, empty set() as value in 2nd-level
                # dictionary in vardic.
                vardic[experiment][realm] = set()
            # end of if not realm in vardic[experiment]:

        elif dirname in Ensemble_list + list(all_ensembles):
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
                dirsize_no = 0
            else:
                dirsize_no, dirsize = __getSizeInKBs(dirsize)               
            # end of if dirsize == '0':

            # assign the dirsize to the leastValue var.
            leastValue = dirsize
            
            if ensemble not in model_es_dic:
                # assign dirsize in string with human readable suffix
                model_es_dic[ensemble] = dirsize                
            else:
                previous_dirsize = model_es_dic[ensemble]
                # add previous and current dirsize & convert it into string
                # with human readable suffix
                current_size = __convert2BigSize(previous_dirsize, dirsize_no)
                # store updated full ensemble size 
                model_es_dic[ensemble] = current_size
            # end of if ensemble not in model_es_dic:
             
            if varname not in fre_vs_dic:
                # assign dirsize in string with human readable suffix
                fre_vs_dic[varname] = dirsize
            else:   
                previous_dirsize = fre_vs_dic[varname]
                # add previous and current dirsize & convert it into string
                # with human readable suffix
                current_size = __convert2BigSize(previous_dirsize, dirsize_no)
                # store updated all variable size 
                fre_vs_dic[varname] = current_size
            # end of if varname not in fre_vs_dic:
            
            if collectxml:
                xmlfile = [f for f in files if f.endswith('.xml')]
                if xmlfile:
                    # found xml file
                    xmlfile = xmlfile[0]
                    xmlTimeAxis = None
                    if get_taxis or get_grid or has_missing_taxis:
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
                        grid = f[varname].getGrid()
                        f.close()
                    # end of if has_missing_taxis:
                    extrainfo = {} 
                    extrainfo['xmlfile'] =  xmlfile
                    if get_taxis:
                        # get start and end time 
                        ct = xmlTimeAxis.asComponentTime()              
                        sd = str(ct[0]).split(' ')[0]
                        ed = str(ct[-1]).split(' ')[0]
                        extrainfo['taxis'] = '(%s to %s)' % (sd, ed)
                    # end of if get_taxis:
                    
                    if get_grid:
                        gstr = grid.__str__()
                        if '\n' in gstr:
                            # Got generic grid. 
                            gtype = gstr.split('\n')[1].split(': ')[1].capitalize()
                            # So get lat, lon resolution also.
                            lat = grid.getLatitude()
                            lon = grid.getLongitude()
                            latshp = str(abs(lat[0] - lat[1]))[:4]
                            lonshp = str(abs(lon[0] - lon[1]))[:4]
                            gtype += ', (%s°x%s°)' % (latshp, lonshp)
                        elif '<' in gstr:
                            # Got curvilinear grid 
                            gtype = gstr.split(',')[0].split('<')[1]
                        else:
                            gtype = ''
                        extrainfo['grid'] = gtype
                    # end of if get_grid:
                        
                    if has_missing_taxis and get_missing_taxis:
                        # get the missing time slice value as component time
                        # string.
                        if len(xmlTimeAxis) == 1:
                            print root, xmlfile
                        get_miss = timobj.has_missing(xmlTimeAxis,
                              deepsearch=1, missingYears=1, missingMonths=1)
                        # assign the current directory size & (xmlfile name &
                        # missing time slice of xml time axis)
                        extrainfo['missingValue'] = get_miss
                    elif has_missing_taxis:
                        # get the boolean value of either time axis has
                        # missing time slice or not
                        has_miss = timobj.has_missing(xmlTimeAxis,
                                                       deepsearch=0)
                        # assign the current directory size & (xmlfile name &
                        # boolean flag value either xml time series has
                        # missing time slice or not.
                        extrainfo['has_missing'] = has_miss
                    else:
                        pass
                    # end of if has_missing_taxis and get_missing_taxis:
                    leastValue = (dirsize, extrainfo)
                else:
                    # xmlfile is not found. so make it as None
                    # assign the current directory size & {} (because
                    # No xml file found in the current directory)
                    leastValue = (dirsize, {})
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
    return (tdic, vardic, esize, vsize)
# end of getDictOfProjDataStruct(project, ...):


def genHtmlHeader(project='', location='', csspath="css/data.css", js='js/data.js'):
    # created index object from HTML() class which should create open & close tags
    html = HTML('html')
    head = html.head()
    title = head.title('Data Status')
    meta = head.meta(charset="utf-8")  
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
    ifen = ' - ' if location else ''
    if project:
        heading.h1(project + ' Project Data Report Sheet' + ifen + location)
    else:
        heading.h1(' Project Index Data Report Sheet' + ifen + location)

    form = b.form()
    tdiv = form.div(id="contentdiv")
    return (html, b, tdiv, form)
# end of def genHtmlHeader(project='', ...):


def genHtmlProjectTable(project, location, tdic, vardic, ensSizeDic, 
                 varSizeDic, latestPath, archiveDir, showXmlTAxis=0, 
                               showVarGrid=0, xmlNotExistsWarning=0, 
                     xmlTAxisMissingWaring=0, showXmlTAxisMissing=0):
    """



    Future Enhancement :-
    --------------------

    Argument 'project' is single string as of now.
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
    idx_html, idx_b, idx_tdiv, idx_form = genHtmlHeader(location=location)
    idx_t = idx_tdiv.table(border='1', klass='tableCls')
    idx_r = idx_t.tr(klass="idxHeaderCls")
    idx_r.th(" S. No. ")
    idx_r.th(" Project ")
    idx_r.th(" Experiment ")
    idx_r.th(" Frequency ")
    idx_r.th(" Total Size")
    # need to increment through project loop
    idx_sno = 1

    preproject = ''
    # get the current time in seconds
    tsec = time.time()
    # Below string format gives as like '201209041637'
    latestdirctime = time.strftime('%Y%m%d%H%M', time.localtime(tsec))
    # Below string format gives as like '2012-09-04 16:37'
    strctime = time.strftime('%Y-%m-%d %H:%M', time.localtime(tsec))
    # store index page grand total 
    IdxGrandTotal = 0
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
        # first 3 column (s.no, model, run) and last 1 column for total size
        totalcol = 4
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
                            location, csspath="../../css/data.css", js=None)

            t = proj_tdiv.table(border='1', klass='tableCls')
            r = t.tr
            r.th("Experiment = " + experiment.upper(),
                    colspan=str(totalcol), klass="expCls")

            r = t.tr(klass="secondHeaderRowCls")
            r.th("Frequency = " + frequency, rowspan="2", colspan="3")
            r.th("Variables", colspan=str(totalcol - 4))
            r.th("Run Total Size", rowspan="3")
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
                            myCls = 'tooltip'
                            toolTxt = ''
                            taxis = ''
                            grid = ''
                            xmlfile = None
                            missing = False
                            missingValue = None
                                                        
                            realmdic = ensembles[ensemble].get(realm)
                            size = realmdic.get(varname, 'to do') if realmdic else 'to do'
                            
                            if isinstance(size, tuple):
                                # split the size and otherinfo from tuple
                                size, otherinfo = size
                                # get needed info from otherinfo 
                                xmlfile = otherinfo.get('xmlfile', None)
                                taxis = otherinfo.get('taxis', '')
                                grid = otherinfo.get('grid', '')
                                missing = otherinfo.get('has_missing', '')
                                missingValue = otherinfo.get('missingValue', '')
                            # end of if isinstance(size, tuple):                                          
                            
                            toolTxt += varname + ', '
                            
                            if showVarGrid and grid:
                                toolTxt += grid 
                            # end of if showVarGrid and grid:
                            
                            if showXmlTAxis and taxis:
                                if toolTxt: toolTxt += ', '
                                toolTxt += 'Avl Time : ' + taxis
                            # end of if showXmlTAxis and taxis:

                            if xmlTAxisMissingWaring and missingValue:
                                myCls = 'xmlTAxisMissingWaringCls'
                                if toolTxt: toolTxt += ', '
                                if showXmlTAxisMissing:
                                    misStr = 'Missing Time : '
                                    missingValues = ''                               
                                    for msv in missingValue[1]:
                                        if missingValues: missingValues += ', '
                                        if len(msv) == 1:
                                            missingValues += '(%d)' % msv
                                        elif len(msv) == 2:
                                            missingValues += '(%d to %d)' % msv
                                    # end of for msv in missingValue[1]:
                                    toolTxt += misStr + missingValues                                 
                                elif not showXmlTAxisMissing:
                                    toolTxt += 'Xmlfile taxis has missing time slice'       
                            # end of if xmlTAxisMissingWaring and ...:
                            
                            if xmlNotExistsWarning and not xmlfile:
                                myCls = 'xmlNotExistsWarningCls'
                                toolTxt = 'Problem in cdcsan'
                            # end of if xmlNotExistsWarning:                     
                            
                            if size == '0 B':
                                myCls = 'zeroByteWarningCls'
                                toolTxt = 'Zero Byte File'
                            # end of if size == '0 B':
                            
                            if size == 'to do':
                                r.td(size) 
                            elif myCls:
                                r.td(size, klass=myCls+' tooltip', tooltxt=toolTxt)                     
                            else:
                                r.td(size, klass='tooltip', tooltxt=toolTxt)  
                            # end of if myCls:  
                        # end of for varname in expvardic[realm]:
                    # end of for realm in expvardic:
                    totTitle = model + ' ' + ensemble + ' Total Size'
                    # add total size of total ensemble at last of column 
                    # of the table
                    if ensemble in ensSizeDic[experiment][frequency][model]:
                        esize = ensSizeDic[experiment][frequency][model][ensemble]
                        suffix = re.findall(r'[A-Z]', esize)[0]
                        esize_no = float(esize.split(suffix)[0])
                        # current dirsize in string with human readable suffix
                        esize = str(round(esize_no, 2))
                        if esize.endswith('.0'): esize = esize.split('.0')[0]     
                        esize += ' ' + suffix + 'B'                        
                        r.td(esize, klass='ensembleTotal tooltip', tooltxt=totTitle)
                    else:
                        # why ensemble comes in models when really not 
                        # present there ???
                        r.td('0 KB', klass='zeroByteWarningCls tooltip', tooltxt=totTitle)
                    # end of if ensemble in ensSizeDic[...]:
                    
                    # adding empty cell for same model but different ensemble
                    if ensemble != avlensembles[-1]:
                        # empty sno, empty model name (because same model)
                        r = t.tr(klass=rcls)
                        r.td()
                        r.td()
                    # end of if ensemble != avlensembles[-1]:
                    
                # end of for ensemble in avlensembles:
            # end of for model in models:
            r = t.tr(klass='')
            r.td('Variable Total Size', colspan="3", klass='varTotalSize')
            GrandTotal = None
            for realm in avlrealms:
                for varname in expvardic[realm]:
                    if not varname in varSizeDic[experiment][frequency]: continue        
                    vsize = varSizeDic[experiment][frequency][varname]                                        
                    if not GrandTotal: 
                        GrandTotal = vsize
                    else:
                        vsize_no, vsize = __getSizeInKBs(vsize)
                        # add total with previous total 
                        GrandTotal = __convert2BigSize(GrandTotal, vsize_no)
                    # end of if not GrandTotal: 
                    # round off size 
                    suffix = re.findall(r'[A-Z]', vsize)[0]
                    vsize_no = float(vsize.split(suffix)[0])
                    # current dirsize in string with human readable suffix
                    vsize = str(round(vsize_no, 2))
                    if vsize.endswith('.0'): vsize = vsize.split('.0')[0]                    
                    vsize += ' ' + suffix + 'B'
                    # add variable full size over all models
                    myTitle = varname + ' Total Size'
                    r.td(vsize, klass='variableTotal tooltip', tooltxt=myTitle)
                # end of for varname in expvardic[realm]:
            # end of for realm in avlrealms:
            
            # GrandTotal sum all together.
            suffix = re.findall(r'[A-Z]', GrandTotal)[0]
            GrandTotal_no = float(GrandTotal.split(suffix)[0])
            # current dirsize in string with human readable suffix
            GrandTotal = str(round(GrandTotal_no, 2))
            if GrandTotal.endswith('.0'): GrandTotal = GrandTotal.split('.0')[0]
            GrandTotal += ' ' + suffix + 'B'
            gtitle = 'GrandTotal of ' + experiment
            r.td(GrandTotal, klass='GrandTotal tooltip', tooltxt=gtitle)
        # end of for frequency in frequencies:
        
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
        
        # add experiment's GrandTotal into index page at last column
        gTitle = ' '.join([project, experiment, frequency, 'Total Size'])
        idx_r.td(GrandTotal, klass='ensembleTotal tooltip', tooltxt=gTitle)
        # find index grand total 
        if not IdxGrandTotal:
            IdxGrandTotal = GrandTotal
        else:
            # get current grand total no and str 
            IdxGrandTotal_no, IdxGrandTotal_str = __getSizeInKBs(GrandTotal)
            # add total with previous total 
            IdxGrandTotal_str = __convert2BigSize(IdxGrandTotal, IdxGrandTotal_no)                        
            suffix = re.findall(r'[A-Z]', IdxGrandTotal_str)[0]
            IdxGrandTotal_no = float(IdxGrandTotal_str.split(suffix)[0])
            # current grand total in string with human readable suffix
            IdxGrandTotal = str(round(IdxGrandTotal_no, 2)) + ' ' + suffix + 'B'        
        # end of for frequency in frequencies:        
    # end of for experiment in experiments:
    # add grand total row and col at the end of the index page table     
    idx_lr = idx_t.tr(klass=idx_rcls)
    idx_lr.td('Grand Total Size', colspan="4", klass='varTotalSize')
    igtitle = 'GrandTotal of ' + project
    idx_lr.td(IdxGrandTotal, klass='GrandTotal tooltip', tooltxt=igtitle)

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


def main(datapath, outpath, project='CMIP5', location='', showXmlTAxis=0, 
                                          showVarGrid=0, cdscanWarning=0, 
                          xmlTAxisMissingWaring=0, showXmlTAxisMissing=0):

    outpath = os.path.join(outpath, 'CMIPs_Data_Status_Report')
    latestPath = os.path.join(outpath, 'latest')
    print "Collecting info about available models, ensembles, variables, files & more"
    print "Be hold ...!"
    # get the both available dataset structure & available vardic as dictionary
    tableDic, varDic, ensSizeDic, varSizeDic = getDictOfProjDataStruct(project, 
                                        datapath, get_taxis=showXmlTAxis,
                                        get_grid=showVarGrid,
                                        collectxml=cdscanWarning,
                                   has_missing_taxis=xmlTAxisMissingWaring,
                                     get_missing_taxis=showXmlTAxisMissing)
    
    print "Creating html table ..."
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
    genHtmlProjectTable(project, location, tableDic, varDic, ensSizeDic,
                                     varSizeDic, latestPath, htmlcrdate, 
                               showXmlTAxis, showVarGrid, cdscanWarning, 
                             xmlTAxisMissingWaring, showXmlTAxisMissing)

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
    
    location = raw_input("Enter the location name [CAS, IITD] : ") 
    project = raw_input("Enter the project name [CMIP5] : ")
    datapath = raw_input("Enter the source project path : ")    
    print "The obtained data path is '%s'" % datapath   
    outpath = raw_input("Enter the html tables outpath : ")
    print "The index.html path will be ", outpath
    
    timeaxis = raw_input("Do you want to show 'start-end years' of xml [Y/n] : ")
    gridinfo = raw_input("Do you want to show 'grid type' of data variable [Y/n] : ")
    cdwarn = raw_input("Do you want to enable cdscan warning [Y/n] : ")
    missing = raw_input("Do you want to enable xml time axis missing time slice warning [Y/n] : ")
    
    if project in ['CMIP5', '']:
        project = 'CMIP5'
    # end of if project in ['CMIP5', '']:
    
    if location in ['CAS, IITD', '']:
        location = 'CAS, IITD'
    # end of if location in ['CAS, IITD', '']:
    
    if outpath in ['', None]:
        outpath = os.path.abspath(os.curdir)
    # end of if outpath in ['', None]:

    if timeaxis in ['', 'y', 'Y', 'yes']:
        # default enter takes 'yes'
        get_timeaxis = True
    else:
        get_timeaxis = False
    # end of if timeaxis in ['', 'y', 'Y', 'yes']:
    
    if gridinfo in ['', 'y', 'Y', 'yes']:
        # default enter takes 'yes'
        get_gridinfo = True
    else:
        get_gridinfo = False
    # end of if gridinfo in ['', 'y', 'Y', 'yes']:
    
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
    main(datapath, outpath, project, location, showXmlTAxis=get_timeaxis, 
         showVarGrid=get_gridinfo, cdscanWarning=cdwarn,
         xmlTAxisMissingWaring=missing, showXmlTAxisMissing=get_missing)

# end of if __name__ == '__main__':
