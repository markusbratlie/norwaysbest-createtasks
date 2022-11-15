import datetime
import pylandax
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import json
import os
from pathlib import Path

#Tagtypes from Landax ('TagTypeIds')
maloppgave = 34
kanslettes = 37
repeterdaglig = 35
repeterukentlig = 36
repetermanedlig = 69

class norwaysBestClient:
    def __init__(self, dry_run):
        self.dry_run = dry_run

    #Getting all data from landax by using pylandax and return in list
    def fetch(self):
        taskListLandax = self.client.get_data('Tasks')

        return taskListLandax


    def fetchSingleTask(self):
        singleTask1 = self.client.get_single_data('Tasks',231574)
        singleTask2 = self.client.get_single_data('Tasks', 231572)
        print(singleTask1)
        print(singleTask2)

    #Taking all the data from fetch and distributing them into different lists for calculation.
    def distribute(self, taskList):

        # The list for daily tasks
        dailyTaskListCopy = []

        # The list for weekly tasks
        weeklyTaskListCopy = []

        # The list for monthly tasks
        monthlyTaskListCopy = []

        # The list for monthly tasks
        mayBeDeleteTaskList = []

        # Checking tagtypes in task and distributing into the right list
        for task in taskList:
            # Getting the tagtypes from the task, datatype is string with IDs like '35, 22'
            checkTagTypeId = task['TagTypeIds']

            # Checking if task has tagtype and split if so
            if checkTagTypeId is not None and checkTagTypeId != '':
                tagTypesList = checkTagTypeId.split(',')

                # Converting the tagtypes in list to int
                for tagTypes in range(0, len(tagTypesList)):
                    tagTypesList[tagTypes] = int(tagTypesList[tagTypes])

                # If task has maloppgave and repeat daily, add to dailyTaskListCopy
                if maloppgave in tagTypesList and repeterdaglig in tagTypesList:
                    dailyTaskListCopy.append(task)

                # if task is maloppgage and repeat weekly, add to weeklylist
                if maloppgave in tagTypesList and repeterukentlig in tagTypesList:
                    weeklyTaskListCopy.append(task)

                # if task is maloppgage and repeat monthly, add to monthlylist
                if maloppgave in tagTypesList and repetermanedlig in tagTypesList:
                    monthlyTaskListCopy.append(task)
                # if task is kan slettes add to mayBeDeleted
                elif kanslettes in tagTypesList:
                    mayBeDeleteTaskList.append(task)

        # Printing and showing wich tasks that will be calculated
        print("Daily tasks that will be copied")
        for task in dailyTaskListCopy:
            print("Dato ", task.get("PlannedStartDate"), " ----------- Beskrivelse ", task.get("Description"))


        dailyTaskListCopyNumber = len(dailyTaskListCopy)
        print("")
        print('Number of daily tasks that will be copied', dailyTaskListCopyNumber)

        print("")
        print("Weekly tasks that will be copied")
        for task in weeklyTaskListCopy:
            print("Dato ", task.get("PlannedStartDate"), " ----------- Beskrivelse ", task.get("Description"))

        weeklyTaskListCopyNumber = len(weeklyTaskListCopy)
        print("")
        print('Number of weekly tasks that will be copied', weeklyTaskListCopyNumber)

        print("")
        print("Monthly tasks that may be copied")
        for task in monthlyTaskListCopy:
            print("Dato ", task.get("PlannedStartDate"), " ----------- Beskrivelse ", task.get("Description"))

        monthlyTaskListCopyNumber = len(monthlyTaskListCopy)
        print(" ")
        print('Number of monthly tasks that may be copied', monthlyTaskListCopyNumber)

        print("")
        print("Tasks that may be deleted - Tasks with kan slettes tag")
        #for task in mayBeDeleteTaskList:
            #print("Dato ", task.get("PlannedStartDate"), " ----------- Beskrivelse ", task.get("Description"), "------Related incicidents ", task.get("RelatedIncidents"), "------Related surveys ", task.get("SurveyResults"))

        mayBeDeleteTaskListNumber = len(mayBeDeleteTaskList)
        print("")
        print('Number of tasks that may be deleted', mayBeDeleteTaskListNumber)

        return [dailyTaskListCopy, weeklyTaskListCopy, monthlyTaskListCopy, mayBeDeleteTaskList]


    # Calculating list of tasks that will be deleted and returning a list ready to be deleted
    def calculateDelete(self, taskList, startDate):

        deleteTaskList = []
        doNotDeleteList = []

        # Checking tagtypes in task and distributing into the right list
        for task in taskList:
            # Getting the tagtypes from the task, datatype is string with IDs like '35, 22'
            checkTagTypeId = task['TagTypeIds']
            checkTaskDate = task['PlannedStartDate']
            checkSurvey = task.get('SurveyResults')
            checkIncident = task.get('RelatedIncidents')

            # The string from Landax format '2022-05-13T10:15:00Z', we split it on date and time
            datotid = checkTaskDate.split('T')
            # Spltting the date and make it into datetime format
            taskDateSplit = datotid[0].split('-')
            taskDateFormated = datetime.date(int(taskDateSplit[0]), int(taskDateSplit[1]), int(taskDateSplit[2]))
            startDeleteDate = startDate - timedelta(days=14)

            # Checking if task has tagtype and split if so
            if checkTagTypeId is not None and checkTagTypeId != '':
                tagTypesList = checkTagTypeId.split(',')

                # Converting the tagtypes in list to int
                for tagTypes in range(0, len(tagTypesList)):
                    tagTypesList[tagTypes] = int(tagTypesList[tagTypes])

                # Checking if task has tagtype "kanslettes" and if the taskdate is smaller then today and there is no surveys or incidents on task
                if kanslettes in tagTypesList and startDeleteDate > taskDateFormated and len(checkSurvey) == 0 and len(
                        checkIncident) == 0:
                    deleteTaskList.append(task)

        return deleteTaskList


    #Calculating the list for posting
    def calculate(self, taskList, startDate, daysSkip, daysRepeat):

        #Defining the tasklist from fetch
        taskListLandax = taskList

        #Running functio distribute
        taskDistribute = self.distribute(taskListLandax)


        # The list for daily tasks
        dailyTaskListCopy = taskDistribute[0]

        # The list for weekly tasks
        weeklyTaskListCopy = taskDistribute[1]

        # The list for monthly tasks
        monthlyTaskListCopy = taskDistribute[2]

        mayBeDeleted = taskDistribute[3]


        #The complete tasklist with all the copied tasks
        taskListComplete = []

        # The complete tasklist with all the copied daily tasks
        taskListCompleteDaily = []

        # The complete tasklist with all the copied daily tasks
        taskListCompleteWeekly = []

        # The complete tasklist with all the copied daily tasks
        taskListCompleteMonthly = []





        #All tasks will be copied from dailyTaskListCopy
        for task in dailyTaskListCopy:

            #Mapping to new copied dict
            description = task['Description']
            typeId = task['TypeId']
            categoryId = task['CategoryId']
            avdelingId = task['DepartmentId']
            projectId = task['MainProjectId']
            ansvarligRolle = task['ResponsibleFunctionId']
            utforesRolle = task['HandledByFunctionId']
            heldagsoppgave = task['IsAlldayTask']
            notat = task['Notes']
            addonMerkelapper = kanslettes

            #Getting the date from the task
            plannedStartDato = task['PlannedStartDate']

            #The string from Landax format '2022-05-13T10:15:00Z', we split it on date and time
            datotid = plannedStartDato.split('T')

            #Making daysRepeate tasks with daysSkip from todays date as start date
            for x in range(daysRepeat):

                i = x+daysSkip

                #Adding a date for every loop and formating date and time to string
                newDate = startDate + timedelta(days=i)
                newDateStr = str(newDate)
                klokkeslett = datotid[1]

                #Combining new date and time
                newPlannedStartDato = newDateStr + 'T' + klokkeslett

                #New task as dictonary with only neccesery information
                newDict = {'Description': description,
                           'TypeId': typeId,
                           'CategoryId': categoryId,
                           'DepartmentId': avdelingId,
                           'MainProjectId': projectId,
                           'ResponsibleFunction': ansvarligRolle,
                           'HandledByFunction': utforesRolle,
                           'TagTypeIds': str(addonMerkelapper),
                           'IsAlldayTask': heldagsoppgave,
                           'Notes': notat,

                           'PlannedStartDate': newPlannedStartDato,
                           'PlannedDoneDate': newPlannedStartDato,

                           }
                # Adding the new task to taskListComplete
                taskListCompleteDaily.append(newDict)

        #Copying all tasks from weeklyTaskList
        for task in weeklyTaskListCopy:

            #Mapping to new dictonary task
            description = task['Description']
            typeId = task['TypeId']
            categoryId = task['CategoryId']
            avdelingId = task['DepartmentId']
            projectId = task['MainProjectId']
            ansvarligRolle = task['ResponsibleFunctionId']
            utforesRolle = task['HandledByFunctionId']
            heldagsoppgave = task['IsAlldayTask']
            addonMerkelapper = kanslettes
            notat = task['Notes']

            #Getting plannedStartDato
            plannedStartDato = task['PlannedStartDate']

            #The string from Landax format '2022-05-13T10:15:00Z', we split it on date and time
            datotid = plannedStartDato.split('T')
            #Spltting the date and make it into datetime format
            taskDateSplit = datotid[0].split('-')
            taskDateFormated = datetime.datetime(int(taskDateSplit[0]),int(taskDateSplit[1]),int(taskDateSplit[2]))

            #Tasks weekday
            weekDayCheck = taskDateFormated.isoweekday()

            runDateDay = startDate + timedelta(days=daysSkip)

            #TodaysDate as weekdat 0-6, 0 is monday, 6 er sunday
            todayWeekDayCheck = runDateDay.isoweekday()

            #Whileloop loops until it finds first weekday that matches the tasks weekday after startDate

            #Check if weekdays match and make a new date
            i = daysSkip
            dayMatched = False

            while not dayMatched:

                if weekDayCheck == todayWeekDayCheck:
                    newDate = startDate + timedelta(days=i)
                    dayMatched = True

                i=i+1

                if todayWeekDayCheck < daysRepeat:
                    todayWeekDayCheck = todayWeekDayCheck+1
                else:
                    todayWeekDayCheck = 0

            newDateStr = str(newDate)
            klokkeslett = datotid[1]

            #Combining ny date with time
            newPlannedStartDato = newDateStr + 'T' + klokkeslett

            #Adding everything in a new dict as task
            newDict = {'Description': description,
                       'TypeId': typeId,
                       'CategoryId': categoryId,
                       'DepartmentId': avdelingId,
                       'MainProjectId': projectId,
                       'ResponsibleFunction': ansvarligRolle,
                       'HandledByFunction': utforesRolle,
                       'TagTypeIds': str(addonMerkelapper),
                       'IsAlldayTask': heldagsoppgave,
                       'Notes': notat,

                       'PlannedStartDate': newPlannedStartDato,
                       'PlannedDoneDate': newPlannedStartDato,

                       }


            #Adding the dict task in the taskListComplete
            taskListCompleteWeekly.append(newDict)

        #Copying all tasks from monthly
        for task in monthlyTaskListCopy:

            # Mapping to new dictonary task
            description = task['Description']
            typeId = task['TypeId']
            categoryId = task['CategoryId']
            avdelingId = task['DepartmentId']
            projectId = task['MainProjectId']
            ansvarligRolle = task['ResponsibleFunctionId']
            utforesRolle = task['HandledByFunctionId']
            heldagsoppgave = task['IsAlldayTask']
            addonMerkelapper = kanslettes
            notat = task['Notes']

            # Getting plannedStartDato
            plannedStartDato = task['PlannedStartDate']

            # The string from Landax format '2022-05-13T10:15:00Z', we split it on date and time
            datotid = plannedStartDato.split('T')
            # Spltting the date and make it into datetime format
            taskDateSplit = datotid[0].split('-')
            taskDateFormated = datetime.date(int(taskDateSplit[0]), int(taskDateSplit[1]), int(taskDateSplit[2]))

            runningDate = startDate + timedelta(days=daysSkip)
            intervalDate = startDate + timedelta(days=daysSkip) + timedelta(days=daysRepeat)

            #print(runningDate.year)
            #print(runningDate.month)
            #print(taskDateFormated.day)

            if taskDateFormated.day < 28:
                taskDatePushed = date(runningDate.year, runningDate.month, taskDateFormated.day)
            else:
                taskDatePushed = date(runningDate.year, runningDate.month, 28)

            #print("---Check dates---")
            #print(runningDate)
            #print(taskDatePushed)
            #print(intervalDate)

            #print(" ")

            #print("-------------Check if its inside weekinterval------------")

            if runningDate <= taskDatePushed < intervalDate:
                #print("This task is inside the week")

                newDate = runningDate + relativedelta(months=1)


                newDate = str(newDate.year) + "-" + str(newDate.month) + "-" + str(taskDatePushed.day)

                klokkeslett = datotid[1]

                # Combining ny date with time
                newPlannedStartDato = newDate + 'T' + klokkeslett

                # Adding everything in a new dict as task
                newDict = {'Description': description,
                           'TypeId': typeId,
                           'CategoryId': categoryId,
                           'DepartmentId': avdelingId,
                           'MainProjectId': projectId,
                           'ResponsibleFunction': ansvarligRolle,
                           'HandledByFunction': utforesRolle,
                           'TagTypeIds': str(addonMerkelapper),
                           'IsAlldayTask': heldagsoppgave,
                           'Notes': notat,

                           'PlannedStartDate': newPlannedStartDato,
                           'PlannedDoneDate': newPlannedStartDato,

                           }

                #print('This task will be posted', newDict.get('Description'),newDict.get('PlannedStartDate'))

                # Adding the dict task in the taskListComplete
                taskListCompleteMonthly.append(newDict)

        #Calculating deleted list
        tasksToBeDeleted = self.calculateDelete(mayBeDeleted, startDate)

        print(" ")
        print("-----------------Quilitycontroll TASKS--------------------")

        dailyTaskListCopyMulti = len(dailyTaskListCopy)*7
        print('Dailytasks copy', dailyTaskListCopyMulti)
        print('Dailytasks complete', len(taskListCompleteDaily))

        tasksForApply = {"taskListCompleteDaily":taskListCompleteDaily, "taskListCompleteWeekly":taskListCompleteWeekly, "taskListCompleteMonthly":taskListCompleteMonthly, "tasksToBeDeleted":tasksToBeDeleted}

        return tasksForApply

    #Function that takes all the lists and applying or deleting them to Landax
    def apply(self, taskListCompleteDaily, taskListCompleteWeekly, taskListCompleteMonthly, tasksToBeDeleted):

        #Applying daily tasks
        print("-------------------------------------")
        print("daily tasks")

        counterDaily = 0

        for task in taskListCompleteDaily:
            if not self.dry_run:
                print("!!!!!!!!!!!POSTING TO LANDAX!!!!!!!!!!!!")
                self.client.post_data('Tasks', task)

            print(task)
            counterDaily = counterDaily+1

        print('Daily tasks created',counterDaily)

        # Applying weekly tasks

        print("-------------------------------------")
        print("Weekly tasks")

        counterWeekly = 0

        for task in taskListCompleteWeekly:
            if not self.dry_run:
                print("!!!!!!!!!!!POSTING TO LANDAX!!!!!!!!!!!!")
                self.client.post_data('Tasks', task)

            print(task)
            counterWeekly = counterWeekly + 1

        print('Weekly tasks created', counterWeekly)

        # Applying monthly tasks

        print("-------------------------------------")
        print("Monthly tasks")

        counterMonthly = 0

        for task in taskListCompleteMonthly:
            if not self.dry_run:
                print("!!!!!!!!!!!POSTING TO LANDAX!!!!!!!!!!!!")
                self.client.post_data('Tasks', task)
            print(task)
            counterMonthly = counterMonthly + 1

        print('Monthly tasks created', counterMonthly)

        # Deleting tasks
        print("-------------------------------------")
        print("Deleting tasks")

        counterDelete = 0
        actualCounterDelete = 0

        for task in tasksToBeDeleted:
            if not self.dry_run:
                #print("!!!!!!!!!!!DELETING FROM LANDAX!!!!!!!!!!!!")
                self.client.delete_data('Tasks',task.get('Id'))
                actualCounterDelete = actualCounterDelete + 1


            #print(task)

            counterDelete = counterDelete + 1

        print('Tasks that was deleted (Dryrun)', counterDelete)
        print('Tasks that actually was deleted', actualCounterDelete)


    def run(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Combined path of filepath and config
        combinedPath = os.path.join(dir_path, "config.json")

        # Config info for API kobling LX
        config = json.loads(open(combinedPath).read())

        # Configuering client from Landax and config file
        self.client = pylandax.Client(config)

        # Kjøringsdato Format startDate = date(2022, 6, 20)
        startDate = date(2022, 11, 21)
        #startDate = date.today()
        daysSkip = 0
        daysRepeat = 7

        #Running fetch function
        taskListLandax = self.fetch()

        #calculting and returning a dict with dayily, weekly, monthly and tasks to be deleted
        taskListComplete = self.calculate(taskListLandax, startDate, daysSkip, daysRepeat)

        #Using the apply function and giving the function the different lists from taskListComplete
        self.apply(taskListComplete.get("taskListCompleteDaily"),taskListComplete.get("taskListCompleteWeekly"),taskListComplete.get("taskListCompleteMonthly"),taskListComplete.get("tasksToBeDeleted"))


def main(dry_run):
        client = norwaysBestClient(dry_run)
        client.run()
