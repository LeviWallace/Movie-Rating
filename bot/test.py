import sys

if (len(sys.argv) != 3):
    if (len(sys.argv) == 2):
        print('InputError: too few arguments')
    if (len(sys.argv) > 3):
        print('InputError: too many arguments')
    if (len(sys.argv) > 1 or (sys.argv[1].isnumeric() == 0)):
        print('InputError: first argument invalid')
    if (len(sys.argv) > 2 or (sys.argv[2].isnumeric() == 0)):
        print('InputError: second argument invalid')
    print('Usage: python operations.py')
    print('Example:\fpython operations.py 10 3')
else:
    a = int(sys.argv[1])
    b = int(sys.argv[2])
    print("Sum:          {}".format(a + b))
    print("Difference:   {}".format(a - b))
    print("Product:      {}".format(a * b))
    if (b == 0):
        print("Quotient:     ERROR (div by zero)")
        print("Remainder:    ERROR (modulo by zero)")
    else:
        print("Quotient:     {}".format(a / b))