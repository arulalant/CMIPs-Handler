import os, re


def getHumanReadable(size, precision=2):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while size > 1024:
        suffixIndex += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return  "%.*f %s" % (precision, size, suffixes[suffixIndex])
# end of def GetHumanReadable(size,precision=2):


def getBytes(humanReadable, precision=2):
    if humanReadable.isdigit():
        return float(humanReadable)
    # end of if humanReadable.isdigit():

    suffixes = [('B'), ('K', 'KB'), ('M', 'MB'), ('G', 'GB'), ('T', 'TB')]
    bytes = 1.0

    suf = ''.join(re.findall(r'[A-Z]', humanReadable))
    val = float(humanReadable.split(suf)[0])

    for suffix in suffixes:
        if suf in suffix:
            return round(val * bytes, precision)
        # end of if suf in suffix:
        bytes *= 1024.0
    # end of for suffix in suffixes:
# end of def getBytes(humanReadable, precision=2):


def getDuplicate(path, extension):
    """
    Get Duplicate file name and its paths will be written in 'duplicates.csv'.

    Written By : Arulalan.T

    Date : 24.08.2012

    """

        
    # find cmd option setup 
    if extension == '':
        find = '-type f'
        print "Finding all duplicate ..."
    else:
        find = "-name '*.%s'" % extension
        print "Finding '*.%s' duplicate ..." % extension
    # end of if extension == '':
    
    # In the below find cmd option -print0 and xargs -0 is important and 
    # useful to handle/pass the filename to the md5sum, even though file name
    # contains many white spaces and special characters.
    # uniq -D option gives the resultant unique of duplicates files.
    cmd = "find %s %s -print0 | xargs -0 md5sum | sort | uniq -D -w 34" % (path, find)
    fin = os.popen(cmd)
    res = fin.readlines()
    result = {}
    if res:
        fout = open('duplicates.csv', 'w')
        fout.write("File Name, Duplicate Path, File Size\n")
        for line in res:
            # get the md5   
            md5 = line.split()[0]       
            # if filepath with md5. So we will the correct file path even 
            # though file name contains many white spaces. 
            fpath = line.split(md5)[1]
            # Also remove the '\n' char alone. We do not remove white space 
            # at the end of the filename.            
            fpath = fpath.replace('\n', '')
            # Remove the white space at the begining of the filepath.
            fpath = fpath.lstrip()
            fname = fpath.split('/')[-1]            
            if not fname in result:
                result[fname] = []
            # end of if not fname in result:
            # finally got the proper filepath without leading white spaces 
            # and with trailing white spaces and removed the '\n' char alone.
            result[fname].append(fpath)
        # end of for line in res:

        total = 0
        for fname in result:
            fout.write(fname)
            for fpath in result[fname]:       
                # execute cms to get the size of the file         
                sf = os.popen("du -h '%s' " % fpath)
                # get the size of the file 
                size = sf.readline().split()[0]         
                size = '0 B' if size == '0' else size
                fout.write("," + fpath + "," + size + "\n")
                # get file size in bytes instead of humanreadable string
                size = getBytes(size)
                # add to the total
                total += size
            # end of for fpath in result[fname]:
            fout.write("\n")
        # end of for fname in result:

        print "Found ", len(result), " duplicate files."
        # get the humanReadable form of the total size of bytes.
        total = getHumanReadable(total)
        fout.write("Total size of the duplicate files, Count = ")
        fout.write(str(len(result)) + "," + total + "\n")
        fout.close()
        print "Total size of the duplicate files = ", total
        print "\n Results saved in 'duplicates.csv'"
    else:
        print "\n No duplicates found"
    # end of if res:
# end of def getDuplicate(path, extension):

if __name__ == '__main__':

    path = raw_input("Enter the path : ")
    ext = raw_input("Enter the lookup extension (eg :- nc) : ")
    getDuplicate(path, ext)
# end of if __name__ == '__main__':

