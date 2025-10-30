import os
a = bytes(input().encode())

b = os.open("./clwork", os.O_WRONLY)

os.write(b, a)
os.close(b)