class Dog:
    def sit(self):
        print("Dog is stiing")

    def bark(self, n : int):
        print("bark " * n)

#a = Dog()
#a.sit()
#a.bark(10)

def cnt_cube(n : int):
    for i in range(1, n + 1):
        yield i**3

for x in cnt_cube(5):
    print(x)
