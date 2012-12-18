#! /usr/bin/env python

# tree.py
#
# Written by Doug Dahms
#
# Prints the tree structure for the path specified on the command line

from os import listdir, sep
from os.path import abspath, basename, isdir, isfile, join
from sys import argv

#dictionary containg the folder name with the number of files it contains
initialList={}
def tree(dir,initialList,padding, print_files=False):
    folderList = []
    fileList = []
    
    
    #t1 = re.compile('208|TFL|T1|t1')
    #dti = re.compile('[Dd][Tt][Ii].*\(.\)_\d+')
    #dki = re.compile('[Dd][Kk][Ii].*\(.\)_\d+')
    #rest = re.compile('[Rr][Ee][Ss][Tt]')
    #t2flair=re.compile('[Ff][Ll][Aa][Ii][Rr]')
    #t2tse=re.compile('[Tt][Ss][Ee]')
    #t1Num,dtiNum,dkiNum,restNum,t2flairNum,t2tseNum = 0
    
    for i in listdir(dir):
        try:
            if isdir(join(dir,i)):
                folderList.append(i)
                #appending name ****1
                toAdd={i:len(listdir(join(dir,i)))}
                initialList.update(toAdd)
            else:
                fileList.append(i)
        except:
            fileList.append(i)

    print padding[:-1] + '+-' + basename(abspath(dir)) + '/','\t\t{0} folders, {1} files'.format(len(folderList),len(fileList))
    #if t1.search(basename(abspath(dir))):
    #    t1Num = len(fileList)
    #    global t1Num
    #elif dti.search(basename(abspath(dir))):
    #    dtiNum = len(fileList)
    #    global dtiNum
    #elif dki.search(basename(abspath(dir))):
    #    dkiNum = len(fileList)
    #    global dkiNum 
    #elif rest.search(basename(abspath(dir))):
    #    restNum = len(fileList)
    #    global restNum
    #elif t2flair.search(basename(abspath(dir))):
    #    t2flairNum = len(fileList)
    #    global t2flairNum
    #elif t2tse.search(basename(abspath(dir))):
    #    t2tse.search = len(fileList)
    #    global t2tseNum
        
    padding = padding + ' '
    files = []
    if print_files:
        files = listdir(dir)
    else:
        files = [x for x in listdir(dir) if isdir(dir + sep + x)]
    count = 0
    for file in files:
        count += 1
        print padding + '|'
        path = dir + sep + file
        if isdir(path):
            if count == len(files):
                tree(path,initialList,padding + ' ', print_files)
            else:
                tree(path,initialList,padding + '|', print_files)
        else:
            print padding + '+-' + file 

    return initialList
    print 'haha',initialList

def usage():
    return '''Usage: %s [-f] <PATH>
Print tree structure of path specified.
Options:
-f      Print files as well as directories
PATH    Path to process''' % basename(argv[0])

def main():
    if len(argv) == 1:
        print usage()
    elif len(argv) == 2:
        # print just directories
        path = argv[1]
        if isdir(path):
            tree(path, ' ')
        else:
            print 'ERROR: \'' + path + '\' is not a directory'
    elif len(argv) == 3 and argv[1] == '-f':
        # print directories and files
        path = argv[2]
        if isdir(path):
            tree(path,initialList,' ', True)
        else:
            print 'ERROR: \'' + path + '\' is not a directory'
    else:
        print usage()

    print initialList

if __name__ == '__main__':
    main()
