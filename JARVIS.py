import json, subprocess, string, pkg_resources, sys
from platform import system 

system = sys

list_of_packages = {
    "typing",
    "pynput",
    "psutil",
    "pytube",
    # "pyaudio",
    "playsound",
    "speechrecognition",
    "wikipedia",
    "sklearn",
    "nltk"
}  # liste der Bibliotheken, die man benötigt und die nicht standartmäßig installiert sind
if system == "Windows":  # für windows-systeme wird noch pyttsx3 für die sprachausgabe installiert
    list_of_packages.add("pyttsx3")
elif system == "Linux":  # für linux-systeme wird noch gtts für die spracherkennung installiert
    list_of_packages.add("gtts")

installed = {
    pkg.key for pkg in (pkg_resources.working_set)
}  # die bereits installierten pakete werden erkannt
missing = (
    list_of_packages - installed
)  # die noch nicht installierten werden daraus erkannt

if missing:  # wenn noch welche fehlen, werden diese nachinstalliert
    python = sys.executable
    subprocess.check_call([python, "-m", "pip", "install", *missing])

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from nltk.stem.snowball import GermanStemmer, EnglishStemmer
from nltk.tokenize import word_tokenize
from commands import *
import commands

# Corpus einlesen
with open("./json_data/learn_list.json", encoding="utf-8") as f:
    learn_data: dict = json.load(f)

corpus = []
y = []
i = 0
for command, sentences in learn_data.items():
    for sentence in sentences:
        corpus.append(sentence)
        y.append(i)
    i += 1

stemmer = GermanStemmer()


def nltk_tokenizer(sentence: str):
    words = word_tokenize(sentence)
    return [stemmer.stem(word) for word in words if word not in string.punctuation]


# unser Dokument-zu-Matrix-Transformierer
# https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
# https://de.wikipedia.org/wiki/Tf-idf-Ma%C3%9F

vectorizer = CountVectorizer(
    tokenizer=nltk_tokenizer,  # wir nutzen unseren NLTK-Stemmer
    min_df=2,  # nur Wörter, die 2x oder öfter vorkommen (damit Rötteln usw entfällt)
    max_df=0.8,  # sperre Wörter aus, die in 80% aller Dokumente vorkommen (oder öfter)
)
# vectorizer = TfidfVectorizer(tokenizer=nltk_tokenizer)

X = vectorizer.fit_transform(corpus)
M = X.toarray()
# print(vectorizer.get_feature_names())

from sklearn.naive_bayes import GaussianNB, ComplementNB, MultinomialNB

# gnb = GaussianNB()
# gnb.fit(M, y)

# cnb = ComplementNB()
# cnb.fit(M, y)

mnb = MultinomialNB()
mnb.fit(M, y)


class Jarvis:
    def __init__(self, inandout="json_data/inandout.json"):
        self.message = ""
        self.data = json.load(open("./json_data/usefull_data.json", encoding="utf-8"))
        self.name_of_assistent = self.data["name_of_programm"]
        self.name_of_owner=self.data["PersonalData"]["Name"]
        self.language = self.data["language"]
        self.learn_list = json.load(open("./json_data/learn_list_en.json"))
        self.yes = self.data["yes"]
        self.inandout = json.load(open(inandout, encoding="utf-8"))
        self.previousinput = ""
        self.previouscommand = ""
        self.current_responses = []

    def identify_command(self, message=""):
        """
        Identifies searched name from the learnlist and assiciates their names
        with the according command -> *Name*Command (PlaymusicCommand)
        """
        T = vectorizer.transform([message]).toarray()
        command_name = list(learn_data.keys())[mnb.predict(T)[0]]
        print(command_name)
        self.current_responses = self.inandout[command_name]["outputs"]
        return getattr(commands, f"{command_name}Command", Command)

    def getNextMessage(self, prompt=">..>"):
        return input(prompt)

    def talkToMe(self, output, lang="de"):
        if output is not None:
            print(output.replace("put_name_here", self.name_of_owner))
    
    def run(
        self,
        message="default_message_jarvis_run",
        previous_message="",
        previous_command=Command,
    ):
        self.message = (
            self.getNextMessage()
            if message == "default_message_jarvis_run"
            else message
        )
        identified_command = self.identify_command(self.message)
        command: Command = identified_command(
            jarvis=self,
            responses=self.current_responses,
            message=self.message,
            previous_message=previous_message,
            previous_command=previous_command,
        )
        self.talkToMe(command.execute())
        self.run(self.getNextMessage(), self.message, command)

class SpeakingJarvis(Jarvis):
    def talkToMe(self, output):
        return super().talkToMe(output)

if __name__ == "__main__":
    jarvis = Jarvis()
    # print(jarvis.identify_command("Schicke bitte eine Whatsapp nachricht an Amelie"))
    jarvis.run()
