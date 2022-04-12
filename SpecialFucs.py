class specials(object):
    def __init__(self):
        self.list = [['func1', self.func1]]
    def func1(self, screen, GAME, script):
        print(1)
        return GAME, script