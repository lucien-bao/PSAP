import psap
from psychopy import gui, core
import datetime

setupDlg = gui.Dlg(title="Run experiment")
setupDlg.addField("Participant ID")
setupDlg.addField("Experiment script",
                  choices=("Point-Subtraction Aggression Paradigm",
                           "Balloon Analog Risk Task"))
response = setupDlg.show()

if (setupDlg.OK):
    if response[1] == "Point-Subtraction Aggression Paradigm":
        date_time = datetime.datetime.now()
        psap.main("data/" + str(response[0]) + " " + str(date_time) + ".csv")
    else:
        print("Run BART script here")
else:
    core.quit()
