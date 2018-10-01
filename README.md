AES

Collaborators: Wenyuan Wu(ww6767), Brandon Chan(Bec944), Yaoyang Liu(yl27488)

To run the program:

python aes.py --keysize $KEYSIZE --keyfile $KEYFILE --inputfile $INPUTFILE--outputfile$OUTFILENAME --mode $MODE

Files: aes.py, tables.py

keysize is 128 or 256
keyfile is a file that acts as the key
inputfile is the file to encrypt
outputfile is the resulting encrytpion/decryption
mode is "encrypt" or "decrypt"

Our AES works as follows:
1. read input
2. determine how to do key expansion with the given key, whether 128 or 256 bits, then run key expansion
3. given an expanded key, and an input file, run the encryption or decryption
4. write output to a given output file

_______________________________________________________________________________________

Our AES encryption works based on the given NIST document.

With a given expanded key, we determine how many rounds we perform. We loop over
every 16 bytes, applying repeated actions
1. Convert the 16 bytes into a matrix, column major
2. Add round key with 1st round(original key)
3. Loop through all the rounds, applying sub bytes, shift row, and mix column.
	NOTE: according to the NIST document, you DO NOT apply mix columns to the last iteration
4. after this loop, we append the resulting encryption to a list of all encrypted bytes
5. We then proceed to flatten the bytes, from matrices to a stream, then write the bytes to a given output file


Again, our AES decryption follows close pseudo code from the NIST document.

1. loop over all 16 bytes in the input
2. convert those 16 bytes into a matrix
3. Apply add Round key
4. Loop over the rounds
	-We do not do it completely backwards, i.e. add round key-> mix columns-> shift rows -> sub bytes
	-This is because we skip mix columns in the last iteration of encryption
	-Thus we loop shift rows, sub bytes, add round key, and mix columns
5. After this loop, we perform an edge case that doesn't include mix columns
6. Like encryption, we append to a list, flatten the bytes, then write it to a file

_______________________________________________________________________________________

ideas/parts of the cipher:

Key Expansion:
- For each key, we first read in the entire key as a 1D list, then then reshaped into a 4xn column majored 2D list.
- Following mostly the pseudo code, we expand the key by performing xor two specific two columns, and for the column that has the index that is multiples of nk, we also did the round column operation, etc.
- When the key expansion is done, we split the key vertically to the round number of equal sized matrices. Use each for every round. 

Sub bytes:
-based on a byte in the matrix on 16 bytes, we use that byte to index into tables.py, sTables. This table is the table that is used to substitute bytes, also used in key expansion. The byte is converted into an index, and the table contains the substitute byte.
-The opposite is not bad, we just look for the index that contains the already substituted byte. We then swap the sub byte with its index


shift rows:
-This is simply shifting rows based on the index. Pretty easy to implement, and pretty easy to reverse. simply use [:] to grab all elements in a row, and [i:] elements past index i

Mix Columns:
- the tables.py is an object that contains all the look up tables needed for this assignment. For mix columns, the table also includes galois fields (2D List) for both encryptionand decryption. 
- Perform matrix multiplication (except you xor the results instead of adding) using th galois matrix and each 16 bytes of inputs. Use corresponding galois table for fast access of the product. 


Add Round key:
-add round key is just xor-ing a specific round key from key expansion, and the 16 bytes.
-for decrypting, we do the same process, xor-ing it again reverts to the pre add round key 16 bytes











