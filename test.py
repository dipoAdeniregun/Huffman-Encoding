a = [3, 4, 5]
with open("test.txt", 'rb') as test:
    for i in range(2):
        a = int(test.read(3))
        print(a)
    