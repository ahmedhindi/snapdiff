@snapper(mode='snap')
def adder(a, b):
    return a + b


@snapper(mode='snap')
def subtractor(a, b):
    return a - b


@snappp
@snapper(mode='snap')
def multiply(a, b):
    return a * b


class Calculator:

    @snapper(mode='snap')
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @snapper(mode='snap')
    def add(self):
        return self.a + self.b

    @snapper(mode='snap')
    def subtract(self):
        return self.a - self.b

    @snapper(mode='snap')
    def multiply(self):
        return self.a * self.b

    @snapper(mode='snap')
    def divide(self):
        return self.a / self.b
