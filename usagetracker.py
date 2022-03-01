'''AddictFree 2.0 is a program that can track application usage, provide
statistics of daily and monthly usage. It can also block programs based on
a time limit. Added to that is a feature to also block the user input,
i.e keyboard and mouse input, so that the user may take a break from
their computer. This app is targeted for those to struggle to organize
their work routine or would like to limit their computer usage without
the hassle of creating reminders or schedules and for those who
find it difficult to stick with their plans.'''



import tkinter as tk
from tkinter import *
from tkinter import ttk
import csv
import pickle
import os
from tkinter import filedialog
import psutil as ps
import time as t
import threading as th
import winapps
import subprocess as sp
import win32api
import win32com.client
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from matplotlib.figure import Figure
#from os import _exit FOR EMERGENCY ABORTION, BUT WE DONT NEED TO USE IT
from ctypes import windll
import traceback


months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
DaYs = []

for x in range(31):
    DaYs.append(x+1)

theMonth = 'January'
theDay = '1'


listOfBlockApps = []
notifsShown = []
stopThreads = False

programLocations = []
programProcesses = []
programsBeingTracked = []
programStatusVar = None

allAppsEXES = []
allAppsNames = []
allAppsLocations = []
selectedIndex = 0

customEXES = []
customLocations = []
customNames = []

canvas = None
toolbarFrame = None
currentMenu = 'mainMenu'

if os.path.exists(os.getcwd() + '\\' + 'settings.bin'): 
    f = open("settings.bin","rb")
    try:
        programProcesses = pickle.load(f)
        programLocations = pickle.load(f)
    except:
        print("Done loading maybe")
    f.close()
else:
    f = open("settings.bin","wb")
    f.close()

print(programProcesses,programLocations)


if os.path.exists(os.getcwd() + '\\' + 'customApps.bin'): 
    print('yes')
    f = open("customApps.bin","rb")
    try:
        customEXES = pickle.load(f)
        customNames = pickle.load(f)
        customLocations = pickle.load(f)

        for exe in customEXES:
            allAppsEXES.append(exe)

        for name in customNames:
            allAppsNames.append(name)

        for loc in customLocations:
            allAppsLocations.append(loc)

        print(allAppsNames)
    except:
        print("Done loading maybe")
    f.close()
else:
    f = open("customApps.bin","wb")
    f.close()


if os.path.exists(os.getcwd() + '\\' + 'blockApps.bin'): 
    f = open("blockApps.bin","rb")
    try:
        listOfBlockApps = pickle.load(f)
    except:
        print("Done loading blockApps maybe")
    f.close()
else:
    f = open("blockApps.bin","wb")
    f.close()


def removeProc(item,delData):
    pIndex = programProcesses.index(item)
    removeProcFromSettings(programLocations[pIndex], item)
    if(delData):
        file = item.replace('exe','csv')
        os.remove(file)

    programLocations.pop(pIndex)
    programProcesses.pop(pIndex)
    print("Sucessfully removed",item)

    #print(programLocations,programProcesses,programsBeingTracked)


def getProcName(item):
    for i in range(len(item)-1,0,-1):
        if(item[i] == "\\"):
            index = i+1
            return item[index::]
            break


def addProc(item):
    programLocations.append(item)
    for i in range(len(item)-1,0,-1):
        if(item[i] == "\\"):
            index = i+1
            theProcess = item[index::]
            programProcesses.append(theProcess)

            addProcToSettings(item,theProcess)

            fileName = f"{item[index:-4:]}.csv"
            if os.path.exists(fileName):
                break
            else:
                f = open(fileName,"w")
                f.close()
                break

    

def addProcToSettings(loc,proc):
    oldProcs = []
    oldLocs = []
    try:
        f = open('settings.bin','rb')
        oldProcs = pickle.load(f)
        oldLocs = pickle.load(f)
        f.close()
    except:
        print("unable to read settings")

    oldProcs.append(proc)
    oldLocs.append(loc)
    try:
        g = open('settings.bin','wb')
        pickle.dump(oldProcs,g)
        pickle.dump(oldLocs,g)
        g.close()
    except:
        print("unable to write settings")

def removeProcFromSettings(loc,proc):
    oldProcs = []
    oldLocs = []
    try:
        f = open('settings.bin','rb')
        oldProcs = pickle.load(f)
        oldLocs = pickle.load(f)
        f.close()
    except:
        print('unable to read settings')

    oldProcs.remove(proc)
    oldLocs.remove(loc)

    try:
        g = open('settings.bin','wb')
        pickle.dump(oldProcs,g)
        pickle.dump(oldLocs,g)
        g.close()
    except:
        print('unable to write settings')

def addCustomProc(item):
    allAppsLocations.append(item)
    for i in range(len(item)-1,0,-1):
        if(item[i] == "\\"):
            index = i+1
            theProcess = item[index::]
            allAppsEXES.append(theProcess)
            name = getFileDescription(item)
            allAppsNames.append(name)

            customEXES.append(theProcess)
            customNames.append(name)
            customLocations.append(item)

            k = open('customApps.bin','wb')
            pickle.dump(customEXES,k)
            pickle.dump(customNames,k)
            pickle.dump(customLocations,k)

            print(item,theProcess,name)
            break

def getTargetOfShortcut(path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(path)
    return shortcut.targetPath


def save_tracked_info(app,timeSpent):
    dateToday = formatted_time()
    formattedDate = f'{str(dateToday[0])} {str(dateToday[1])} {str(dateToday[2])}'
    fields = list()
    allData = list()

    tFormat = f'{timeSpent[0][3]}:{timeSpent[0][4]}:{timeSpent[0][5]} {timeSpent[1][3]}:{timeSpent[1][4]}:{timeSpent[1][5]}'

    f = open(app.replace('exe','csv'),'r',newline='')
    rr = csv.reader(f)
    for i in rr:
        allData.append(i)

    f.close()
    if allData != [] and allData != None:
        fields = allData[0]
        requiredColumn = 0
        if formattedDate in fields:
            requiredColumn = fields.index(formattedDate)
            for j in range(1,len(allData)):
                if allData[j][requiredColumn] == 'empty':
                    allData[j][requiredColumn] = tFormat
                elif j == len(allData)-1:
                    newRow = list()
                    for i in fields:
                        newRow.append('empty')
                    allData.append(newRow)

                    allData[j+1][requiredColumn] = tFormat

            h = open(app.replace('exe','csv'),'w',newline='')
            wr0 = csv.writer(h)
            wr0.writerows(allData)
            h.close()
        else:
            print("putting new date yo")
            fields = allData[0]
            fields.append(formattedDate)
            for i in range(len(allData)):
                while True:
                    if len(allData[i]) < len(fields):
                        allData[i].append('empty')
                    else:
                        break

            print(allData)
                        
            requiredColumn = fields.index(formattedDate)
            for j in range(1,len(allData)):
                if allData[j][requiredColumn] == 'empty':
                    allData[j][requiredColumn] = tFormat
                    break
                elif j == len(allData)-1:
                    newRow = list()
                    for i in fields:
                        newRow.append('empty')
                    allData.append(newRow)

                    allData[j+1][requiredColumn] = tFormat
                    break

            h = open(app.replace('exe','csv'),'w',newline='')
            wr1 = csv.writer(h)
            wr1.writerows(allData)
            h.close()
    else:
        g = open(app.replace('exe','csv'),'w',newline='')
        wr2 = csv.writer(g)
        wr2.writerow([formattedDate])
        wr2.writerow([tFormat])
        g.close()

def selectFile():
    tkRoot = tk.Tk()
    tkRoot.withdraw()
    file_path = filedialog.askopenfilename()

    if(file_path[-1:-4:-1] == "exe"):
        file_path = file_path.replace('/','\\')

        if file_path in allAppsLocations:
            prAlreadyError = tk.messagebox.showerror("ERROR",'Program was found in list already!')
        else:
            print("Successfully added: ",file_path)
            addCustomProc(file_path)
        

        #addProc(file_path)
    else:
        prIncorrectError = tk.messagebox.showerror("ERROR","Program is of incorrect format or is not an .exe")



def get_time_now():
    return t.localtime()[0:6]


def formatted_time():
    theTime = get_time_now()
    month = months[theTime[1] - 1]
    l = [theTime[2], month, theTime[0], theTime[3],theTime[4],theTime[5]]
    return l



def list_addedprocesses():
    count = 1
    for i in programProcesses:
        print(count,i)
        count += 1

def check_blocking_tasks(prInfo):
    global notifsShown
    if(stopThreads):
        return
    pName = prInfo[0]
    timeLimit = prInfo[1]
    notifyPrior = prInfo[2]
    blockUserInputMins = prInfo[3]
    forceQuitOrNot = prInfo[4]
    try:
        allFileData = []
        f = open(pName.replace('exe','csv'),'r')
        rr = csv.reader(f)

        for i in rr:
            allFileData.append(i)

        fields = allFileData[0]

        totalTimeSpent = 0

        dateToday = formatted_time()
        formattedDate = f'{str(dateToday[0])} {str(dateToday[1])} {str(dateToday[2])}'
        if formattedDate in fields:
            indexOfColumn = fields.index(formattedDate)
            for m in range(1,len(allFileData)):
                timeStamp = allFileData[m][indexOfColumn]
                totalTimeSpent += get_time_spent_between_daily(timeStamp)

        finalMessage = ''
        if (totalTimeSpent > timeLimit*60*60):
            finalMessage += f'Time limit of {str(timeLimit)} hr reached for {str(pName)}! '
        else:
            print(totalTimeSpent,'ha???')
            print(totalTimeSpent,'ha???')
            print(totalTimeSpent,'ha???')
            print((timeLimit*60*60 - notifyPrior*60),'hahshah')
            if totalTimeSpent > (timeLimit*60*60 - notifyPrior*60) and pName not in notifsShown:
                notifyUserMSG = tk.messagebox.showwarning('WARNING',f'You have less than {notifyPrior} mins before {pName} will get blocked! Please save your work as a precaution :)')
                notifsShown.append(pName)
            else:
                print('muwahwahwha')
            return
        if forceQuitOrNot:
            finalMessage += 'Program has been automatically terminated. '
        if(blockUserInputMins > 0):
            finalMessage += f'Also blocking user input for {str(blockUserInputMins)} mins.'

        finalMessage += "CLOSING IN 10 SECONDS!"

        specialWindow = Tk()
        specialWindow.withdraw()
        specialWindow.after(10000,specialWindow.destroy)
        finalMessageGUI = tk.messagebox.showwarning("WARNING",finalMessage,master=specialWindow)
        
        if (totalTimeSpent > timeLimit*60*60):
            if forceQuitOrNot:
                for pr in ps.pids():
                    try:
                        p = ps.Process(pr)
                    except:
                        continue
                    if p.name() == pName:
                        #os.kill(p.pid, signal.SIGKILL)
                        p.terminate()
                        break
            if(blockUserInputMins > 0):
                windll.user32.BlockInput(True)
                t.sleep(blockUserInputMins*60)
                windll.user32.BlockInput(False)
    except:
        print(traceback.print_exc())
        print(":) :(")


def trackTime(process):
    for programBlocked in listOfBlockApps:
        if process in programBlocked:
            print('Can block:',process)
            brThread = th.Thread(target=check_blocking_tasks,args=(programBlocked,))
            brThread.start()
            #check_blocking_tasks(programBlocked)
            break
        else:
            print("Not eligible for block:",process)

    print("Tracking",process)
    print(__name__)
    startTime = t.time()
    startDate = formatted_time()
    if(currentMenu == 'trackingMenu'):
        set_program_status(2,process)
        #programStatusVar.set('Program Status: RUNNING!')

    while not stopThreads:
        if(currentMenu == 'trackingMenu'):
            set_program_status(2,process)
            #programStatusVar.set('Program Status: RUNNING!')
        found = False
        for pr in ps.pids():
            try:
                p = ps.Process(pr)
            except:
                continue
            if(process == p.name()):
                found = True
                break

        if(found == True):
            found = False
        else:
            break

        currentTime = t.time()
        currentDate = formatted_time()
        if currentTime - startTime > 60:
            #TIME TO SAVE THE DATA AND ALSO CHECK IF BLOCKING TIME
            timeStamp = [startDate,currentDate]
            save_tracked_info(process,timeStamp)
            startTime = t.time()
            startDate = formatted_time()

            for programBlocked in listOfBlockApps:
                if process in programBlocked:
                    print('Can block:',process)
                    brThread = th.Thread(target=check_blocking_tasks,args=(programBlocked,))
                    brThread.start()
                    #check_blocking_tasks(programBlocked)
                    break
                else:
                    print("Not eligible for block:",process)
        else:
            t.sleep(2)

    endTime = t.time()
    endDate = formatted_time()
    programsBeingTracked.remove(process)
    print(endTime-startTime,"was spent on this program: ",process)
    print("Program was started on",startDate,"and ended on",endDate)
    if(currentMenu == 'trackingMenu'):
        set_program_status(1,process)
        #programStatusVar.set('Program Status: Not running')
    #timeStamp = endTime-startTime
    timeStamp = [startDate,endDate]
    save_tracked_info(process,timeStamp)




def Update_TrackingInfo():

    while not stopThreads:
        for pr in ps.pids():
            try:
                p = ps.Process(pr)
            except:
                continue
            if(p.name() in programProcesses and p.name() not in programsBeingTracked):
                thread = th.Thread(target=trackTime,args=(p.name(),))
                thread.start()
                #thread.join()
                programsBeingTracked.append(p.name())
                print("Lets go!")
                #trackTime(p.name())

        t.sleep(2)



trackingThread = th.Thread(target=Update_TrackingInfo)
trackingThread.start()
#trackingThread.join()

def track_button():
    delMenu()
    buildTrackingMenu()

def usage_button():
    delMenu()
    buildUsageMenu()

def block_button():
    delMenu()
    buildAppBlockingMenu()

def quit_button():
    global stopThreads
    print("GOODBYE")
    stopThreads = True
    appWindow.withdraw()
    t.sleep(2)
    os._exit(0)

def search_by_input(event):
    value = event.widget.get()

    if value == '':
        drpCombo['values'] = allAppsNames
    else:
        data = []
        for item in allAppsNames:
            if value.lower() in item.lower():
                data.append(item)

        drpCombo['values'] = data


def buildMenu():
    global title,button1,button2,button3,button4,currentMenu
    currentMenu = 'mainMenu'
    title = tk.Label(appWindow,text='AddictFree 2.0',bg='#4FC3F7',font=('Roboto',50))
    title.grid(row=0,column=1)


    button1 = tk.Button(appWindow,text='Track Application',fg='#000000',bg='#8BC34A',font=('Roboto',20,'bold'),command=track_button)
    button2 = tk.Button(appWindow,text='Usage Stats',fg='#000000',bg='#8BC34A',font=('Roboto',20,'bold'),command=usage_button)
    button3 = tk.Button(appWindow,text='App Blocker',fg='#000000',bg='#8BC34A',font=('Roboto',20,'bold'),command=block_button)
    button4 = tk.Button(appWindow,text='Save and Quit',fg='#000000',bg='#FF0000',font=('Roboto',20,'bold'),command=quit_button)

    button1.grid(row=1,column=1,pady=25)
    button2.grid(row=2,column=1,pady=25)
    button3.grid(row=3,column=1,pady=25)
    button4.grid(row=4,column=1,pady=25)


def delMenu():
    title.destroy()
    button1.destroy()
    button2.destroy()
    button3.destroy()
    button4.destroy()

def getFileDescription(windows_exe):
    try:
        language, codepage = win32api.GetFileVersionInfo(windows_exe, '\\VarFileInfo\\Translation')[0]
        stringFileInfo = u'\\StringFileInfo\\%04X%04X\\%s' % (language, codepage, "FileDescription")
        description = win32api.GetFileVersionInfo(windows_exe, stringFileInfo)
    except:
        description = "unknown"
        
    return description

def removeGraph():
    if canvas == None:
        return
    canvas.get_tk_widget().destroy()
    #toolbarFrame.destroy()
    print("Destroyed?")

def updateGraph(app):
    removeGraph()
    showStatsGraph(app,'hourly',True)

def buildUsageMenu():
    global title,newFrame,drpUCombo,currentMenu
    global theMonth,theDay
    global hourlyButton,monthlyButton,dailyButton,monthChoosingDrp
    currentMenu = 'usageMenu'

    title = tk.Label(appWindow,text='AddictFree 2.0',bg='#4FC3F7',font=('Roboto',50))
    title.grid(row=0,column=1)

    dateToday = formatted_time()

    newFrame = Frame(appWindow,bg='#212121')
    newFrame.grid(row=1,column=1,pady=20)

    graph_type = 'hourly'

    def update_month_chosen():
        nonlocal chosenMonth
        global theMonth
        print('yessagoiwahgioahiog')
        theMonth = chosenMonth.get()
        removeGraph()
        showStatsGraph(selectedAppU.get(), graph_type,False)

    def update_day_chosen():
        nonlocal chosenDay
        global theDay
        print('yessagoiwahgioahiog')
        theDay = chosenDay.get()
        removeGraph()
        showStatsGraph(selectedAppU.get(), graph_type,False)

    chosenMonth = StringVar()
    chosenMonth.set(dateToday[1])
    chosenMonth.trace('w', lambda name, index, mode, chosenMonth=chosenMonth: update_month_chosen())
    theMonth = chosenMonth.get()

    chosenDay = StringVar()
    chosenDay.set(dateToday[0])
    chosenDay.trace('w', lambda name, index, mode, chosenDay=chosenDay: update_day_chosen())
    theDay = chosenDay.get()

    def set_graph_type(type):
        nonlocal graph_type
        global monthChoosingDrp,dayChoosingDrp,dayChoosingDrpDescrip,monthChoosingDrpDescrip
        graph_type = type
        removeGraph()

        def clearAll():
            monthChoosingDrp.destroy()
            monthChoosingDrpDescrip.destroy()
            dayChoosingDrp.destroy()
            dayChoosingDrpDescrip.destroy()
        if type == 'daily':
            try:
                clearAll()
            except:
                print('aga')
            monthChoosingDrpDescrip = Label(newFrame,text='Choose Month: ',fg='#FFC107',bg='#212121',font=('Roboto','15'))
            monthChoosingDrp = ttk.Combobox(newFrame,value=months,textvariable=chosenMonth,font=('Roboto','15'))
            monthChoosingDrpDescrip.grid(row=3,column=1)
            monthChoosingDrp.grid(row=3,column=2)
        elif type == 'hourly':
            try:
                clearAll()
            except:
                print('aga')
            dayChoosingDrpDescrip = Label(newFrame,text='Choose Day: ',fg='#FFC107',bg='#212121',font=('Roboto','15'))
            dayChoosingDrp = ttk.Combobox(newFrame,value=DaYs,textvariable=chosenDay,font=('Roboto','15'))
            dayChoosingDrp.grid(row=3,column=1)
            dayChoosingDrpDescrip.grid(row=3,column=0)  
            monthChoosingDrpDescrip = Label(newFrame,text='Choose Month: ',fg='#FFC107',bg='#212121',font=('Roboto','15'))
            monthChoosingDrp = ttk.Combobox(newFrame,value=months,textvariable=chosenMonth,font=('Roboto','15'))
            monthChoosingDrpDescrip.grid(row=3,column=2)
            monthChoosingDrp.grid(row=3,column=3)
        else:
            try:
                clearAll()
            except:
                print('hm what')
        showStatsGraph(selectedAppU.get(), graph_type,False)



    selectedAppU = StringVar()
    selectedAppU.trace('w', lambda name, index, mode, selectedAppU=selectedAppU: update_selection())

    def update_selection():
        
        removeGraph()
        showStatsGraph(selectedAppU.get(),graph_type,False)

    listOfRecordedApps = list()
    print(programProcesses)
    for i in programProcesses:
        file = i.replace('exe','csv')
        if os.path.exists(file):
            data = []
            f = open(file,'r')
            rr = csv.reader(f)
            for k in rr:
                data.append(k)

            if data != None and data != []:
                listOfRecordedApps.append(i)
            
    if(len(listOfRecordedApps) == 0):
        noAppsRecMSG = tk.messagebox.showerror('ERROR','No apps are being tracked. Cannot use stats feature without enabling tracking first.')
        backButton()
        return
    
    drpUCombo = ttk.Combobox(newFrame,value=listOfRecordedApps,textvariable=selectedAppU,font=('Roboto',25))

    drpUCombo.current(0)
    #drpUCombo.bind('<KeyRelease>', search_by_input)
    drpUCombo.grid(row=1,column=1,pady=25)

    hourlyButton = Button(newFrame,text='Hourly',bg='#FFC107',font=('Roboto','15','bold'),command=lambda: set_graph_type('hourly'))
    dailyButton = Button(newFrame,text='Daily',bg='#FFC107',font=('Roboto','15','bold'),command=lambda: set_graph_type('daily'))
    #monthlyButton = Button(newFrame,text='Monthly',fg='blue',command=lambda: set_graph_type('monthly'))

    hourlyButton.grid(row=2,column=0)
    dailyButton.grid(row=2,column=2)
    #monthlyButton.grid(row=2,column=2)
    set_graph_type(graph_type)

def delUsageMenu():
    try:
        removeGraph()
        title.destroy()
        drpUCombo.destroy()
        newFrame.destroy()
        hourlyButton.destroy()
        monthlyButton.destroy()
        monthChoosingDrp.destroy()
        dailyButton.destroy()
    except:
        print('lol')


def showStatsGraph(app,type,today):
    print(type)
    global canvas,toolbarFrame
    data = {}
    theData = list()
    try:
        f = open(app.replace('exe','csv'),'r')
        #appIndex = allAppsEXES.index(app)
        #print(os.getcwd() + '\\'+app.replace('exe','csv'))
        #if not os.path.exists(os.getcwd() + '\\'+app.replace('exe','csv')):
        #    print("whatever")
        #    return
    except:
        noStatsMsg = tk.messagebox.showinfo('INFO','No stats available for this app!')
        return
    fr = csv.reader(f)
    for i in fr:
        theData.append(i)
    f.close()
    if theData == None or theData == []:
        noStatsMsg = tk.messagebox.showinfo('INFO','You have never used this app yet!')
        return
    timeUnit = ''

    fields = theData[0]

    for j in range(len(fields)):
        totalTime = 0
        timeList = []
        for k in range(1,len(theData)):
            theTime = theData[k][j]
            if theTime != 'empty':
                #totalTime += round(float(theTime),2)
                timeList.append(theTime)
        data[fields[j]] = timeList
    #data = {'C':20, 'C++':15, 'Java':30,'Python':35,'C#':100,'Ruby':10,'PHP':17,'SQL':27,'Javascript':91,'Swift':69}
    dates = list(data.keys())
    timeSpent = list(data.values())
    print(data)

    allTimeData = []

    for times in timeSpent:
        for time in times:
            timeStamps = time.split()
            startTimeStamp = timeStamps[0].split(':')
            endTimeStamp = timeStamps[1].split(':')
            allTimeData.append([startTimeStamp,endTimeStamp])


    if type == 'hourly':
        hourlyList = []
        dateToday = formatted_time()
        formattedDate = f'{str(dateToday[0])} {str(dateToday[1])} {str(dateToday[2])}'

        if(today):
            hourlyList = get_hourly_datalist(data,dateToday[0],dateToday[1])
        else:
            hourlyList = get_hourly_datalist(data,theDay,theMonth)
        for z in hourlyList:
            if z != 0:
                break
        else:
            return
        hours = []
        for b in range(24):
            hours.append(b)
        usedHrs = 0
        for i in hourlyList:
            if i > 0:
                usedHrs += 1
        print(hourlyList)
        avgTime = sum(hourlyList)/usedHrs
        print(avgTime,'averga time!')
        if avgTime > 60:
            timeUnit = '(m)'
            for j in range(len(hourlyList)):
                hourlyList[j] = hourlyList[j] / 60
        elif avgTime > 3600:
            timeUnit = '(h)'
            for j in range(len(hourlyList)):
                hourlyList[j] = hourlyList[j] / 3600
        else:
            timeUnit = '(s)'
        fig = plt.figure(figsize = (8, 3.8))
        plt.xticks(hours)
        plt.bar(hours, hourlyList, color ='blue')
        if(today):
            plt.xlabel(formattedDate)
            plt.title("Usage Statistics(TODAY)")
        else:
            plt.xlabel('Hour')
            plt.title("Usage Statistics")
        plt.ylabel(f"Time spent {timeUnit}")
    elif type == 'daily':
        dailyList = []
        dailyList = get_daily_datalist(data,theMonth)
        days = []
        for b in range(31):
            days.append(b+1)
        usedDays = 0
        for i in dailyList:
            if i > 0:
                usedDays += 1
        print(dailyList)
        avgTime = sum(dailyList)/usedDays
        print(avgTime,'dailylaly')
        if avgTime > 60:
            timeUnit = '(m)'
            for j in range(len(dailyList)):
                dailyList[j] = dailyList[j] / 60            
        elif avgTime > 3600:
            timeUnit = '(h)'
            for j in range(len(dailyList)):
                dailyList[j] = dailyList[j] / 3600
        else:
            timeUnit = '(s)'
        fig = plt.figure(figsize = (8, 3.8))
        print('graph data')
        print(len(days))
        print(len(dailyList))
        plt.xticks(days)
        plt.bar(days, dailyList, color ='blue')
        plt.xlabel("Day")
        plt.ylabel(f"Time spent {timeUnit}")
        plt.title("Usage Statistics")

        

    #placing the graph into tkinter
    canvas = FigureCanvasTkAgg(fig,master = appWindow)  
    canvas.draw()
    canvas.get_tk_widget().grid(row=7,column=1,pady=10)
    #toolbarFrame = Frame(appWindow)
    #toolbarFrame.grid(row=8,column=1,pady=0)
    #toolbar = NavigationToolbar2Tk(canvas,toolbarFrame)
    #toolbar.update()
    canvas.get_tk_widget().grid(row=7,column=1,pady=10)
    canvas.get_tk_widget().update()

def get_time_spent_between_times(time):
    if time == [] or time == None or time == 'empty':
        return 0
    hourSpent = int(time[1][0]) - int(time[0][0])
    minuteSpent = int(time[1][1]) - int(time[0][1])
    secondSpent = int(time[1][2]) - int(time[0][2])

    if minuteSpent < 0:
        hourSpent -= 1
        minuteSpent = 60 + minuteSpent

    if secondSpent < 0:
        minuteSpent -= 1
        secondSpent = 60 + secondSpent

    actualTimeSpent = hourSpent*3600 + minuteSpent*60 + secondSpent
    return actualTimeSpent

def get_time_spent_between_daily(time):
    if time == [] or time == None or time == 'empty':
        return 0
    time = time.split()

    startTimeStamp = time[0].split(':')
    endTimeStamp = time[1].split(':')
    theTime = [startTimeStamp,endTimeStamp]

    hourSpent = int(theTime[1][0]) - int(theTime[0][0])
    minuteSpent = int(theTime[1][1]) - int(theTime[0][1])
    secondSpent = int(theTime[1][2]) - int(theTime[0][2])

    if minuteSpent < 0:
        hourSpent -= 1
        minuteSpent = 60 + minuteSpent

    if secondSpent < 0:
        minuteSpent -= 1
        secondSpent = 60 + secondSpent

    actualTimeSpent = hourSpent*3600 + minuteSpent*60 + secondSpent
    return actualTimeSpent


def get_hourly_datalist(data,reqDay,reqMonth):
    print("REQUIRED DAY:",reqDay)
    print("REQUIRED MONTH:",reqMonth)
    print(data,'normal one')
    hourList = []
    for m in range(24):
        hourList.append(0)
    for day in data:
        if str(reqDay) in day and str(reqMonth) in day:
            for time in data[day]:
                actualTimeSpent = get_time_spent_between_daily(time)
                print(actualTimeSpent,"excuse me")
                #dayNo = int(day.split()[0])
                hourNo = int(time.split()[0].split(':')[0])
                hourList[hourNo] = hourList[hourNo] + actualTimeSpent

    # for i in range(24):
    #     for time in data:
    #         if int(time[0][0]) == i:
    #             actualTimeSpent = get_time_spent_between_times(time)
    #             print(actualTimeSpent)
    #             hourList[i] += actualTimeSpent
    return hourList

def get_daily_datalist(data,month):
    print(data,'what')
    dayList = []
    for m in range(31):
        dayList.append(0)

    for day in data:
        if month in day:
            for time in data[day]:
                actualTimeSpent = get_time_spent_between_daily(time)
                print(actualTimeSpent)
                dayNo = int(day.split()[0])
                dayList[dayNo-1] = dayList[dayNo-1] + actualTimeSpent
    return dayList


def set_program_status(state,app):
    #print(allAppsEXES[selectedIndex])
    if app != allAppsEXES[selectedIndex]:
        #print('not the correct exe')
        return
    if state == 0:
        programStatusVar.set('Program Status: Not being tracked')
    elif state == 1:
        programStatusVar.set('Program Status: Not running')
    elif state == 2:
        programStatusVar.set('Program Status: RUNNING!')


def buildTrackingMenu():
    global programStatusVar,currentMenu,allAppsEXES,allAppsNames,allAppsLocations,selectedIndex
    global drpCombo,customEXEButton,DappName,DappLoc,forTracking,programStatus,graphUpdate,newFrame
    currentMenu = 'trackingMenu'
    title = tk.Label(appWindow,text='AddictFree 2.0',bg='#4FC3F7',font=('Roboto',50))
    title.grid(row=0,column=1)

    dirOfApps = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"
    #allAppsEXES = list()
    #allAppsNames = list()
    #allAppsLocations = list()

    appChosen = True

    #appsInstalled = []
    folders = os.listdir(dirOfApps)
    for folder in folders:
        if folder.endswith('.lnk'):
            directory = dirOfApps + '\\' + folder
            targetPath = getTargetOfShortcut(directory)
            fileDesc = getFileDescription(targetPath)
            if(targetPath != None and targetPath != '' and fileDesc not in [None,'unknown','']):
                exeFile = getProcName(targetPath)
                if exeFile not in allAppsEXES and fileDesc not in allAppsNames:
                    allAppsEXES.append(exeFile)
                    allAppsLocations.append(targetPath)
                    allAppsNames.append(fileDesc)
        elif os.path.isdir(dirOfApps+'\\'+folder):
            mainDirectory = dirOfApps+ '\\' + folder
            files = os.listdir(mainDirectory)
            for file in files:
                if file.endswith('.lnk'):
                    directory = mainDirectory + '\\' + file
                    targetPath = getTargetOfShortcut(directory)
                    fileDesc = getFileDescription(targetPath)
                    if(targetPath != None and targetPath != '' and fileDesc not in [None,'unknown','']):
                        exeFile = getProcName(targetPath)
                        if exeFile not in allAppsEXES and fileDesc not in allAppsNames:
                            allAppsEXES.append(exeFile)
                            allAppsLocations.append(targetPath)
                            allAppsNames.append(fileDesc)


    #print(len(allAppsEXES),len(allAppsLocations),len(allAppsNames)) 

    def check_if_file_exists(file):
        if os.path.exists(file):
            return True
        else:
            return False

    def track_state_changed():
        if trackState.get() == 0:
            disabledTracking()
        elif trackState.get() == 1:
            trackInfoMSG = tk.messagebox.showinfo('NOTE','Please note that usage stats and blocking features will be available only when atleast 1 min of usage has been recorded for you application.')
            enabledTracking()

    def update_app_selected():
        global selectedIndex,appChosen
        #print(programProcesses,programLocations)
        try:
            selectedIndex = allAppsNames.index(selectedApp.get())
            selectedLocation.set(allAppsLocations[selectedIndex])
            app = allAppsEXES[selectedIndex]
            if app in programProcesses:
                alreadySavedUpdateTracking()
            else:
                alreadyNotSavedUpdateTracking()
            #if check_if_file_exists(app.replace('exe','csv')):
            #   showStatsGraph(app)
            appChosen = True
        except Exception:
            print(traceback.print_exc())
            appChosen = False

    def alreadySavedUpdateTracking():
        trackState.set(1)
        programStatusVar.set('Program Status: Not running')
        showStatsGraph(allAppsEXES[selectedIndex],'hourly',True)

    def alreadyNotSavedUpdateTracking():
        trackState.set(0)
        programStatusVar.set('Program Status: Not being tracked')
        removeGraph()


    def enabledTracking():
        global selectedIndex
        print(appChosen)
        if(not appChosen):
            invalidAppBox = tk.messagebox.showerror('ERROR','Invalid application selected!')
            trackState.set(0)
            return
        addProc(allAppsLocations[selectedIndex])
        programStatusVar.set('Program Status: Not running')
        #showStatsGraph(allAppsEXES[selectedIndex])
    
    def disabledTracking():
        global selectedIndex
        if(not appChosen):
            invalidAppBox = tk.messagebox.showerror('ERROR','Invalid application selected!')
            trackState.set(0)
            return
        dBox = tk.messagebox.askyesnocancel('WARNING','Do you also want to delete the app\'s usage statistics?')
        if dBox == True:
            removeProc(allAppsEXES[selectedIndex],True)
        elif dBox == False:
            removeProc(allAppsEXES[selectedIndex],False)
        elif dBox == None:
            trackState.set(1)
            #forTracking.config(variable=)
            return
        programStatusVar.set('Program Status: Not being tracked')
        #showStatsGraph(allAppsEXES[selectedIndex])
        removeGraph()




    selectedApp = StringVar()
    selectedApp.set(allAppsNames[0])

    selectedIndex = 0


    selectedLocation = StringVar()
    selectedLocation.set(allAppsLocations[selectedIndex])

    selectedApp.trace('w', lambda name, index, mode, selectedApp=selectedApp: update_app_selected())

    programStatusVar = StringVar()
    programStatusVar.set('Program Staus: Not being tracked')

    trackState = IntVar()


    if allAppsEXES[selectedIndex] in programProcesses:
        alreadySavedUpdateTracking()
    else:
        alreadyNotSavedUpdateTracking()


    def showDown():
        print("hehkahlajsl")
        drpCombo.event_generate('<Down>')


    

    #dropdown = tk.OptionMenu(mainFrame, selectedApp, *allAppsNames)
    #dropdown.grid(row=1,column=1,pady=25)

    newFrame = Frame(appWindow,bg='#212121')
    newFrame.grid(row=1,column=1,pady=20)

    drpCombo = ttk.Combobox(newFrame,value=allAppsNames,textvariable=selectedApp,font=('Roboto','15'))
    drpCombo.current(0)
    drpCombo.bind('k',showDown)
    drpCombo.bind('<KeyRelease>', search_by_input)
    drpCombo.grid(row=1,column=1,pady=25)

    customEXEButton = Button(newFrame,text='Select App Manually',font=('Roboto','10','bold'),bg='#FFC107',command=selectFile)
    customEXEButton.grid(row=1,column=2)

    DappName = Label(newFrame,textvariable=selectedApp,fg='#76FF03',font=('Roboto','12','bold'),bg = '#212121')
    DappName.grid(row=2,column=1)

    DappLoc = Label(newFrame,textvariable=selectedLocation,fg='#76FF03',font=('Roboto','12','bold'),bg = '#212121')
    DappLoc.grid(row=3,column=1)

    forTracking = Checkbutton(newFrame,text="Enable tracking",command=track_state_changed,variable=trackState,bg = '#212121',fg='#FFC107',font=('Roboto',15))
    forTracking.grid(row=4,column=1)


    programStatus = Label(newFrame,textvariable=programStatusVar,fg='#00B0FF',font=('Roboto','15','bold'),bg = '#212121')
    programStatus.grid(row=5,column=1)

    graphUpdate = Button(newFrame,text='Update Graph',command=lambda: updateGraph(allAppsEXES[selectedIndex]),font=('Roboto','10','bold'),bg = '#FFC107')
    graphUpdate.grid(row=6,column=1)


def delTrackingMenu():
    removeGraph()
    title.destroy()
    drpCombo.destroy()
    customEXEButton.destroy()
    DappName.destroy()
    DappLoc.destroy()
    graphUpdate.destroy()
    forTracking.destroy()
    programStatus.destroy()
    newFrame.destroy()
    

def backButton():
    if currentMenu == 'trackingMenu':
        delTrackingMenu()
        buildMenu()
    elif currentMenu == 'usageMenu':
        delUsageMenu()
        buildMenu()
    elif currentMenu == 'blockingMenu':
        delAppBlockingMenu()
        buildMenu()

def search_exe(filepath,filename):
    l = list()

    for file in os.listdir(filepath):
        
        if file.endswith('.exe'):
            l.append(file)


    return l


def buildAppBlockingMenu():
    global title,newFrame,drpBCombo,currentMenu,notifyPriorLabel,notifyPrior
    global applyButton,timeLimitLabel,timeLimit,forceQuitLabel,forceQuit
    global blockUserInputAlsoLabel,blockUserInputAlso
    currentMenu = 'blockingMenu'

    title = tk.Label(appWindow,text='AddictFree 2.0',bg='#4FC3F7',font=('Roboto',50))
    title.grid(row=0,column=1)

    newFrame = Frame(appWindow,bg='#212121')
    newFrame.grid(row=1,column=1,pady=20)

    def update_what_selected():
        for program in listOfBlockApps:
            if selectedAppB.get() in program:
                timeLimit.delete("1.0",'end-1c')
                notifyPrior.delete("1.0",'end-1c')
                blockUserInputAlso.delete("1.0",'end-1c')

                timeLimit.insert("1.0",str(program[1]))
                notifyPrior.insert("1.0",str(program[2]))
                blockUserInputAlso.insert("1.0",str(program[3]))
                fQBool.set(int(program[4]))

    def convertToFloat(var):
        return float(var)

    def convertToInt(var):
        return int(var)

    def invalidInputMsgBox():
        msgBoxGUI = tk.messagebox.showerror('ERROR','Please check your input, must be integer or float!')

    def Apply_Block_Changes():
        timeLimitVar = timeLimit.get("1.0",'end-1c')
        notifyPriorVar = notifyPrior.get("1.0",'end-1c')
        blockUserInputAlsoVar = blockUserInputAlso.get("1.0",'end-1c')
        fQBoolVar = bool(fQBool.get())

        try:
            timeLimitVar = convertToInt(timeLimitVar)
        except:
            try:
                timeLimitVar = convertToFloat(timeLimitVar)
            except:
                invalidInputMsgBox()
                return

        try:
            notifyPriorVar = convertToInt(notifyPriorVar)
        except:
            try:
                notifyPriorVar = convertToFloat(notifyPriorVar)
            except:
                invalidInputMsgBox()
                return

        try:
            blockUserInputAlsoVar = convertToInt(blockUserInputAlsoVar)
        except:
            try:
                blockUserInputAlsoVar = convertToFloat(blockUserInputAlsoVar)
            except:
                invalidInputMsgBox()
                return

        changesAppliedBox = tk.messagebox.showinfo("INFO","Changes have been saved successfully!")

        dataToAdd = [selectedAppB.get(),timeLimitVar,notifyPriorVar,blockUserInputAlsoVar,fQBoolVar]
        theIndex = 0
        for program in listOfBlockApps:
            if selectedAppB.get() in program:
                listOfBlockApps[theIndex] = dataToAdd
                break
            else:
                theIndex += 1
        else:
            listOfBlockApps.append(dataToAdd)

        

        f = open('blockApps.bin','wb')

        pickle.dump(listOfBlockApps,f)

        f.close()

    listOfRecordedApps = list()
    for i in programProcesses:
        file = i.replace('exe','csv')
        if os.path.exists(file):
            data = []
            f = open(file,'r')
            rr = csv.reader(f)
            for k in rr:
                data.append(k)

            if data != None and data != []:
                listOfRecordedApps.append(i)
            
    if(len(listOfRecordedApps) == 0):
        noAppsRecMSG = tk.messagebox.showerror('ERROR','No apps are being tracked. Cannot use block feature without enabling tracking first.')
        backButton()
        return        

    fQBool = IntVar()
    #timeLimitVar = StringVar()
    #notifyPriorVar = StringVar()
    #blockUserInputAlsoVar = StringVar()


    selectedAppB = StringVar()
    selectedAppB.set(listOfRecordedApps[0])
    selectedAppB.trace('w', lambda name, index, mode, selectedAppB=selectedAppB: update_what_selected())


    
    drpBCombo = ttk.Combobox(newFrame,value=listOfRecordedApps,textvariable=selectedAppB,font=('Roboto','25'))

    #drpBCombo.current(0)
    #drpUCombo.bind('<KeyRelease>', search_by_input)
    drpBCombo.grid(row=1,column=1,pady=25)

    timeLimitLabel = Label(newFrame,text='Time Limit(in hr): ',font=('Roboto',20),bg='#212121',fg='#FFC107')
    timeLimit = Text(newFrame,height=1,width=10,font=('Roboto',20))

    forceQuitLabel = Label(newFrame,text='Force Quit(to terminate program automatically): ',font=('Roboto',20),bg='#212121',fg='#FFC107')
    forceQuit = Checkbutton(newFrame,variable=fQBool,bg='#212121')

    notifyPriorLabel = Label(newFrame,text='Notify prior(in mins): ',font=('Roboto',20),bg='#212121',fg='#FFC107')
    notifyPrior = Text(newFrame,height=1,width=10,font=('Roboto',20))

    blockUserInputAlsoLabel = Label(newFrame,text='Also Block User Input for(in mins): ',font=('Roboto',20),bg='#212121',fg='#FFC107')
    blockUserInputAlso = Text(newFrame,height=1,width=10,font=('Roboto',20))

    applyButton = Button(newFrame,text='Apply',bg='#8BC34A',font=('Roboto',20,'bold'),command=Apply_Block_Changes)

    timeLimitLabel.grid(row=2,column=0,pady=25)
    timeLimit.grid(row=2,column=1)
    forceQuitLabel.grid(row=3,column=0,pady=25)
    forceQuit.grid(row=3,column=1)
    notifyPriorLabel.grid(row=4,column=0,pady=25)
    notifyPrior.grid(row=4,column=1)
    blockUserInputAlsoLabel.grid(row=5,column=0,pady=25)
    blockUserInputAlso.grid(row=5,column=1)

    applyButton.grid(row=6,column=1)

    update_what_selected()


def delAppBlockingMenu():
    try:
        title.destroy()
        newFrame.destroy()
        drpBCombo.destroy()
        title.destroy()
        notifyPrior.destroy()
        notifyPriorLabel.destroy()
        blockUserInputAlsoLabel.destroy()
        blockUserInputAlso.destroy()
        applyButton.destroy()
        forceQuit.destroy()
        forceQuitLabel.destroy()
        timeLimitLabel.destroy()
        timeLimit.destroy()
    except:
        print("lol")


appWindow = tk.Tk(className='AddictFree 2.0')

appWindow.geometry('1280x720')
#appWindow.grid_columnconfigure(1,minsize=500)
appWindow.grid_anchor('n')
appWindow.configure(bg='#212121')
appWindow.protocol("WM_DELETE_WINDOW", quit_button)


backButtonGUI = Button(appWindow,text='BACK',bg='#FFC107',font=('Roboto','15','bold'),command=backButton)
backButtonGUI.grid(row=0,column=0)

buildMenu()

appWindow.mainloop()


'''
while True:
    print("""Choose options:
    1.Add Program to Track
    2.Remove Program to Track
    3.Exit""")
    try:
        ch = int(input("Enter choice: "))
        if ch == 1:
            selectFile()
        elif ch == 2:
            if(len(programProcesses) == 0):
                print("You do not have anything being tracked!")
            else:
                list_addedprocesses()
                try:
                    ch = int(input("Select program: "))
                    ch2 = input("Do you also want to remove its database?(Y/N): ")
                    if(ch2.lower() == 'y'):
                        removeProc(ch-1,True)
                    elif(ch2.lower() == 'n'):
                        removeProc(ch-1,False)
                    else:
                        print("Bad input!")
                except:
                    print("Incorrect input. Try again.")
        elif ch == 3:
            break
        else:
            print("Incorrect choice! Try again.")
    except:
        print("Something went wrong..Try again!")



'''




