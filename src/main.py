import datetime
import pylandax
from datetime import date
from datetime import timedelta
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
    #Getting all data from landax by using pylandax and return in list
    def fetch(self):
        taskListLandax = self.client.get_data('Tasks')

        return taskListLandax

    #Calculating the list for posting
    def calculate(self, taskList,startDate, daysSkip, daysRepeat):

        #The list for daily tasks
        dailyTaskListCopy = []

        # The list for weekly tasks
        weeklyTaskListCopy = []

        # The list for monthly tasks
        monthlyTaskListCopy = []

        #Checking tagtypes in task and distributing into the right list
        for task in taskList:
            #Getting the tagtypes from the task, datatype is string with IDs like '35, 22'
            checkTagTypeId = task['TagTypeIds']

            #Checking if task has tagtype and split if so
            if checkTagTypeId is not None and checkTagTypeId != '':
                tagTypesList = checkTagTypeId.split(',')

                #Converting the tagtypes in list to int
                for tagTypes in range(0, len(tagTypesList)):
                    tagTypesList[tagTypes] = int(tagTypesList[tagTypes])

                #If task has maloppgave and repeat daily, add to dailyTaskListCopy
                if maloppgave in tagTypesList and repeterdaglig in tagTypesList:
                    dailyTaskListCopy.append(task)

                if maloppgave in tagTypesList and repeterukentlig in tagTypesList:
                    weeklyTaskListCopy.append(task)

                elif maloppgave in tagTypesList and repetermanedlig in tagTypesList:
                    monthlyTaskListCopy.append(task)

        #The complete tasklist with all the copied tasks
        taskListComplete = []

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
                taskListComplete.append(newDict)

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
            taskListComplete.append(newDict)

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

            if runningDate.day <= taskDateFormated.day < intervalDate.day:
                print("Innenfor uken")

                newMonth = int(taskDateSplit[1]) + 1

                newDate = taskDateSplit[0] + "-" + str(newMonth) + "-" + taskDateSplit[2]

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

                # Adding the dict task in the taskListComplete
                taskListComplete.append(newDict)

        return taskListComplete

    #Dryrun to test what the integration is posting
    def dry_run(self, completeTaskList):

        counter = 0
        # Test printer hele tasklist complete
        for task in completeTaskList:
            print(task)
            counter = counter+1

        print('Oppgaver opprettet',counter)

    #posting all the copied tasks
    def apply(self, completeTaskList):

        counter = 0

        # Test printer hele tasklist complete
        for task in completeTaskList:
            client.post_data('Tasks',task)
            print(task)
            counter = counter + 1

        print('Oppgaver opprettet', counter)

    def main(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Combined path of filepath and config
        combinedPath = os.path.join(dir_path, "config.json")

        # Config info for API kobling LX
        config = json.loads(open(combinedPath).read())

        # Configuering client from Landax and config file
        self.client = pylandax.Client(config)

        # Kjøringsdato Format startDate = date(2022, 6, 20)
        startDate = date(2022, 9, 18)
        #startDate = date.today()
        daysSkip = 0
        daysRepeat = 7

        taskListLandax = self.fetch()
        taskListComplete = self.calculate(taskListLandax, startDate, daysSkip, daysRepeat)
        self.dry_run(taskListComplete)

if __name__ == '__main__':
    client = norwaysBestClient()
    client.main()



