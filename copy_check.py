#!/opt/bin/python2.7
'''
2012_12_12
Kevin Cho
from USB hard-drive
find all new subjects
copy those folders into appropriate folders
append the log file
save patient number and name information automatically
into a log.txt
'''

import re
import time
import sys
import os
from os import join
import tree
import shutil
import getpass
import pickle
from progressbar import ProgressBar,Percentage,Bar

backupList=[]	#Append list to execute backup
copiedAtThisRound=[]	#Pickle dump list for the round of back up
initialList=[]

backUpTo=os.path.abspath('/volume1/CCNC_MRI') #Back up to
backUpFrom = os.path.abspath('/volumeUSB2/usbshare') #Find subj to back up from

if os.path.isfile(os.path.join(backUpFrom,"DO_NOT_DELETE_LOG.txt")):
    f = open(os.path.join(backUpFrom,"DO_NOT_DELETE_LOG.txt"),'r')
    alreadyCopied=pickle.load(f)
    f.close()
    print 'loaded log successfully'
    print alreadyCopied
else:
    alreadyCopied=[]
        

def main():
    '''
    test whether the source directory is a folder
    '''
    #directory = raw_input('\nwhere is the files ?:')  ---> for different sources
    if os.path.exists(backUpTo) & os.path.exists(backUpFrom) == True:
        os.system('clear')
        backUpConfirm(backUpFrom)
        if copiedAtThisRound!=[]:
            executeBackUp(backupList,backUpFrom)

def backUpConfirm(backUpFrom):
    '''
    show the list of folders under the backUpFrom
    if it is confirmed by the user
    excute backup
    '''
    dirList = [o for o in os.listdir(backUpFrom) if os.path.isdir(os.path.join(backUpFrom,o))]
    #removing subjects already copied according to the log file
    for copied in alreadyCopied:
        try:
            dirList.remove(copied)
        except:
            continue
    #removing folder names begining with '.' and '$'
    # check out filter
    withDot=[i for i in dirList if i.startswith('.')]
    withDol=[i for i in dirList if i.startswith('$')]
    dirList = [item for item in dirList if item not in withDot]
    dirList = [item for item in dirList if item not in withDol]

    for folderName in dirList:
        subjFolder = os.path.join(backUpFrom,folderName)
        stat = os.stat(subjFolder)
        created = os.stat(subjFolder).st_mtime
        asciiTime = time.asctime( time.gmtime( created ) )
        print '''
        ------------------------------------
        ------{0} 
        created on ( {1} )
        ------------------------------------
        '''.format(folderName,asciiTime)
        response = raw_input('\nIs this the name of the subject you want to back up? [Yes/No/Quit] :')
        if re.search('[yY]|[yY][Ee][Ss]',response):
            backUpAppend(subjFolder)
        elif re.search('[Dd][Oo][Nn][Ee]|stop|[Qq][Uu][Ii][Tt]|exit',response):
            break
        else:
            continue

def backUpAppend(subjFolder):
    print '\n'
    #countFile contains the tuples of image name and count number
    #countFile=[(image name,count number)]
    groupName, countFile = countCheck(subjFolder)
    subjInitial, fullname, subjNum = getName(subjFolder)
    targetDir = os.path.join(backUpTo, groupName)
    maxNum = maxGroupNum(targetDir)
    #temp file for adding count   
    f = open(os.path.join(targetDir,'.{}'.format(maxNum)),'w')
    f.write('temp')
    f.close()

    targetName=groupName+maxNum+'_'+subjInitial
    targetFolder=os.path.join(targetDir,targetName)
    print '\t{0} will be saved as {1} in \n\t{2}'.format(os.path.basename(subjFolder),targetName,targetFolder)

    if re.search('[yY]|[yY][eE][sS]',raw_input('\tCheck? [Yes/No] :')):
        toBackUp=(subjFolder,targetFolder,fullname,subjNum,groupName)
        backupList.append(toBackUp)
        copiedAtThisRound.append(os.path.basename(subjFolder))
        print '\t------\n\tQued to be copied!'
        makeTable(fullname,subjInitial,subjNum,groupName,targetName,countFile)

def makeTable(fullname,subjInitial,subjNum,groupName,targetName,countFile):
    print fullname,subjInitial,subjNum,groupName,targetName,countFile
    print '{}\t{}\t{}\t{}\t{}\t'.format(fullname,subjInitial,subjNum,groupName,targetName),
    
    #grep image numbers
    t1 = re.compile(r'TFL\S*|\S*T1\S*|\S*t1\S*')
    #dti = re.compile(r'\S*[Dd][Tt][Ii]\S*') 
    #dki = re.compile(r'\S*[Dd][Kk][Ii]\S*') 
    dti = re.compile(r'[Dd][Tt][Ii]\S*\(.\)_\d+\S*') 
    dki = re.compile(r'[Dd][Kk][Ii]\S*\(.\)_\d+\S*') 
    rest = re.compile(r'\S*[Rr][Ee][Ss][Tt]\S*') 
    t2flair = re.compile(r'\S*[Ff][Ll][Aa][Ii][Rr]\S*') 
    t2tse = re.compile(r'\S*[Tt][Ss][Ee]\S*')
   
    #T1, DTI, DKI, REST, T2FLAIR, T2TSE
    imageNums=[]
    for imagePattern in t1,dti,dki,rest,t2flair,t2tse:
        nameUsed = imagePattern.search(' '.join(countFile.viewkeys()))
        if nameUsed:
            imageNums.append(str(countFile.get(nameUsed.group(0))))
        else:
            imageNums.append(str(0))
    print '{}\t{}\t{}\t{}\t{}\t{}'.format(imageNums[0],imageNums[1],imageNums[2],imageNums[3],imageNums[4],imageNums[5])
    
    totalList=[fullname,subjInitial,subjNum,groupName,targetName,imageNums[0],imageNums[1],imageNums[2],imageNums[3],imageNums[4],imageNums[5],time.ctime(time.time()),getpass.getuser()]
    print totalList
    f = open(os.path.join(backUpFrom,'spread.txt'),'a')
    f.write('\t'.join(totalList))
    f.write('\n')
    f.close()

    #'DKI_30D_B-VALUE_NB_06_(3)_0010' 'DTI_64D_B1K(2)_FA_0008' 'DKI_30D_B-VALUE_NB_06_(3)_COLFA_0013'  'PHOENIXZIPREPORT_0099' 'DKI_30D_B-VALUE_NB_06_(3)_EXP_0011'    'REST_FMRI_PHASE_116_(1)_0005' 'DKI_30D_B-VALUE_NB_06_(3)_FA_0012'

def countCheck(subjFolder):
    emptyList = {} 
    countResult=tree.tree(subjFolder,emptyList,'\t')
    print '\n'
    if re.search('[yY]|[yY][eE][sS]',raw_input('\tDo file numbers match? [Yes/No] :')):
        initialList.append(countResult)
        groupName = group()
        return groupName,countResult
        print '\t{0}\n\tadded to the back up list\n\n'.format(subjFolder)
    else:
        print '\tNumbers does not match, will return error.\n\tCheck the directory manually'


def group():
    possibleGroups = str('CHR,DNO,EMO,FEP,GHR,NOR,OCM,ONS,OXY,PAIN,SPR,UMO').split(',')
    groupName=''
    while groupName=='':
        groupName=raw_input('\twhich group ? [CHR/DNO/EMO/FEP/GHR/NOR/OCM/ONS/OXY/PAIN/SPR/UMO] :') 
        groupName = groupName.upper()
        if groupName not in possibleGroups:
            print 'not in groups, let Kevin know.'
            groupName=''
        else:
            return groupName
 
def getName(subjFolder):
    '''
    will try getting the name and subj number from the source folder first
    if it fails,
    will require user to type in the subjs' name
    '''
    if re.findall('\d{8}',os.path.basename(subjFolder)):
        subjNum = re.search('(\d{8})',os.path.basename(subjFolder)).group(0)
        subjName = re.findall('[^\W\d_]+',os.path.basename(subjFolder))
       
        #Appending first letters
        subjInitial=''
        for i in subjName:
            subjInitial = subjInitial + i[0]

        fullname=''
        for i in subjName:
            fullname = fullname + i[0] + i[1:].lower()
        
        return subjInitial, fullname, subjNum
    
    #if the folder shows no pattern 
    else:
        subjName = raw_input('\tEnter the name of the subject in English eg.Cho Kang Ik:')
        subjNum = raw_input("\tEnter subject's 8digit number eg.45291835:")

        subjwords=subjName.split(' ') 
        fullname=''
        subjInitial=''
        for i in subjwords:
            fullname=fullname + i[0].upper()
            fullname=fullname + i[1:]
            subjInitial=subjInitial+i[0][0]
        print subjInitial
        return subjInitial.upper(),fullname,subjNum
       
def maxGroupNum(targetDir):
    maxNumPattern=re.compile('\d+')
    mx = 0
    for string in maxNumPattern.findall(' '.join(os.listdir(targetDir))):
        if int(string) > mx:
            mx = int(string)
    
    highest = mx +1
    if highest<10:
        highest ='0'+str(highest)
    else:
        highest = str(highest)
    return highest

def executeBackUp(backupList,backUpFrom):
    pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=len(backupList)).start()
    num=0
    maxNum=len(backupList)
    perOne=1/(maxNum*3)

    for i in backupList:
        shutil.copytree(i[0],i[1])
        pbar.update(num+perOne)
        log(i[0],i[1],i[2],i[3],i[4])
        post_check(backUpFrom)
        pbar.update(num+perOne)
        time.sleep(0.01)
        pbar.update(num+perOne)
    pbar.finish()
            

def log(source,destination,fullname,subjNum,groupName): 
    try:
        timeInfo = time.gmtime(os.stat(source).st_mtime)
        prodT=str(timeInfo.tm_year)+'_'+str(timeInfo.tm_mon)+'_'+str(timeInfo.tm_mday)
        prodH=str(timeInfo.tm_hour)+':'+str(timeInfo.tm_min)
        user=getpass.getuser()
        currentTime=time.ctime()
        with open(os.path.join(destination,'log.txt'),'w') as f:
            f.write('''Subject Full Name = {6}
Subject number = {7}
Group Name = {8}
Source : {0}
Destination : {1}
Data produced in : {2}\t{3}
Data copied at : {4}
Copied by : {5}'''.format(source,destination,prodT,prodH,currentTime,user,fullname,subjNum,groupName))
    except:
        print 'log failed'

#Pickle dump the list of subjects backed up in this round
def post_check(backUpFrom):
    with open(os.path.join(backUpFrom,"DO_NOT_DELETE_LOG.txt"),'w') as f:
        currentTime=time.ctime()
        pickle.dump(alreadyCopied+copiedAtThisRound,f)


if __name__=='__main__':
    main()
