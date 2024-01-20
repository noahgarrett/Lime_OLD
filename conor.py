
class Car:
    def __init__(self) -> None:
        self.color = "blue"

car = Car()
print(car.color)

class FordCar(Car):
    def __init__(self) -> None:
        super().__init__()

        self.color = "red"

class ChevyCar(Car):
    def __init__(self) -> None:
        super().__init__()

        self.color = "green"

f_car = FordCar()
print(f_car.color)

c_car = ChevyCar()
print(c_car.color)
