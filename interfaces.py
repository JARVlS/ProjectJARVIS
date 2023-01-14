class CommandNotFoundError(Exception):
    pass
class AbstractJarvis:

    def run(self):
        raise NotImplementedError('override in subclass')

    def getNextMessage(self):
        raise NotImplementedError('override in subclass')

    def buildCommandList(self):
        raise NotImplementedError('override in subclass')

    def retrieveCommand(self, message: str):
        raise NotImplementedError('override in subclass')

    def talkToMe(self):
        raise NotImplementedError('override in subclass')

    def addNewCommand(self, message: str):
        # Methode, die zwingend implementiert sein muss, wirft Fehler, wenn sie es nicht ist
        raise NotImplementedError('override in subclass')

    def etwas_freiwilliges(self):
        # Methode, die optional implementiert sein kann, tut einfach nichts.
        pass


class AbstractCommand:
    def __init__(self, jarvis: AbstractJarvis):
        self.jarvis = jarvis

    def test(self, message: str):
        raise NotImplementedError('override test in a subclass')

    def execute(self):
        raise NotImplementedError('override execute in a subclass')