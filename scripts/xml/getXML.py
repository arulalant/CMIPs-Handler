import os


def getXMLPath(datapath, model, experiment, freq, realm, var,
                                    ensemble, project='CMIP5', __DEBUG=0):
    """

    Written By : Arulalan.T

    Date : 09.09.2012

    """

    if not project in ['CMIP5']:
        # if some other project data directory structure is same as 'CMIP5'
        # means, then we can include that project name in the above if check
        # list.
        raise ValueError("'Method Not Implimented Yet' for other than 'CMIP5' Project Dataset!")
    # end of if not project in ['CMIP5']:

    xmlpath = os.path.join(datapath, project, model, experiment,
                                     freq, realm, var, ensemble)
    if os.path.isdir(xmlpath):
        return xmlpath
    else:
        if not __DEBUG:
            return None
        else:
            if not os.path.isdir(datapath):
                print "datapath doesn't exists, ", datapath
                return None
            projects = os.listdir(datapath)
            if project not in projects:
                print project, " project not available. Try the available projects ", projects
                return None
            projpath = os.path.join(datapath, project)
            models = os.listdir(projpath)
            if model not in models:
                print model, " model not available. Try the available models ", models
                return None
            modelpath = os.path.join(projpath, model)
            experiments = os.listdir(modelpath)
            if experiment not in experiments:
                print experiment, "experiment not available. Try the available experiments ", experiments
                return None
            exppath = os.path.join(modelpath, experiment)
            freqs = os.listdir(exppath)
            if freq not in freqs:
                print freq, " frequency not available. Try the available frequencies ", freqs
                return None
            freqpath = os.path.join(exppath, freq)
            realms = os.listdir(freqpath)
            if realm not in realms:
                print realm, "realm not available. Try the available realms ", realms
                return None
            realmpath = os.path.join(freqpath, realm)
            variables = os.listdir(realmpath)
            if var not in variables:
                print var, " variable not available. Try the available variables ", variables
                return None
            varpath = os.path.join(realmpath, var)
            ensembles = os.listdir(varpath)
            if ensemble not in ensembles:
                print ensemble, " ensemble not available. Try the available ensembles ", ensembles
                return None
        # end of if not __DEBUG:
    # end of if os.path.isdir(xmlpath):
# end of def getXMLPath(...):


def getXMLFile(datapath, model, experiment, freq, realm, var,
                  ensemble, project='CMIP5', extension='.xml', abspath=0, __DEBUG=0):

    """

    Written By : Arulalan.T

    Date : 09.09.2012

    """

    xmlpath = getXMLPath(datapath, model, experiment, freq, realm, var,
                                            ensemble, project, __DEBUG)
    if xmlpath:
        files = os.listdir(xmlpath)
        xmlfile = [f for f in files if f.endswith(extension)]

        if xmlfile:
            if __DEBUG and len(xmlfile) > 1:
                print "WARNING : More %r files are available in the path %r" % (extension, xmlpath)
                print "Returning the first xml file alone"
            # end of if __DEBUG and len(xmlfile) > 1:
            if abspath:
                return os.path.join(xmlpath, xmlfile[0])
            else:
                return xmlfile[0]
            # end of if abspath:
        else:
            if __DEBUG: print "No xml file exists in path ", xmlpath
            return None
        # end of if xmlfile:
    else:
        if __DEBUG: print "No such a directory or path exists ", xmlpath
        return None
    # end of if xmlpath:
# end of def getXMLFile(...):


