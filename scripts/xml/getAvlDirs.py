import os
import time


def createProjectList(datapath, project='CMIP5'):
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

    projpath = os.path.join(datapath, project)
    all_models = os.listdir(projpath)

    all_experiments = []
    all_frequencies = []
    all_realms = []
    all_vars = []
    all_ensembles = []

    for model in all_models:
        if model.startswith('.'): continue
        modelpath = os.path.join(projpath, model)
        experiments = os.listdir(modelpath)
        all_experiments += experiments

        for experiment in experiments:
            if experiment.startswith('.'): continue
            exppath = os.path.join(modelpath, experiment)
            freqs = os.listdir(exppath)
            all_frequencies += freqs

            for freq in freqs:
                if freq.startswith('.'): continue
                freqpath = os.path.join(exppath, freq)
                realms = os.listdir(freqpath)
                all_realms += realms

                for realm in realms:
                    if realm.startswith('.'): continue
                    realmpath = os.path.join(freqpath, realm)
                    variables = os.listdir(realmpath)
                    all_vars += variables

                    for var in variables:
                        if var.startswith('.'): continue
                        varpath = os.path.join(realmpath, var)
                        ensembles = os.listdir(varpath)
                        all_ensembles += ensembles
                    # end of for var in variables:
                # end of for realm in realms:
            # end of for freq in freqs:
        # end of for experiment in experiments:
    # end of for model in all_models:
    fname = project + '_Dataset_List.py'
    f = open(fname, 'w')
    docstr = """
    project : %s
    info : It contains all the available models, experiments,
        frequencies, realms, variables, ensembles list.
    generated by : This python module generated by the function
                'createProjectList()'self.
    Date : %s \n\n""" % (project, time.ctime())

    f.write('"""%s"""' % docstr)
    f.write("\n\n\n")
    f.write("all_models = " + repr(set(all_models)))
    f.write("\n\n")
    f.write("all_experiments = " + repr(set(all_experiments)))
    f.write("\n\n")
    f.write("all_frequencies = " + repr(set(all_frequencies)))
    f.write("\n\n")
    f.write("all_realms = " + repr(set(all_realms)))
    f.write("\n\n")
    f.write("all_vars = " + repr(set(all_vars)))
    f.write("\n\n")
    f.write("all_ensembles = " + repr(set(all_ensembles)))
    f.write("\n\n")
    f.close()
    print "Created %s which contains all the avilable list into it" % fname
    os.system("cp %s %s" % (fname, '../html/projectdatatypes_auto.py'))
    print "copied the same into '../html/projectdatatypes_auto.py'"
    os.system("cp %s %s" % (fname, '../mv/projectdatatypes_auto.py'))
    print "Also copied the same into '../mv/projectdatatypes_auto.py'"
# end of def createProjectList(datapath, project='CMIP5'):

if __name__ == '__main__':
    datapath = raw_input("Enter the data path : ")
    createProjectList(datapath)


