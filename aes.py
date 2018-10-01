

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
    column = []
    for i in range(len(matrix)):
        column.append(matrix[i][idx])

    return column

# def matrix_to_hex(matrix):
#     for row in matrix:
#         for element in row:
#             # print(hex(element))

#     return
# def split_keys_bytes(key):

# ------------- Above are Helper Functions----------


def read_input(inputfile):
    hex = []
    dump = os.popen("xxd " + inputfile).read()
    dump = dump.split('\n')
    dump = list(filter(('').__ne__, dump))
    for row in dump:
        row = row.split(' ')
        row.pop()
        row.pop(0)
        row = row[0:row.index("")]
        row = list(filter(('').__ne__, row))
        hex.append(row)

    return hex


def read_key_input(keyfile):
    key = []
    dump = os.popen("xxd " + keyfile).read()
    dump = dump.split('\n')
    dump = list(filter(('').__ne__, dump))
    for row in dump:
        row = row.split(' ')
        row.pop()
        row.pop(0)
        row = row[0:row.index("")]
        row = list(filter(('').__ne__, row))
        key += (row)
    return key


def splitting(hex):
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
    return hex2


def padding(hex2):
    last_row = hex2[len(hex2)-1]
    total_bytes = int(sum(len(element) for element in last_row)/2)
    missing_bytes = 16 - total_bytes
    if(missing_bytes == 0):
        # pad 16 bytes
        row = ['10']*16
        hex2.append(row)
    else:
        for i in range(missing_bytes):
            hex_string = '{:02x}'.format(missing_bytes)
            hex2[len(hex2)-1].append(hex_string)

    return hex2


def split_key_bytes(key):
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


# opposite of sub_bytes_encrypt
# this method returns a list of consecutive bytes
def sub_bytes_decrypt(matrix):
    new_list = list(matrix)

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            fourBytes = []
            element = matrix[i][j]
            # need to scan through the sub byte
            # table in search of the target byte
            idx = tables.Sbox.index(element)
            # new_list.append(str(hex(idx)))
            new_list[i][j] = idx
    return new_list


def shift_rows_encrypt(matrix):
    for i in range(len(matrix)):
        row = matrix[i]
        row = row[i:]+row[0:i]
        matrix[i] = row
    return matrix


def shift_rows_decrypt(matrix):
    for i in range(len(matrix)):
        row = matrix[i]
        row[:] = row[-i:] + row[:-i]
        matrix[i] = row
    return matrix


def mix_columns_encrypt(matrix):
    new_matrix = zero_matrix(len(matrix))
    galois = tables.galois

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            # get the matrix column
            col = [matrix[0][j], matrix[1][j], matrix[2][j], matrix[3][j]]
            gal = galois[i]

            # get the product
            column = []
            for k in range(len(col)):
                which_table = gal[k]
                if(which_table == 1):
                    column.append(col[k])
                elif(which_table == 2):
                    table = tables.mul2
                    column.append(table[col[k]])
                else:
                    table = tables.mul3
                    column.append(table[col[k]])
            final_value = column[0]
            for z in range(1, len(column)):
                final_value = final_value ^ column[z]
            new_matrix[i][j] = final_value

    return new_matrix


def mix_columns_decrypt(matrix):
    new_matrix = zero_matrix(len(matrix))
    galois = tables.otherGalois

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            # get the matrix column
            col = [matrix[0][j], matrix[1][j], matrix[2][j], matrix[3][j]]
            gal = galois[i]

            # get the product
            column = []
            for k in range(len(col)):
                which_table = gal[k]
                if(which_table == 9):
                    table = tables.mul9
                    column.append(table[col[k]])
                elif(which_table == 11):
                    table = tables.mul11
                    column.append(table[col[k]])
                elif(which_table == 13):
                    table = tables.mul13
                    column.append(table[col[k]])
                else:
                    table = tables.mul14
                    column.append(table[col[k]])
            final_value = column[0]
            for z in range(1, len(column)):
                final_value = final_value ^ column[z]
            new_matrix[i][j] = final_value

    return new_matrix


def rot_word(l):
    rotate = [l[1], l[2], l[3], l[0]]
    return rotate


def subword(l):
    for i in range(len(l)):
        l[i] = tables.Sbox[int(l[i])]

    return l


def rcon(i):
    constant = [1, 2, 4, 8, 16, 32, 64, 128, 27, 54]

    return [constant[i], 0, 0, 0]


def key_expansion(key, key_size):
    for i in range(len(key)):
        for j in range(len(key[0])):
            if (type(key[i][j]) is str):
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
        temp = []
        temp.append(expanded_key[0][i - 1])
        temp.append(expanded_key[1][i - 1])
        temp.append(expanded_key[2][i - 1])
        temp.append(expanded_key[3][i - 1])
        if(i % nk == 0):
            temp = xorLists(subword(rot_word(temp)), rcon(int(i / nk) - 1))
        elif (nk > 6 and i % nk == 4):
            temp = subword(temp)

        wi_sub_nk = [expanded_key[0][i-nk]]
        wi_sub_nk.append(expanded_key[1][i - nk])
        wi_sub_nk.append(expanded_key[2][i - nk])
        wi_sub_nk.append(expanded_key[3][i - nk])

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


def addRoundKey(roundKey, sixteen):
    result = []
    for i in range(0, len(sixteen)):
        result.append(xorLists(roundKey[i], sixteen[i]))
    return result


def readArguments():
    arguments = {}

    # capture keysize, turn into int
    arguments["keysize"] = int(sys.argv[sys.argv.index("--keysize") + 1])

    # capture keyfile
    arguments["keyfile"] = sys.argv[sys.argv.index("--keyfile") + 1]

    # capture input file
    arguments["inputfile"] = sys.argv[sys.argv.index("--inputfile") + 1]

    # capture output file
    arguments["outputfile"] = sys.argv[sys.argv.index("--outputfile") + 1]
    # capture mode
    arguments["mode"] = sys.argv[sys.argv.index("--mode") + 1]

    return arguments


def obtain_file_size(hex):
    total_bytes = 0
    for l in hex:
        total_bytes += int(sum(len(element) for element in l)/2)

    return total_bytes


def flatten_bytes(encryted_bytes):
    encryted_bytes_remove_padding = []
    for matrix in encryted_bytes:
        for j in range(len(matrix[0])):
            for i in range(len(matrix)):
                encryted_bytes_remove_padding.append(matrix[i][j])

    return encryted_bytes_remove_padding


def writeToFile(flatten_bytes, outputfile):
    with open(outputfile, 'wb') as f:
        f.write(bytearray(i for i in flatten_bytes))

    f.close()

    return flatten_bytes


def remove_pad(flatten_bytes):

    num_bytes_to_remove = flatten_bytes[len(flatten_bytes)-1]

    flatten_bytes = flatten_bytes[:len(flatten_bytes)-num_bytes_to_remove]
    return flatten_bytes


def encryption(hex, all_keys, outputfile):

    round_numbers = len(all_keys)
    encrypted_bytes = []  # store all the encrypted matrix
    # perform encoding for each 16 bytes
    for sixteen in hex:

        matrix = to_matrix(sixteen, 4)
        matrix = addRoundKey(all_keys[0], matrix)

        for num_round in range(1, round_numbers):

            # subbytes:
            matrix = sub_bytes_encrypt(matrix)

            # shiftRows
            matrix = shift_rows_encrypt(matrix)

            # mix columns
            if(num_round < round_numbers-1):
                matrix = mix_columns_encrypt(matrix)

            # add round key
            matrix = addRoundKey(all_keys[num_round], matrix)
        encrypted_bytes.append(matrix)

    encrypted_bytes = flatten_bytes(encrypted_bytes)
    encrypted_bytes = writeToFile(encrypted_bytes, outputfile)


def decryption(hex, all_keys, outputfile):
    round_numbers = len(all_keys)
    decrypted_bytes = []  # store all the encrypted matrix
    all_keys = list(reversed(all_keys))

    for sixteen in hex:
        matrix = to_matrix(sixteen, 4)
        matrix = addRoundKey(all_keys[0], matrix)

        for i in range(1, round_numbers - 1):

            matrix = shift_rows_decrypt(matrix)

            matrix = sub_bytes_decrypt(matrix)

            matrix = addRoundKey(all_keys[i], matrix)

            matrix = mix_columns_decrypt(matrix)

        matrix = shift_rows_decrypt(matrix)

        matrix = sub_bytes_decrypt(matrix)

        matrix = addRoundKey(all_keys[round_numbers - 1], matrix)

        decrypted_bytes.append(matrix)

    decrypted_bytes = flatten_bytes(decrypted_bytes)

    decrypted_bytes = remove_pad(decrypted_bytes)
    decrypted_bytes = writeToFile(decrypted_bytes, outputfile)


# -------- Main Method -------------
def main():
    arguments = readArguments()
    # print(arguments)
    # input the data and padding it.
    hex = read_input(arguments["inputfile"])
    # file_size = obtain_file_size(hex)

    hex = splitting(hex)
    if(arguments['mode'] == 'encrypt'):
        hex = padding(hex)

    # input the key
    key = read_key_input(arguments["keyfile"])

    # split the bytes
    key = split_key_bytes(key)

    # expanded the key
    key_size = arguments["keysize"]
    expanded_key = key_expansion(key, key_size)

    # split the key
    all_keys = split_key(expanded_key)
    # for key in all_keys:
    #     print_matrix(key)
    #     print('---------------------------')
    if arguments["mode"] == "encrypt":
        encryption(hex, all_keys, arguments["outputfile"])

    elif arguments["mode"] == "decrypt":
        # print("here", arguments)
        decryption(hex, all_keys, arguments["outputfile"])


if __name__ == "__main__":
    main()
