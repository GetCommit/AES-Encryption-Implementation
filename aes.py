import os
import sys
import math
from tables import *

tables = tables()
rcon = []

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
    row = n
    col = int(len(l)/n)

    # zero matrix
    matrix = []
    for i in range(row):
        matrix.append([0]*col)

    idx = 0
    for j in range(col):
        for i in range(row):
            matrix[i][j] = l[idx]
            idx += 1

    return matrix

def xorLists(a, b):
    c = []
    for i in range(0, len(a)):
        a2 = a[i]
        b2 = b[i]
        if(type(a2) is str):
            a2 = int(a2, 16)
        if(type(b2) is str):
            b2 = int(b2, 16)
        c.append(a2 ^ b2)

    return c

def col_by_idx(matrix, idx):
    l = []
    for i in range(len(matrix)):
        l.append(matrix[i][idx])

    return l

def matrix_to_hex(matrix):
    for row in matrix:
        for element in row:
            print(hex(element))
# ------------- Above are Helper Functions----------


def read_input():
    hex=[]
    dump = os.popen("xxd input").read()
    dump = dump.split('\n')
    dump = list(filter(('').__ne__, dump))
    for row in dump:
        row = row.split(' ')
        row.pop()
        row.pop(0)
        row = list(filter(('').__ne__, row))
        hex.append(row)

    return hex

def read_key_input():
    key=[]
    dump = os.popen("xxd key").read()
    dump = dump.split('\n')
    dump = list(filter(('').__ne__, dump))
    for row in dump:
        row = row.split(' ')
        row.pop()
        row.pop(0)
        row = list(filter(('').__ne__, row))
        key += (row)


    return key


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

def split_key(key):
    new_key = []
    for k in key:
        new_key.append(k[0:2])
        new_key.append(k[2:])

    new_key = to_matrix(new_key, 4)
    return new_key

def sub_bytes_encrypt(matrix):
    new_matrix = zero_matrix(len(matrix))

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            element = matrix[i][j]
            if(type(element) is str):
                element = int(element, 16)

            idx = element
            new_matrix[i][j] = tables.Sbox[idx]
    return new_matrix

#opposite of sub_bytes_encrypt
#this method returns a list of consecutive bytes
def sub_bytes_decrypt(matrix):
    new_list = []

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            fourBytes = []
            element = matrix[i][j]
            #need to scan through the sub byte table in search of the target byte
            idx = tables.Sbox.index(element)
            new_list.append(str(hex(idx)))
    return new_list

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

def rot_word(l):
    l = [l[1], l[2], l[3], l[0]]
    return l
def subword(l):
    for i in range(len(l)):
        l[i] = tables.Sbox[int(l[i])]

    return l

def rcon(i):
    l = [1, 2, 4, 8, 16, 32, 64, 128, 27, 54]

    return [l[i], 0 , 0, 0]


def key_expansion2(key, key_size):
    for i in range(len(key)):
        for j in range(len(key[0])):
            key[i][j] = int(key[i][j], 16)
    expanded_key = list(key)
    if(key_size == 128):
        nk = 4
        round = 10
    elif(key_size == 192):
        nk = 6
        round = 12
    else:
        nk = 8
        round = 14

    i = nk
    while(i < 4*(round+1)):
        temp = [expanded_key[0][i-1], expanded_key[1][i-1], expanded_key[2][i-1], expanded_key[3][i-1]]
        if(i%nk == 0):
            temp = xorLists (subword(rot_word(temp)), rcon(int(i/nk)-1))
        elif (nk > 6 and i%nk == 4):
            temp = subword(temp)

        wi_sub_nk = [expanded_key[0][i-nk], expanded_key[1][i-nk], expanded_key[2][i-nk], expanded_key[3][i-nk]]
        wi = xorLists(wi_sub_nk, temp)
        # append to expanded_key
        for idx in range(len(expanded_key)):
            expanded_key[idx].append(wi[idx])
        i += 1


    return expanded_key

def split_key(expanded_key):
    all_keys = []

    for j in range(0, len(expanded_key[0]), 4):
        key = []
        for i in range(len(expanded_key)):
            key.append(expanded_key[i][j:j+4])
        all_keys.append(key)

    return all_keys


# def key_expansion(key):
#     # str hex to int
#     for i in range(len(key)):
#         for j in range(len(key[0])):
#             key[i][j] = int(key[i][j], 16)

#     all_keys = [key]

#     bits = len(key)*len(key[0])*8
#     if bits is 128:
#         rounds = 10
#     elif bits is 192:
#         rounds = 12
#     elif bits is 256:
#         rounds = 14
#     else:
#         print("error")
#         return

#     for i in range(1, rounds+1):
#         previous_key = all_keys[i - 1]
#         last_col = [previous_key[len(previous_key)-1][3], previous_key[len(previous_key)-1][0], previous_key[len(previous_key)-1][1], previous_key[len(previous_key)-1][2]]
#         #map with sub table
#         for j in range(0, len(last_col)):
#             last_col[j] = tables.Sbox[last_col[j]]

#         #xor with round constant
#         round_constant = [i, 0, 0, 0]

#         last_col = xorLists(last_col, round_constant)

#         new_col = xorLists(last_col, col_by_idx(previous_key, 0)) # needs to fix

#         # new_round_key = [new_col]
#         # for j in range(1, len(previous_key)):
#         #     current_col = xorLists(previous_key[j], new_round_key[j-1])
#         #     new_round_key.append(current_col)

#         # all_keys.append(new_round_key)

#         new_round_key = [[], [], [], []]
#         for j in range(len(new_col)):
#             new_round_key[j].append(new_col[j])

#         for j in range(1, len(previous_key[0])):
#              current_col = xorLists(col_by_idx(previous_key, j), col_by_idx(new_round_key, j-1))

#              for k in range(len(new_round_key)):
#                 new_round_key[k].append(current_col[k])

#         all_keys.append(new_round_key)

#     return all_keys

def addRoundKey(roundKey, sixteen):
    result = []
    for i in range(0, len(sixteen)):
        result.append(xorLists(roundKey[i], sixteen[i]))
    return result

def readArguments():
    arguments = {}

    #capture keysize, turn into int
    arguments["keysize"] = int(sys.argv[sys.argv.index("--keysize") + 1])

    #capture keyfile
    arguments["keyfile"] = sys.argv[sys.argv.index("--keyfile") + 1]

    #capture input file
    arguments["inputfile"] = sys.argv[sys.argv.index("--inputfile") + 1]

    #capture output file
    arguments["outputfile"] = sys.argv[sys.argv.index("--outputfile") + 1]
    #capture mode
    arguments["mode"] = sys.argv[sys.argv.index("--mode") + 1]

    return arguments



# -------- Main Method -------------
def main():
    # arguments = readArguments()
    # print(arguments)
    # input the data and padding it.
    hex = read_input()
    hex = splitting_padding(hex)

    # mock the hex 
    hex = [['32', '43', 'f6', 'a8', '88', '5a', '30', '8d', '31', '31', '98', 'a2', 'e0', '37', '07', '34'], ['16', '16', '16', '16', '16', '16', '16', '16', '16', '16', '16', '16', '16', '16', '16', '16']]

    # input the key
    # Checking if the key is 
    key = read_key_input()
    key = split_key(key)
    # split the bytes

    # mock the keys
    key = [['2b', '28', 'ab', '09'], ['7e', 'ae', 'f7', 'cf'], ['15', 'd2', '15', '4f'], ['16', 'a6', '88', '3c']]

    # expanded the key
    key_size = 128
    expanded_key = key_expansion2(key, 128)

    # split the key
    all_keys = split_key(expanded_key)
    # for key in all_keys:
    #     print_matrix(key)
    #     print('---------------------------')

    round_numbers = len(all_keys)
    # perform encoding for each 16 bytes
    for sixteen in hex:

        matrix = to_matrix(sixteen, 4)
        matrix = addRoundKey(all_keys[0], matrix)

        for num_round in range(1, round_numbers):

            # convert to a 4x4 2D list

            # subbytes:
            matrix = sub_bytes_encrypt(matrix)

            # sub_bytes_decrypt
            # listOfBytes = sub_bytes_decrypt(matrix)
            # sub_bytes_decrypt(listOfBytes)

            # shiftRows
            matrix = shift_rows_encrypt(matrix)

            # mix columns
            matrix = mix_columns_encrypt(matrix)

            #add round key
            matrix = addRoundKey(all_keys[num_round], matrix)
            print_matrix(matrix)
            print('------------')
        print('------------------------------------------------')
if __name__ == "__main__":
  main()