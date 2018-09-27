import os
from tables import *

tables = tables()

# ------------Helper functions-----------
def zero_matrix(n):
    matrix = []
    for i in range(n):
        matrix.append([0]*n)
    return matrix

def print_matrix(matrix):
    for row in matrix:
        print(row)
    return

def to_matrix(l, n):
    matrix = [l[i:i + n] for i in range(0, len(l), n)]
    return matrix

# ------------- Above are Helper Functions----------


def read_input():
    hex=[]
    dump = os.popen("xxd inputfile.txt").read()
    dump = dump.split('\n')
    dump = list(filter(('').__ne__, dump))
    for row in dump:
        row = row.split(' ')
        row.pop()
        row.pop(0)
        row = list(filter(('').__ne__, row))
        hex.append(row)

    return hex

def splitting_padding(hex):
    hex2 = []
    for row in hex:
        new_row = []
        for element in row:
            if(len(element) == 4):
                new_row.append(element[0:2])
                new_row.append(element[2:])
            else:
                new_row.append(element)
        hex2.append(new_row)

    # first pad if total bytes less than 16
    last_row = hex2[len(hex2)-1]
    total_bytes = int(sum(len(element) for element in last_row)/2)
    missing_bytes = 16 - total_bytes
    if(missing_bytes == 0):
        # pad 16 bytes
        row = ['16']*16
        hex2.append(row)
    else:
        for i in range(missing_bytes):
            hex2[len(hex2)-1].append(str(missing_bytes))

    return hex2


def sub_bytes_encrypt(matrix):
    new_matrix = zero_matrix(len(matrix))

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            element = matrix[i][j]
            x = int(element[0])
            y = int(element[1])
            new_matrix[i][j] = tables.Sbox[x][y]
    return new_matrix

#todo
def sub_bytes_decrypt(matrix):
    new_matrix = zero_matrix(len(matrix))

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            element = matrix[i][j]
            x = int(element[0])
            y = int(element[1])
            new_matrix[i][j] = tables.Sbox[x][y]
    return new_matrix

def shift_rows_encrypt(matrix):
    for i in range(len(matrix)):
        row = matrix[i]
        row = row[i:]+row[0:i]
        matrix[i] = row
    return matrix

#opposite of the above method, i have 0 idea how this works,
#i ripped it from online, can anyone explain this to me?
def shift_rows_decrypt(matrix):
    for i in range(len(matrix)):
        row = matrix[i]
        row[:] = row[-i:] + row[:-i]
        matrix[i] = row
    return matrix

def mix_columns_encrypt(matrix):
    new_matrix = zero_matrix(len(matrix))
    galois = tables.galois

    # matrix multiplication
    for row in galois:
        for j in range(len(matrix[0])):
            for i in range(len(matrix)):
                element = matrix[i][j]
                which_table = row[i]

                if(which_table == 1):
                    new_matrix[i][j] = element
                elif(which_table == 2):
                    table = tables.mul2
                    new_matrix[i][j] = table[element]
                else:
                    table = tables.mul3
                    new_matrix[i][j] = table[element]

    return new_matrix


# -------- Main Method -------------
def main():

    # input the data and padding it.
    hex = read_input()
    hex = splitting_padding(hex)

    # perform encoding for each 16 bytes
    for sixteen in hex:

        # convert to a 4x4 2D list
        matrix = to_matrix(sixteen, 4)

        # subbytes:
        matrix = sub_bytes_encrypt(matrix)

        # shiftRows
        matrix = shift_rows_encrypt(matrix)
        
        # decrypt shift
        # matrix = shift_rows_decrypt(matrix)


        # mix columns
        # matrix = mix_columns_encrypt(matrix)

if __name__ == "__main__":
  main()