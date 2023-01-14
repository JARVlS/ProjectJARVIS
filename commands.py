from typing import List
from random import choice
from platform import system
import smtplib
import os
from pynput.keyboard import Key, Controller
import time
from time import sleep
import webbrowser
from interfaces import AbstractJarvis, AbstractCommand, CommandNotFoundError
import psutil
import json
import random
import re
import wikipedia
import requests
import calendar, datetime
import playsound
from tkinter import *
from pytube import YouTube

system = system()


class Command(AbstractCommand):
    def __init__(
        self,
        jarvis: AbstractJarvis,
        responses: List[str],
        message: str = "",
        previous_message: str = "",
        previous_command="",
    ):
        super().__init__(jarvis)
        self.message = message.lower()
        self.responses = responses
        self.previous_message = previous_message
        self.previous_command = previous_command
        with open("./json_data/inandout.json", encoding="utf-8") as f:
            self.inandouts = json.load(f)
        self.data = json.load(open("./json_data/usefull_data.json", encoding="utf-8"))
        self.yes = self.data["yes"]
        self.name_of_programm = str(self.data["name_of_programm"])

    def execute(self):
        return choice(self.responses)


class AdoptionsCommand(Command):
    def execute(self, message=""):
        if message == "":
            message = self.message
        self.jarvis.talkToMe(choice(self.responses))
        while True:  # schalte in "Schlummermodus"
            message = (
                self.jarvis.getNextMessage()
            )  # warten, dass eine der folgenden Wörter eingegeben wird
            if "jarvis" in message and message not in [
                self.name_of_programm,
                "hey" + self.name_of_programm,
                "hallo" + self.name_of_programm,
            ]:
                self.jarvis.buildCommandList()
                try:
                    command = self.jarvis.retrieveCommand(message=message)
                    if str(type(command).__name__) != "Command" and " und " in message:
                        commands = message.split(" und ")
                        for i in commands:
                            try:
                                command = self.jarvis.retrieveCommand(message=i)
                            except CommandNotFoundError:
                                self.jarvis.talkToMe(
                                    "Ich kann folgendes noch nicht: " + i
                                )
                            else:
                                try:
                                    command.message = i
                                except Exception:
                                    pass
                                result = command.execute()
                                self.jarvis.talkToMe(result)
                                self.jarvis.previousinput = i
                                self.jarvis.previouscommand = command
                        continue
                except CommandNotFoundError:
                    # self.jarvis.talkToMe("Das kann ich noch nicht")
                    playsound.playsound("talk.mp3")
                    message = self.jarvis.getNextMessage().lower()
                    new_one = ["neue antwort", "neues kommando", "neue zuordnung"]
                    res = [ele for ele in new_one if (ele in message)]
                    if bool(res):  # wenn ein neues Kommando hinzugefügt werden soll
                        command = self.jarvis.addNewCommand(
                            message=self.message
                        )  # Funktion zum Hinzufügen wird aufgerufen
                    else:
                        self.jarvis.run(message=message)
                    self.jarvis.run()
                else:
                    try:
                        command.message = message
                    except Exception:
                        pass
                    result = (
                        command.execute()
                    )  # Die Antwort wird mit der execute-Funktion des jeweilig zuständigen Commands ermittelt

                    self.jarvis.talkToMe(result)  # Die Antwort wird ausgegeben
                    self.jarvis.previousinput = message
                    self.jarvis.previouscommand = command
                    self.jarvis.run()
            elif message in [
                self.name_of_programm,
                "hey" + self.name_of_programm,
                "hallo" + self.name_of_programm,
            ]:
                self.jarvis.talkToMe("Ja Sir?")
                self.jarvis.run()
                break


class EndjarvisCommand(Command):
    def execute(self):
        quit(self.jarvis.talkToMe("Auf ein anderes Mal"))



class YoutubeCommand(Command):
    def execute(self, message=""):
        if message == "":
            message = self.message
        self.target = ""  # hiernach soll gesucht werden
        self.target_string = ""  # tatsächlich für den browser verarbeitbarer string ("python+lernen+morpheus")

        def OpenYoutubeWithSearchQuery():
            self.target = self.target[
                1:
            ]  # unten (zeile 48ff) wird die suchanfrage geteilt in tatsächliche Suchanfrage und einleitung
            for i in self.target:  # für jedes wort in der suchanfrage
                self.target_string += (
                    i + "+"
                )  # suchanfrage wird in "url-format" gebracht
            if system == "Windows":
                webbrowser.get("windows-default").open(
                    "https://www.youtube.com/results?search_query=" + self.target_string
                )  # suchanfrage wird bei youtube eingegeben
            else:
                webbrowser.open(
                    "https://www.youtube.com/results?search_query=" + self.target_string
                )  # suchanfrage wird bei youtube eingegeben

        if (
            message == "youtube"
        ):  # wenn die eingabe youtube ist, wird einfach nur youtube geöffnet
            webbrowser.get("windows-default").open("https://www.youtube.com")

        elif (
            "nach" in message
        ):  # wenn nach etwas bestimmten gesucht wird, wird die funktion zu verarbeitung der suchanfrage aufgerufen
            self.target = message.split(
                "nach "
            )  # eine liste mit zwei einträgen - einmal der "einleitung" und einmal der suchanfrage - wird übergeben
            OpenYoutubeWithSearchQuery()

        elif (
            "youtube" in message
        ):  # wenn youtube nicht die eingabe ist, aber in der eingabe vorkommt, wird auch hier eine liste mit zwei einträge erzeuggt und übergeben
            self.target = message.split("youtube ")
            OpenYoutubeWithSearchQuery()
        return "Sehr gerne Sir!"  # eine antwort wird nach ausführen des commands ebenfalls noch ausgegeben


class SendwhatsappCommand(Command):  # comma # siehe youtubecommand

    def execute(self, message=""):
        if message == "":
            message = self.message
        name = ""

        def checkIfProcessRunning(processName):
            for proc in psutil.process_iter():
                try:
                    # Check if process name contains the given name string.
                    if processName.lower() in proc.name().lower():
                        return True
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    pass
            else:
                return False

        def whatsapp_coordination(name, nachricht, time=7):
            keyboard = Controller()
            if system == "Windows":
                if checkIfProcessRunning("WhatsApp"):
                    os.startfile("WhatsApp Desktop.lnk")
                    sleep(float(time / 2))
                    for i in range(2):
                        keyboard.press(Key.tab)
                        sleep(0.3)
                        keyboard.release(Key.tab)
                else:
                    os.startfile("WhatsApp Desktop.lnk")
                    sleep(float(time))
                    for i in range(2):
                        keyboard.press(Key.tab)
                        sleep(0.3)
                        keyboard.release(Key.tab)
            else:
                webbrowser.get("windows-default").open("https://web.whatsapp.com/")
                sleep(float(time))
                keyboard.press(Key.tab)
                sleep(0.3)
                keyboard.release(Key.tab)
                sleep(0.3)
            keyboard.type(name)
            sleep(0.3)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            sleep(0.5)
            keyboard.type(nachricht)
            sleep(0.5)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            self.jarvis.talkToMe("Sie sollten bald eine Antwort erhalten!")

        if " in " in message and not " an " in message:
            name = str(input("Name: "))
            nachricht = str(self.jarvis.getNextMessage("Nachricht: "))
            time = ""
            time = message.split("in")
            try:
                time = int(time[1])
            except Exception:
                time = 6
            else:
                time = 6
            webbrowser.get("windows-default").open("https://web.whatsapp.com/")
            if nachricht != "abbrechen":
                whatsapp_coordination(name, nachricht, time)
            else:
                return "Abgebrochen"
        elif " an " in message:
            name = message.split("an ")
            name = name[1]
            if " in " in message:
                time = message.split("in ")
                name = name.replace("in " + time[1], "")
                name = name.strip()
                try:
                    time = float(time[1])
                except Exception:
                    time = 5
            else:
                time = 5
            nachricht = str(self.jarvis.getNextMessage("Nachricht: "))

            if nachricht != "abbrechen":
                whatsapp_coordination(name, nachricht, time)
            else:
                return "Abgebrochen"
        elif "whatsapp" in message or "nachricht" in message:
            name = str(self.jarvis.getNextMessage("Name: "))
            nachricht = str(self.jarvis.getNextMessage("Nachricht: "))
            time = ""
            if " in " in message:
                time = message.split("in")
                try:
                    time = int(time[1])
                except Exception:
                    time = 6
            else:
                time = 6

            if nachricht != "abbrechen":
                whatsapp_coordination(name, nachricht, time)
            else:
                return "Abgebrochen"
        else:
            webbrowser.get("windows-default").open("https://web.whatsapp.com/")
        return "Nachricht an " + name + " versandt"


class PlaymusicCommand(Command):
    def execute(self, message=""):
        if message == "":
            message = self.message
        if system == "Windows":
            if os.path.exists("C:/Users/leong/AppData/Roaming/Spotify/Spotify.exe"):
                os.startfile("C:/Users/leong/AppData/Roaming/Spotify/Spotify.exe")
            else:
                self.jarvis.talkToMe(
                    "Hast Spotify leider nicht installiert (Wenn doch, dann verschiebe es bitte and folgenden Ort: C:/Users/leong/AppData/Roaming/Spotify/ -> Hier muss die Spotify.exe Datei hin)"
                )
        elif system == "Linux":
            try:
                os.system("spotify")
                # webbrowser.get("windows-default").open("https://www.spotify.com")
            except:
                self.jarvis.talkToMe("Du hast kein Spotify installiert!")
        keyboard = Controller()
        time.sleep(3)
        keyboard.press(Key.media_play_pause)
        return ""


class SendmailCommand(Command):
    def execute(self, message=""):
        if message == "":
            message = self.message
        user = "j.a.r.v.i.s@mein.gmx"
        pwd = "j4rv1514m"

        server = smtplib.SMTP("mail.gmx.net", 587)
        server.starttls()
        server.login(user, pwd)
        print("\nLogin erfolgreich\n")

        Inhalt = self.jarvis.getNextMessage("Inhalt der Mail: ")
        Betreff = self.jarvis.getNextMessage("Betreff der Mail: ")

        def sendit(Empfänger, Inhalt, Betreff, Empfänger_name):
            mail_text = Inhalt
            subject = Betreff
            MAIL_FROM = "j.a.r.v.i.s@mein.gmx"
            RCPT_TO = ""
            if Empfänger != "":
                RCPT_TO = Empfänger
            else:
                getreceiver()
            DATA = "From:%s\nTo:%s\nSubject:%s\n\n%s" % (
                MAIL_FROM,
                RCPT_TO,
                subject,
                mail_text,
            )
            server.sendmail(MAIL_FROM, RCPT_TO, DATA)
            server.quit()
            if Empfänger_name != "":
                self.jarvis.talkToMe(
                    "Die Mail wurde erfolgreich an " + Empfänger_name + " versandt"
                )
            else:
                self.jarvis.talkToMe(
                    "Die Mail wurde nicht erfolgreich an " + Empfänger + " versandt"
                )

        def getCommmonReceavers():
            with open("./json_data/usefull_data.json", encoding="utf-8") as file:
                data = json.load(file)
                return data["CommonReceavers"]

        common_receavers = getCommmonReceavers()

        def wannaAddNewContact(Empfänger_name, common_receavers):
            wanna_new_contact = self.jarvis.getNextMessage(
                "Für diesen Namen ist noch keine Email-Adresse angegeben. Willst du eine neue hinzufügen? \n>..>"
            )
            if wanna_new_contact in self.yes:
                new_contact_adress = self.jarvis.getNextMessage(
                    "Wie lautet die Mail-Adresse des Kontaktes?\n >..>"
                )
                if "@" in new_contact_adress and "." in new_contact_adress:
                    with open("./json_data/usefull_data.json", encoding="utf-8") as f:
                        data = json.load(f)
                    common_receavers[Empfänger_name] = new_contact_adress
                    data["CommonReceavers"] = common_receavers
                    with open("./json_data/usefull_data.json", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    common_receavers = getCommmonReceavers()
                    return common_receavers[Empfänger_name]
                else:
                    self.jarvis.talkToMe(
                        "That can not be a valid E-Mail Adress! Please try again."
                    )
                    wannaAddNewContact(Empfänger_name, common_receavers)
            else:
                pass

        def getreceiver():
            Empfänger = ""
            Empfänger_name = ""
            if " an " in message:
                Empfänger_name = message.split("an ")[1].lower().strip()
            else:
                Empfänger_name = self.jarvis.getNextMessage(
                    "An wen soll die Mail gesendet werden?"
                )

            for receaver in common_receavers:
                if Empfänger_name == receaver:
                    Empfänger = common_receavers[receaver]
                    print("Adress: " + Empfänger)
                    break
            else:
                print("Well here I am")
                if (
                    Empfänger_name not in common_receavers
                    and "@" not in message
                    and "." not in message
                ):
                    Empfänger = wannaAddNewContact(Empfänger_name, common_receavers)
                else:
                    Empfänger = Empfänger_name

            if "@" in Empfänger and "." in Empfänger:
                try:
                    sendit(Empfänger, Inhalt, Betreff, Empfänger_name)
                except smtplib.SMTPRecipientsRefused:
                    Empfänger = self.jarvis.getNextMessage(
                        "Entschuldigen Sie. Das hat nicht funktioniert. Wiederholen Sie die Ämpfängeradresse: "
                    )
                    try:
                        sendit(Empfänger, Inhalt, Betreff, Empfänger_name)
                    except Exception:
                        self.jarvis.talkToMe(
                            "Das hat nicht funktioniert. Versuchen Sie es zu einem späteren Zeitpunkt erneut"
                        )
                        pass
                except UnicodeEncodeError:
                    I = (
                        str(Inhalt)
                        .replace("ä", "ae")
                        .replace("ö", "oe")
                        .replace("ü", "ue")
                        .replace("ß", "ss")
                        .replace("é", "e")
                        .replace("ó", "o")
                        .replace("è", "e")
                    )
                    B = (
                        str(Betreff)
                        .replace("ä", "ae")
                        .replace("ö", "oe")
                        .replace("ü", "ue")
                        .replace("ß", "ss")
                        .replace("é", "e")
                        .replace("ó", "o")
                        .replace("è", "e")
                    )
                    try:
                        sendit(Empfänger, I, B, Empfänger_name)
                    except Exception:
                        self.jarvis.talkToMe(
                            "Das hat nicht funktioniert. Vermutlich aufgrund unerlaubter Satzzeichen. Versuchen Sie es zu einem späteren Zeitpunkt erneut"
                        )
                        pass

        getreceiver()
        return ""


class ChangevolumeCommand(Command):
    def execute(self, message=""):
        if message == "":
            message = self.message
        keyboard = Controller()

        def lauter(um_so_viel=5):
            for i in range(int(um_so_viel)):
                keyboard.press(Key.media_volume_up)
                time.sleep(0.01)

        def leiser(um_so_viel=5):
            for i in range(int(um_so_viel)):
                keyboard.press(Key.media_volume_down)
                time.sleep(0.1)

        if "um " in message.lower() and ("leiser" in message or "lauter" in message):
            um_so_viel = message.split("um")[1].strip()
            um_so_viel = um_so_viel.replace("%", "")
            try:
                um_so_viel = int(um_so_viel)
            except Exception:
                try:
                    um_so_viel = um_so_viel.split("lauter")[0].strip()
                    um_so_viel = int(um_so_viel)
                except Exception:
                    try:
                        um_so_viel = um_so_viel.split("leiser")[0].strip()
                        um_so_viel = int(um_so_viel)
                    except Exception:
                        um_so_viel = 10

            if "lauter" in message.lower():
                lauter(um_so_viel / 2)
            elif "leiser" in message.lower():
                leiser(um_so_viel / 2)

        elif "lauter" in message.lower():
            lauter()
        elif "leiser" in message.lower():
            leiser()
        return ""


class MediapauseplayCommand(Command):
    def execute(self, message=""):
        if message == "":
            message = message
        keyboard = Controller()
        keyboard.press(Key.media_play_pause)
        return ""


class MedianextCommand(Command):
    def execute(self, message=""):
        if message == "":
            message = self.message
        keyboard = Controller()
        if "anderes" or "anderer" in message.lower():
            for i in range(random.randint(1, 10)):
                keyboard.press(Key.media_next)
        else:
            keyboard.press(Key.media_next)
        return ""


class MediapreviousCommand(Command):
    def execute(self, message=""):
        if message == "":
            message = self.message
        keyboard = Controller()
        keyboard.press(Key.media_previous)
        return ""


class WeiterCommand(Command):
    def execute(self, message=""):
        if message == "":
            message = self.message
        keyboard = Controller()
        if "weiter" not in self.previous_message:  # hier weitermachen
            keyboard.press(Key.media_next)


class GoogleCommand(Command):
    def execute(self):
        message = self.message.lower()
        if_list_1 = ["nach", "google", "suche", "googel"]
        for i in if_list_1:
            if i in message:
                message = message.split(i)[1].strip()
                # ---- hier müsste ein Wörterbuch eingebunden werden ----
                # if " nach " in self.message and message[-1] == "n":
                #     message_list = list(message)
                #     message_list[-1] = ""
                #     message = "".join(message_list)
                break
        target = message.replace(" ", "+")
        if system == "Windows":
            webbrowser.get("windows-default").open(
                "https://duckduckgo.com/?q=" + target
            )
        else:
            webbrowser.open("https://duckduckgo.com/?q=" + target)

        return ""


class OpenCommand(Command):
    def execute(self):
        message = self.message.lower()
        message = self.message.lower().strip()
        path = ""
        with open("./json_data/usefull_data.json", encoding="utf-8") as f:
            data = json.load(f)
        programm_names = []
        for name in data[
            "open"
        ].keys():  # namen der programme in liste laden, um nachher den entsprechenden Pfad herauszufiltern
            programm_names.append(name)

        for name in programm_names:
            if name in message:
                path = data["open"][name]
                break
        else:
            self.jarvis.talkToMe(
                "Dieses Programm oder diese Website ist noch nicht in meiner Datenbank"
            )
            wanna_new_one = self.jarvis.getNextMessage(
                "Möchtest du ein neues Programm hinzufügen? "
            )
            if wanna_new_one in self.yes:
                programm_name = self.jarvis.getNextMessage("Programmname: ")
                self.jarvis.talkToMe("Bitte tippe den Pfad ein")
                programm_path = (
                    input("->")
                    .lower()
                    .replace("\\", "/")
                    .replace("\\\\", "/")
                    .replace('"', "")
                )
                data["open"][programm_name] = programm_path
                with open("./json_data/usefull_data.json", "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=True, indent=4)
            else:
                pass

        if path != "":
            try:
                os.startfile(path)
            except Exception:
                try:
                    if system == "Windows":
                        webbrowser.get("windows-default").open(path)
                    else:
                        webbrowser.open(path)
                except Exception:
                    print(Exception)
                    print(
                        "Dieses Programm kann ich leider nicht öffnen!\n Möglichkeiten sind:"
                    )
                    for name in programm_names:
                        print(name)
        return "Gerne"


class SearchamazonCommand(Command):
    def execute(self):
        message = self.message.lower()
        if "nach " in message:
            message = message.split("nach")[1]
        elif "amazon " in message:
            message = message.split("amazon")[1]
        elif "auf amazon " in message:
            message = message.split("amazon")[1]
        search = message.replace(" ", "+")
        webbrowser.get("windows-default").open("https://smile.amazon.de//s?k=" + search)
        # playsound.playsound("sounds\hierSindMeineSuchergebnisse.mp3")
        return "Hier sind meine Suchergebnisse"


class WikipediaCommand(Command):
    def execute(self):
        try:
            message = self.message.lower()
            list_of_common_inputs = [
                "zu",
                "schlag",
                "nach",
                "über",
                "wikipedia",
                "wikipediaartikel",
                "definition",
                "von",
            ]
            for input_ in list_of_common_inputs:
                if input_ in message:
                    message = message.split(input_)[1].strip()

            wikipedia.set_lang("de")
            result = wikipedia.summary(message, sentences=5)
            command = "echo " + result + "| clip"
            os.system(command)
            d = json.load(open("./json_data/usefull_data.json", encoding="utf-8"))
            d["read"] = result
            with open("./json_data/usefull_data.json", "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=4)

            print(
                "Die Definition von "
                + message
                + " ist: \n"
                + result.replace("“", "").replace("„", "")
            )
            print('\nZum vorlesen das Lesen Kommando nutzen: z.B."vorlesen"')
            return "Artikel eingelesen"
        except wikipedia.exceptions.DisambiguationError:
            return (
                "Zu diesem Begriff ist auf Wikipedia kein eindeutiger Artikel vorhanden"
            )
        except wikipedia.exceptions.PageError:
            return "Zu diesem Begriff ist auf Wikipedia kein Artikel vorhanden"


class PersonaldataCommand(Command):
    def execute(self):
        message = self.message
        with open("./json_data/inandout.json", encoding="utf-8") as f:
            inandouts = json.load(f)

        with open("./json_data/usefull_data.json", encoding="utf-8") as f2:
            data = json.load(f2)

        oldname = data["PersonalData"]["Name"]
        personaldata = data["PersonalData"]
        list_of_keys = personaldata.keys()

        def changeData(key, value):
            data["PersonalData"][key] = value
            newname = data["PersonalData"]["Name"]
            with open("./json_data/usefull_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            if oldname != newname:
                for i in inandouts.keys():
                    if inandouts[i]["outputs"] != "":
                        inandouts[i]["outputs"] = [
                            w.lower().replace(oldname.lower(), newname)
                            for w in inandouts[i]["outputs"]
                        ]
                with open("./json_data/inandout.json", "w", encoding="utf-8") as f:
                    json.dump(inandouts, f, ensure_ascii=False, indent=4)

        def changeKeys(key, delete=True):
            ok = False
            if delete == True:
                for p in personaldata:
                    if p == key:
                        ok = True
                if ok:
                    del data["PersonalData"][key]
                    with open("./json_data/usefull_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                else:
                    self.jarvis.talkToMe("Keine solchen Daten vorhanden")

        def checkKeys(key):
            for i in list_of_keys:
                if i.lower() in key.lower():
                    return i
            else:
                return ""

        if "zeige " in message:
            ok = False
            for key in list_of_keys:
                if key.lower() in message:
                    self.jarvis.talkToMe(key + ": " + personaldata[key])
                    ok = True
            if not ok:
                for i in list_of_keys:
                    self.jarvis.talkToMe(i + ": " + personaldata[i])
            return ""

        elif "ändere " in message:
            if checkKeys(message) != "":
                what_to_change = checkKeys(message)
            else:
                what_to_change = self.jarvis.getNextMessage(
                    "Welche Daten willst du ändern? Name, Alter, Geschlecht oder Wohnort?\n>..>"
                )
            for change in list_of_keys:
                if change.lower() == what_to_change.lower():
                    change_in = self.jarvis.getNextMessage(
                        "Wie soll dein " + change + " sein\n>..>"
                    )
                    changeData(what_to_change, change_in)
                    return "Deine Persönlichen Daten wurden geändert"

        elif "sprich mich " in message:
            if " mit " in message:
                name = message.split("mit ")[1]
                if " an" in name:
                    name = name.split(" an")[0].capitalize()
                    changeData("Name", name)
                    return "Sehr gerne " + name

        elif (
            "neu" in message
            or "weiter" in message
            or ("füge " in message and " hinzu" in message)
        ):
            add_data_key = self.jarvis.getNextMessage(
                "Welche Datan möchtest du Hinzufügen?\n>..>"
            )
            add_data_value = ""
            if " und " in add_data_key:
                add_data_key = add_data_key.split(" und ")
                for i in add_data_key:
                    add_data_value = self.jarvis.getNextMessage(
                        "Welcher Wert soll für "
                        + add_data_key
                        + " hinzugefügt werden?\n>..>"
                    )
            else:
                add_data_value = self.jarvis.getNextMessage(
                    "Welcher Wert soll für "
                    + add_data_key
                    + " hinzugefügt werden?\n>..>"
                )
                changeData(add_data_key, add_data_value)
            return "Die Daten wurden hinzugefügt"

        elif "lösche" in message or "entferne" in message:
            if checkKeys(message) != "":
                delete_data_key = checkKeys(message)
            else:
                delete_data_key = self.jarvis.getNextMessage(
                    "Welche Daten möchtest du löschen?\n>..>"
                )
            if " und " in delete_data_key:
                delete_data_key = delete_data_key.split(" und ")
                for i in delete_data_key:
                    for j in personaldata.keys():
                        if j in delete_data_key:
                            delete_data_key = j
            else:
                changeKeys(delete_data_key)
            return "Die Daten wurden gelöscht"


class AddnewCommand(Command):
    def execute(self):
        message = self.message
        with open("./json_data/inandout.json") as file:  # json datei wird geöffnet
            data = json.load(
                file
            )  # inhalt wird in der variablen data gespeichert, da die datei nach Austritt aus der with-schleife wieder geschlossen wird
        self.jarvis.talkToMe("Zu welcher Kategorie gehört die Antwort? ")
        print(
            "Neu (0)", end=" / "
        )  # hier kann man auswählen (mit Eingabe einer Nummer) welcher Kategorie der neue Command hinzugefüggt wird
        num = 0
        for i in data.keys():  # für jede Überschrift (des jeweiligen dicts)
            num += 1
            ende = " / "
            print(
                i + "(" + str(num) + ")", end=ende
            )  # den namen der Kategorie ausgeben, den man dann durcht eingabe einer zahl (num) auswählen
        range_list = range(
            0, int(len(data) + 1)
        )  # range list auf die Länge der liste an dicts setzen

        def get_input():
            takeIn = self.jarvis.getNextMessage(
                prompt="\n>..>"
            )  # Input reinnehmen (Zahl des dicts, dem der neue Command hinzugefügt werden soll)
            try:
                takeIn = int(
                    takeIn
                )  # Es wird versucht, den Input auf eine integer zu setzen, damit man das dict anwählen kann
                if (
                    takeIn not in range_list
                ):  # wenn das dict nicht vorhanden ist, wird eine neue Zahl angefordert
                    self.jarvis.talkToMe(
                        "Du musst eine Zahl zwischen 0 und "
                        + str(len(data))
                        + " eingeben."
                    )  # Bereich der akzeptierten Zahlen
                    get_input()  # Funktion wird neugestartet
            except Exception:  # wenn das nicht geht fordert man erneut eine Zahl an
                print("\n---------NOT POSSIBLE--------\n")
                self.jarvis.talkToMe("Bitte geben Sie eine Zahl ein.")
                takeIn = get_input()
            return takeIn  # hier wird dann der input als integer zurückgegeben

        takeIn = get_input()
        if (
            takeIn in range_list
        ):  # wenn die erhaltene Nummer auch wirklich innerhalb der möglichen aufrufbaren Zahlen liegt
            if takeIn == 0:  # wenn man eine neue Kategorie anlegen möchte
                self.jarvis.talkToMe("Wie soll die neue Kategorie heissen?")
                newName = self.jarvis.getNextMessage(
                    prompt=">..>"
                )  # neuer Name der Kategorie
                append_question = message
                with open(
                    "./json_data/inandout.json", encoding="utf-8"
                ) as f:  # Json datei wird mit utf-8 (standart) kodierung geöffnet, damit man auch spezielle Buchstaben wie ß,ö,ä,ü verwenden kann
                    dat = json.load(
                        f
                    )  # speichern des Dateiinhalts, da nach beenden der with-schleife die datei wieder geschlossen wird
                append_answer = self.jarvis.getNextMessage(
                    "Wie soll die neue Antwort lauten?\n>..>"
                )  # welche Antwort soll gegeben werden
                dat[newName] = {
                    "inputs": [append_question],
                    "outputs": [append_answer],
                }  # in der variablen dat (liste von dictionarys) wird ein neus dict angelegt, das den neuen Namen trägt
                with open(
                    "./json_data/inandout.json", "w", encoding="utf-8"
                ) as f:  # wiederholtes Öfnnen der Json Datei
                    json.dump(
                        dat, f, ensure_ascii=False, indent=4
                    )  # schreiben in die json datei: genau das gleiche wie geholt wurde nur mit ergänzungen
                return "Antwort erfolgreich hinzugefügt!"
            else:  # wenn keine neue Kategorie sondern ein neuer Eintrag in einer vorhanden Kategorie erstellt werden soll
                num = 0
                for k in data:  # für jeden eintrag in der json datei
                    num += 1
                    if (
                        num == takeIn
                    ):  # wenn die vorher eingegebene Zahl gleich der Zahl also auch der Stelle der Kategorie ist
                        append_qu = message  # die frage wird für später in einer variablen gespeichert
                        with open(
                            "./json_data/inandout.json", "r", encoding="utf-8"
                        ) as f:  # Json datei wird mit utf-8 (standart) kodierung geöffnet, damit man auch spezielle Buchstaben wie ß,ö,ä,ü verwenden kann
                            dat = json.load(
                                f
                            )  # speichern des Dateiinhalts, da nach beenden der with-schleife die datei wieder geschlossen wird
                        wanna_append = self.jarvis.getNextMessage(
                            "Willst du einen neue Antwort hinzufügen? "
                        )
                        if wanna_append in self.yes:
                            append_ans = str(
                                self.jarvis.getNextMessage(
                                    "Wie soll die neue Antwort lauten? "
                                )
                            )  # neue antwort
                            if (
                                append_ans not in data[k]["outputs"]
                            ):  # wenn diese antwort noch nicht existiert, wird sie hinzugefügt
                                dat[k]["outputs"].append(append_ans)
                        dat[k]["inputs"].append(
                            append_qu
                        )  # die frage wird den inputs hinzugefügt
                        with open(
                            "./json_data/inandout.json", "w", encoding="utf-8"
                        ) as f:  # wiederholtes Öfnnen der Json Datei
                            json.dump(
                                dat, f, ensure_ascii=False, indent=4
                            )  # schreiben in die json datei: genau das gleiche wie geholt wurde nur mit ergänzungen
                return "Erfolgreich übernommen"


    def execute(self):
        def addnew(date_):
            weekdays = {
                "monday": "montag",
                "tuesday": "dienstag",
                "wednesday": "mittwoch",
                "thursday": "donnerstag",
                "friday": "freitag",
                "saturday": "samstag",
                "sunday": "sonntag",
            }
            day, month, year = (int(x) for x in date_.split("."))
            weekday = weekdays[datetime.date(year, month, day).strftime("%A").lower()]
            monthname = calendar.month_name[month].lower()
            with open("./json_data/kalender.json", encoding="utf-8") as f:
                d = json.load(f)
            d[date_] = {"weekday": weekday, "monthname": monthname, "plan": {}}
            with open("./json_data/kalender.json", "w", encoding="utf-8") as f2:
                json.dump(d, f2, ensure_ascii=False, indent=4)

        with open("./json_data/kalender.json", encoding="utf-8") as f:
            data = json.load(f)
        d = datetime.datetime.now()
        weekdays_en_de = {
            "monday": "montag",
            "tuesday": "dienstag",
            "wednesday": "mittwoch",
            "thursday": "donnerstag",
            "friday": "freitag",
            "saturday": "samstag",
            "sunday": "sonntag",
        }
        weekdays = {
            "montag": 0,
            "dienstag": 1,
            "mittwoch": 2,
            "donnerstag": 3,
            "freitag": 4,
            "samstag": 5,
            "sonntag": 6,
        }
        day_expressions = {
            "vorvorgestern": -3,
            "vorgestern": -2,
            "gestern": -1,
            "morgen": 1,
            "übermorgen": 2,
            "überübermorgen": 3,
        }
        cal = {
            "date": d.strftime("%d.%m.%Y"),
            "time": d.strftime("%H:%M"),
            "hour": d.strftime("%H"),
            "day": d.strftime("%d"),
            "month": d.strftime("%m"),
            "year": d.strftime("%Y"),
            "weekday": d.strftime("%A").lower(),
            "monthname": d.strftime("%B"),
        }

        take_in = self.message

        if "zeig" in take_in or "was " in take_in or "wie sieht" in take_in:
            plan = ""
            tag = 0
            date = [str(x.group()) + "." for x in re.finditer(r"\d+", take_in)]
            try:
                y = int(date[-1].replace(".", ""))
                m = int(date[-2].replace(".", ""))
                dy = int(date[-3].replace(".", ""))
                dt = datetime.datetime(y, m, dy).strftime("%Y-%m-%d")
                if len(date[1]) == 1:
                    date[1] = "0" + date[1]
                date[2] = date[2].replace(".", "")
                date = "".join(str(i) for i in date)
            except Exception:
                date = []
            for wd in weekdays:
                if wd in take_in:
                    tag = weekdays[wd] - weekdays[weekdays_en_de[cal["weekday"]]]
                    if "nächsten " in take_in or "nächster ":
                        if "über" in take_in:
                            tag += take_in.count("über") * 7 + 7
                        else:
                            tag += 7
            else:
                for de in day_expressions:
                    if de in take_in:
                        tag = day_expressions[de]

            if date != []:
                cal["date"] = date
            else:
                cal["date"] = (
                    datetime.datetime.now() + datetime.timedelta(tag)
                ).strftime("%d.%m.%Y")
            try:
                plan = data[cal["date"]]["plan"]
            except KeyError:
                self.jarvis.talkToMe("Für diesen Tag haben Sie noch keine Pläne")
            if plan != {}:
                self.jarvis.talkToMe("Ihr Plan für " + cal["date"] + ":")
                for time in plan:
                    # self.jarvis.talkToMe(time + " - " + plan[time]["To_when"] +"\n  ↪ "+  plan[time]["what"])
                    self.jarvis.talkToMe(
                        "  Von "
                        + time
                        + " Uhr bis "
                        + plan[time]["To_when"]
                        + " : "
                        + plan[time]["what"]
                    )
            else:
                return "Sie haben für diesen Tag noch keine Pläne"
            return ""

        if "trage " in take_in or "neu" in take_in:
            day = take_in
            date = [str(x.group()) + "." for x in re.finditer(r"\d+", take_in)]
            try:
                y = int(date[-1].replace(".", ""))
                m = int(date[-2].replace(".", ""))
                dy = int(date[-3].replace(".", ""))
                dt = datetime.datetime(y, m, dy).strftime("%Y-%m-%d")
                if len(date[1]) == 1:
                    date[1] = "0" + date[1]
                date[2] = date[2].replace(".", "")
                date = "".join(str(i) for i in date)
            except Exception:
                date = ""
            if date != "":
                day = date
            else:
                tag = 0
                for wd in weekdays:
                    if wd in day:
                        tag = weekdays[wd] - weekdays[weekdays_en_de[cal["weekday"]]]
                        if "nächsten " in day or "nächster " in day:
                            if "über" in day:
                                tag += day.count("über") * 7 + 7
                            else:
                                tag += 7
                else:
                    for de in day_expressions:
                        if de in day:
                            tag = day_expressions[de]
                day = (datetime.datetime.now() + datetime.timedelta(tag)).strftime(
                    "%d.%m.%Y"
                )
            time_list = ["um ", "von "]
            for tl in time_list:
                if tl in take_in:
                    zeit = take_in.split(tl)[1].strip()
                    break
            else:
                zeit = self.jarvis.getNextMessage("Zeit: ").lower()
            zeit = zeit.replace(" uhr", "").replace("uhr", "")
            From_when = ""
            To_when = ""
            try:
                f = data[day]
            except KeyError:
                addnew(day)
                import time

                time.sleep(0.2)

            if "von " in zeit:
                zeit = zeit.split("von ")[1]
            elif "bis " in zeit:
                From_when = zeit.split("bis ")[0].replace("von ", "")
                To_when = zeit.split("bis ")[1]
            elif "-" in zeit:
                From_when = zeit.split("-")[0].strip().replace("von ", "")
                To_when = zeit.split("-")[1].strip()
            else:
                From_when = (
                    self.jarvis.getNextMessage("Von wann?")
                    .lower()
                    .replace(" uhr", "")
                    .replace("uhr", "")
                    .strip()
                )
                To_when = (
                    self.jarvis.getNextMessage("Bis wann?")
                    .lower()
                    .replace(" uhr", "")
                    .replace("uhr", "")
                    .strip()
                )
            From_when = From_when.strip().replace(" ", "")
            To_when = To_when.strip().replace(" ", "")

            if From_when[0] == "0":
                From_when = From_when[1:]
                start_hour = From_when[0]
            else:
                if len(From_when) == 5 or (
                    len(From_when) == 2 and From_when[:2].isdigit()
                ):
                    start_hour = From_when[0:2]
                else:
                    start_hour = From_when[0]

            if To_when[0] == "0":
                To_when = To_when[1:]
                end_hour = To_when[0]
            else:
                if len(To_when) == 5 or (len(To_when) == 2 and To_when[1].isdigit()):
                    end_hour = To_when[0:2]
                else:
                    end_hour = To_when[0]

            def new_time(what="", name=""):
                if what == ":":
                    if name == "Anfang":
                        try:
                            if start_hour.isdigit():
                                return (start_hour) + ":00"
                            else:
                                raise Exception
                        except Exception:
                            sh = self.jarvis.getNextMessage(
                                "Die Anfangszeit war nicht richtig eingegeben.\nErneute Eingabe. Von wann: "
                            )
                            if ":" not in sh:
                                sh = (sh) + ":00"
                            else:
                                return sh
                    elif name == "Ende":
                        try:
                            if end_hour.isdigit():
                                return (end_hour) + ":00"
                            else:
                                raise Exception
                        except Exception:
                            eh = self.jarvis.getNextMessage(
                                "Die Endzeit war nicht richtig eingegeben.\nErneute Eingabe. Bis wann: "
                            )
                            if ":" not in eh:
                                return eh + ":00"
                            else:
                                return eh
                elif what == "new":
                    if name == "Anfang":
                        sh = self.jarvis.getNextMessage(
                            "Die Anfangszeit war nicht richtig eingegeben.\nErneute Eingabe. Von wann: "
                        )
                        if ":" not in sh:
                            sh = sh + ":00"
                        try:
                            if (
                                len(sh) in range(4, 6)
                                and sh[-3] == ":"
                                and (
                                    int(sh[0:2]) in range(25)
                                    or (int(sh[0:1]) in range(25) and sh[2] == ":")
                                )
                            ):
                                return sh
                            else:
                                return new_time(what="new", name="Anfang")
                        except Exception:
                            return new_time("new", "Anfang")
                        else:
                            return new_time("new", "Anfang")

                    elif name == "Ende":
                        eh = self.jarvis.getNextMessage(
                            "Die Endzeit war nicht richtig eingegeben.\nErneute Eingabe. Bis wann: "
                        )
                        if ":" not in eh:
                            eh = eh + ":00"
                        try:
                            if (
                                len(eh) in range(4, 6)
                                and eh[-3] == ":"
                                and (
                                    int(eh[0:2]) in range(25)
                                    or (int(eh[0:1]) in range(25) and eh[2] == ":")
                                )
                            ):
                                return eh
                            else:
                                return new_time(what="new", name="Ende")
                        except Exception:
                            return new_time("new", "Ende")
                        else:
                            return new_time("new", "Ende")

            if ":" not in From_when:
                From_when = new_time(what=":", name="Anfang")
            if ":" not in To_when:
                To_when = new_time(what=":", name="Ende")
            try:
                if int(start_hour) not in range(25) or From_when == "":
                    From_when = new_time(what="new", name="Anfang")
            except Exception:
                new_time("new", "Anfang")
            try:
                if int(end_hour) not in range(25) or To_when == "":
                    To_when = new_time(what="new", name="Ende")
            except Exception:
                new_time("new", "Ende")
            with open("./json_data/kalender.json", encoding="utf-8") as f:
                data = json.load(f)
            planned = self.jarvis.getNextMessage("Was ist geplant?: ")
            old_plan = data[day]["plan"]
            print(From_when)
            print(To_when)
            if len(From_when) == 4:
                From_when = "0" + From_when
            data[day]["plan"][From_when] = {"To_when": str(To_when), "what": planned}
            data[day]["plan"] = {}
            for o in sorted(old_plan):
                data[day]["plan"][o] = old_plan[o]
            dta = {}
            for i in sorted(data):
                dta[i] = data[i]
            with open("./json_data/kalender.json", "w", encoding="utf-8") as f:
                json.dump(dta, f, ensure_ascii=False, indent=4)

            return "Der Kalender wurde aktualisiert"


class ReadCommand(Command):
    def execute(self):
        message = (
            self.message.lower()
            .strip()
            .replace("jarvis ", "")
            .replace("hey jarvis ", "")
            .replace("bitte ", "")
        )
        read_in_and_outs = self.inandouts["Read"]["inputs"]
        read_this = "Nichts drinnen"
        for i in read_in_and_outs:
            if i == message:
                with open("./json_data/usefull_data.json", encoding="utf-8") as f:
                    read_this = json.load(f)
                read_this = read_this["read"]
                break
        else:
            read_this = message
            for i in read_in_and_outs:
                if i in read_this:
                    read_this = read_this.split(i)[1]
            write_in_file = self.data
            write_in_file["read"] = read_this
            with open("./json_data/usefull_data.json", "w", encoding="utf-8") as f:
                json.dump(write_in_file, f, ensure_ascii=False, indent=4)

        return read_this


class WhatcanyoudoCommand(Command):
    def execute(self):
        return super().execute()


class WeatherCommand(Command):
    def execute(self):
        message = self.message
        if "in " in message:
            location = message.split("in ")[1]
        else:
            location = self.jarvis.getNextMessage(
                "Von welcher Stadt wollen Sie das Wetter wissen?\n>..>"
            )
        api_link = (
            "https://api.openweathermap.org/data/2.5/weather?q="
            + location
            + "&appid=efcabea9a839b92f7efae93eff363068&lang=de"
        )
        link = requests.get(api_link)
        data = link.json()
        if data["cod"] == 200:
            lon = data["coord"]["lon"]
            lat = data["coord"]["lat"]
            api_link2 = (
                "https://api.openweathermap.org/data/2.5/onecall?lat="
                + str(lat)
                + "&lon="
                + str(lon)
                + "&exclude=minutely,hourly&appid=efcabea9a839b92f7efae93eff363068&lang=de"
            )
            link2 = requests.get(api_link2)
            data_all = link2.json()
            today_temp = (
                data_all["daily"][0]["temp"]["min"] - 273.15,
                data_all["daily"][0]["temp"]["max"] - 273.15,
            )
            day_night_temp = (
                data_all["daily"][0]["temp"]["day"] - 273.15,
                data_all["daily"][0]["temp"]["night"] - 273.15,
            )
            morning_evening_temp = (
                data_all["daily"][0]["temp"]["morn"] - 273.15,
                data_all["daily"][0]["temp"]["eve"] - 273.15,
            )
            feels_like_day_night_morn_eve = (
                data_all["daily"][1]["feels_like"]["day"] - 273.15,
                data_all["daily"][1]["feels_like"]["night"] - 273.15,
                data_all["daily"][1]["feels_like"]["morn"] - 273.15,
                data_all["daily"][1]["feels_like"]["eve"] - 273.15,
            )
            day_description = data_all["daily"][1]["weather"][0]["description"]
            day_hum = data_all["daily"][1]["humidity"]
            current_temp = data["main"]["temp"] - 273.15
            current_description = data["weather"][0]["description"]
            feels_linke_now = data["main"]["feels_like"] - 273.15
            sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime(
                "%H:%M"
            )
            sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime(
                "%H:%M"
            )
            windspeed_now = data["wind"]["speed"]
            current_hum = data["main"]["humidity"]
            if "ist " in message:
                return (
                    "\n"
                    + location
                    + ": "
                    + current_description
                    + ". Es herrschen Temperaturen von "
                    + str(current_temp)[0:5]
                    + "°C, gefühlt sind das "
                    + str(feels_linke_now)[0:5]
                    + "°C. Der Wind erreicht heute Geschwindigkeiten bis zu "
                    + str(windspeed_now)
                    + "km/h, die Luftfeuchtigkeit beträgt "
                    + str(current_hum)
                    + "%, die Sonne geht um "
                    + sunrise
                    + " Uhr auf und um "
                    + sunset
                    + " Uhr unter\n"
                )
            else:
                if "ausführlich " in message:
                    write_this = (
                        "Die Wettervorhersage für "
                        + location
                        + " lautet: \n"
                        + day_description
                        + "\nEs herrschen die folgenden Temperaturen: \nMorgens: "
                        + str(morning_evening_temp[1])[:4]
                        + "°C (gefühlt "
                        + str(feels_like_day_night_morn_eve[2])[:4]
                        + "°C) \nMittags: "
                        + str(day_night_temp[0])[:4]
                        + "°C (gefühlt "
                        + str(feels_like_day_night_morn_eve[0])[:4]
                        + "°C) \nAbends: "
                        + str(morning_evening_temp[1])[:4]
                        + "°C (gefühlt "
                        + str(feels_like_day_night_morn_eve[3])[:4]
                        + "°C) \nNachts: "
                        + str(day_night_temp[1])[:4]
                        + "°C (gefühlt "
                        + str(feels_like_day_night_morn_eve[1])[:4]
                        + "°C)\nMaximaltemperatur: "
                        + str(today_temp[1])[:4]
                        + "°C \nMinimaltemperaturen:"
                        + str(today_temp[0])[:4]
                        + "°C \nDie durchschnittliche Luftfeuchtigkeit beträgt "
                        + str(day_hum)
                        + "%"
                    )
                else:
                    write_this = (
                        "Wettervorhersage:\n   "
                        + day_description
                        + "\nTemperaturen: \n   Tagsüber: "
                        + str(day_night_temp[0])[:4]
                        + "°C (gefühlt "
                        + str(feels_like_day_night_morn_eve[0])[:4]
                        + "°C) \n   Nachts: "
                        + str(day_night_temp[1])[:4]
                        + "°C (gefühlt "
                        + str(feels_like_day_night_morn_eve[1])[:4]
                        + "°C)\n   Maximaltemperatur: "
                        + str(today_temp[1])[:4]
                        + "°C \n   Minimaltemperaturen:"
                        + str(today_temp[0])[:4]
                        + "°C"
                    )

            with open("./json_data/usefull_data.json", encoding="utf-8") as f:
                d = json.load(f)
            d["read"] = write_this
            with open("./json_data/usefull_data.json", "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=4)
            print(write_this)
            return "Wetter eingelesen"
        else:
            return "\nInvalid City Name: " + location + "! \n\nTry again\n"


class WhattimeCommand(Command):
    def execute(self):
        time = datetime.datetime.now().strftime("%H:%M")
        return time


class ChangenameofassistentCommand(Command):
    def execute(self):
        message = self.message
        data = json.load(open("./json_data/usefull_data.json", encoding="utf-8"))
        name = data["name_of_programm"]
        if " nennen" in message:
            name = message.split(" nennen")[0].split(" ")[-1]
        data["name_of_programm"] = name
        json.dump(
            data,
            open("./json_data/usefull_data.json", "w", encoding="utf-8"),
            indent=4,
            ensure_ascii=False,
        )


class YoutubedownloaderCommand(Command):
    def execute(self):
        message = self.message
        choices = ["720p", "144p", "only audio"]
        choice = self.jarvis.getNextMessage(
            "Wähle die Qualität: " + ", ".join(choices) + " >"
        ).lower()
        if choice in choices:
            folder_name = "./dowloads"
        if not "https://www.youtube.com/watch?" in message:
            url = input("Gib die URL ein >")
        else:
            url = [
                i for i in message.split(" ") if "https://www.youtube.com/watch?" in i
            ][0]

        def confirm(select):
            select.dowload(folder_name)
            play = self.jarvis.getNextMessage(
                "Das Video wurde gespeichert. Soll ich es abspielen? >"
            )
            if play in self.yes:
                pass

        if len(url) > 1:
            yt = YouTube(url)
            if choice == choices[0]:
                select = yt.streams.filter(progressive=True).first()
                confirm(select)
            elif choice == choices[1]:
                select = yt.streams.filter(
                    progressive=True, file_extension="mp4"
                ).last()
                confirm(select)
            elif choice == choices[2]:
                select = yt.streams.filter(only_audio == True).first()
            else:
                self.jarvis.talkToMe("Das hat nicht ganz geklappt")


class SchooltimetableCommand(Command):
    def execute(self):
        data: dict = json.load(open("./json_data/school_timetable.json", "r", encoding="utf-8"))

        weekdays = [day for day, value in data.items()]
        day_expressions = {"gestern": -1, "morgen": 1, "tomorrow": 1, "yesterday": -1}

        week_A_timestamp = 1631484000.000001
        then = datetime.datetime.fromtimestamp(week_A_timestamp)
        self.jarvis.talkToMe("From when do you want to know your schedule?", lang="en")
        when = self.jarvis.getNextMessage(">..>")
        if when.replace("next ", "").replace("this ", "") in weekdays:
            weekdays = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
            }
            current_weekday = datetime.datetime.now().strftime("%A").lower()
            difference = (
                weekdays[when.replace("next ", "").replace("this ", "")]
                - weekdays[current_weekday]
            )
            if "next " in when:
                difference += 7
            now = datetime.datetime.now() + datetime.timedelta(difference)

        else:
            add = 0
            for key, value in day_expressions.items():
                if key in when:
                    if key == "gestern":
                        vors = when.count("vor")
                        add = value - vors
                    elif key == "morgen":
                        ubers = when.count("über")
                        add = value + ubers

            now = datetime.datetime.now() + datetime.timedelta(days=add)
        duration = now - then
        duration_sec = duration.total_seconds()
        days = divmod(duration_sec, 86400)[0]
        week = "A" if days % 14 < 7 else "B"
        weekday = now.strftime("%A").lower()
        courses = data[weekday]

        returning = "\n"
        for hours, details in courses.items():
            h = hours.split(" - ")

            hour_endings_english = {
                "1": "st",
                "2": "nd",
                "3": "rd",
                "4": "th",
                "5": "th",
                "6": "th",
                "7": "th",
                "8": "th",
                "9": "th",
                "10": "th",
                "11": "th",
            }

            h1 = h[0] + hour_endings_english[h[0]]

            if len(h) > 1:
                h2 = h[1] + hour_endings_english[h[1]]
                addition = f"From the {h1} to the {h2}"

            else:
                addition = f"In the {h1}"

            course = details["course"]
            room = details["room"]

            if "[A]" in course or "[B]" in course:
                if week == "A":
                    course = course.split(" [A];")[0].replace(" [A]; ", "")
                elif week == "B":
                    course = course.split("[A]; ")[1].replace("[B]", "")
            if "[A]" in room or "[B]" in room:
                if week == "A":
                    room = room.split(" [A];")[0].replace(" [A]; ", "")
                elif week == "B":
                    room = room.split("[A]; ")[1].replace("[B]", "")

            returning += (
                addition
                + f" hour you have {course} "
                + (f" in room {room}" if room != " " else "")
                + "\n"
            )
        self.jarvis.talkToMe(returning, lang="en")
        return ""

#         from jarvis import SpeakingJarvis as speak, Jarvis as jarvis, SpeakingAndListeningJarvis as saljarvis, ListeningJarvis as listen
#         message = self.message
#         if "texteingabe" in message:
#             jarvis = Jarvis()
#         elif "mikrofon" in message or "mikrophon" in message or ("höre" in message and "stimme" in message):
#             if "sprich" in message or "lautsprecher" in message or "dich laut" in message:
#                 jarvis = SpeakingAndListeningJarvis()
#             else:
#                 jarvis = ListeningJarvis()
#         elif "sprich" in message or "lautsprecher" in message or "dich laut" in message:
#             if "mikrofon" in message or "mikrophon" in message or ("höre" in message and "stimme" in message):
#                 jarvis = SpeakingAndListeningJarvis()
#             else:
#                 jarvis = SpeakingJarvis()
#         else:
#             jarvis = Jarvis()
#         jarvis.run()
