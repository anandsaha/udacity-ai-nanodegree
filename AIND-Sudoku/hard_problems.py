import io

f = open('hard_problems.txt')
lines = f.readlines()

for l in lines:
    print("'" + l.strip() + "', \n", end='')


