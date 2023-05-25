import numpy as np
import sys
import math
import copy
import heapq
import operator #for sorting lists of classes by attribute
import bitstring
from timeit import default_timer as timer
from datetime import timedelta
import pickle

class HuffmanNode:
    """Huffman encoding tree node"""
    
    character = -1      #the character represented
    index = -1          #index of character (integer)
    count = -1          #character frequency (count) in the file
    left = None           #left child node
    right = None          #right child node
    code = bitstring.BitArray()    #bitstring code for the character
    
    #constructor
    def __init__(self,character):
        self.character = character
        self.index = int.from_bytes(self.character, sys.byteorder)
        self.count = 0
    
    #for printing
    def __repr__(self):
        return str("Huffman Node") + str(self.__dict__)
        
    #for printing
    def __str__(self):
        return str("Huffman Node") + str(self.__dict__)
        
    #comparison operator required for heapq comparison
    def __lt__(self, other):
        return self.count < other.count

    #print function (non-recursive)
    def print(self):
        print("Huffman Node: ")
        print("\tCharacter = ", self.character)
        print("\tIndex = ", self.index)
        print("\tCount = ", self.count)
        has_left = (self.left != [])
        has_right = (self.right != [])
        print("\tHas left child = ", has_left)
        print("\tHas right child = ", has_right)
        print("\tCode = ", self.code)

#done
def getfilecharactercounts(filename):
    """ Read a file and count characters """

    f = open(filename,"rb")
    nodes = []
    
    #for every character of interest (and then some) create a huffman node
    for i in range(0,256):
        nodes.append(HuffmanNode(bytes([i]))) #works in python 3
    
    #loop over file reading a character at a time and increment the count
    #of that character in the list of huffman nodes
    while True:
        c = f.read(1)
        if c:
            index = int.from_bytes(c, sys.byteorder)
            nodes[index].count += 1
        else:
            #print("End of file")
            break

    f.close()
    
    #mark and delete any characters that don't occur in the file
    #i.e., nodes should be as long as the number of unique characters in the file (not 256 things long)

    nodes = [node for node in nodes if node.count > 0]
    nodes.sort(key=lambda HuffmanNode: HuffmanNode.count)

    return nodes


def createhuffmantree(huffmannodes):
    """ Create the huffman tree
        Using heapq functionality to build the tree from a priority queue"""

    node_heap = copy.deepcopy(huffmannodes)  #first create a copy
    heapq.heapify(node_heap)                 #create heap

    #Create the Huffman Node Tree using the Min Priority Queue (heap)
    for i in range(len(huffmannodes) - 1):
        leftNode = heapq.heappop(node_heap)
        rightNode = heapq.heappop(node_heap)
        parentNode = HuffmanNode(bytes([0]))
        parentNode.left = leftNode
        parentNode.right = rightNode
        parentNode.count = leftNode.count + rightNode.count
        heapq.heappush(node_heap,parentNode)
    return heapq.heappop(node_heap) #final node is the tree we want


def codehuffmantree(huffmantreenode, nodecode):
    """ Traverse Huffman Tree to produce Prefix Codes"""
    #huffmantreenode.print()
    #print("Nodecode = ", nodecode)
    
    if (huffmantreenode.left == None and huffmantreenode.right == None):
        huffmantreenode.code = nodecode     #no children - assign code
    else:
        leftcode = copy.copy(nodecode)      #append 0 to left
        leftcode.append(bitstring.Bits('0b0'))
        codehuffmantree(huffmantreenode.left,leftcode)
        rightcode = copy.copy(nodecode)     #append 1 to right
        rightcode.append(bitstring.Bits('0b1'))
        codehuffmantree(huffmantreenode.right,rightcode)


def listhuffmancodes(huffmantreenode, codelist):
    """ Create a list of Prefix Codes from the Huffman Tree"""
    if (huffmantreenode.left == None and huffmantreenode.right == None):
        codelist[huffmantreenode.index] = huffmantreenode.code
    else:
        listhuffmancodes(huffmantreenode.left,codelist)
        listhuffmancodes(huffmantreenode.right,codelist)


def canonical_list(codelist):
    """ Create a list whose indexes are lenghts of the huffman codes and the entry for each
        index is a list of characters whose original huffman code is that length"""
    
    #find the longest number of bits in all huffman codes
    longest_length = 0
    for code in codelist:
        if code != None and len(code) > longest_length:
            longest_length = len(code)
    
    all_bitlengths = [[] for _ in range(longest_length + 1)]

    #for each code length, add all characters with that code length to all_bitlengths[code_length]
    for index,code in enumerate(codelist):
        if code != None: 
            all_bitlengths[len(code)].append(index)
        else:
            all_bitlengths[0].append(index)

    return all_bitlengths
    

def canonical_encode(canon):
    """
        given a list of indexes with a code of given length, generate
        a canonical huffman code by
        starting with a new code of 0b0 and a length of 1, for each unique code
        with a given length increment by 1 and assign this new code to the
        character at that index. When moving on to a new length, append a '0'
        to maintain the length for each code

    """
    newCodelist = [None]*256
    newCode = bitstring.BitArray('0b0')
    last_index = canon[len(canon)-1][-1] #get last element in entire list
    stop = False

    for i in range(1,len(canon)):
        for index in canon[i]:
            newCodelist[index] = newCode
            #print("index", index, "has new code", newCode.bin)
            if index != last_index:
                newCode_int = newCode.uint + 1
                newCode = bitstring.BitArray(uint=newCode_int, length=i)
            #makes the last index's code go one over without this condition
            else:
                stop = True
        if stop != True:       
            newCode.append(bitstring.Bits('0b0'))

    return newCodelist


def huffmanencodefile(filename):
    """ Read and Encode a File using Huffman Codes"""
        
    counts = getfilecharactercounts(filename) #get the counts from the file
        
    huffmantree = createhuffmantree(counts) #create and encode the characters
    codehuffmantree(huffmantree,bitstring.BitArray())
    
    codelist = [None]*256
    listhuffmancodes(huffmantree, codelist) #get the codes for each character

    canon = canonical_list(codelist) #change huffman codes to a canonical format
    
    canon_codelist = canonical_encode(canon)
    #otherCanon = canonical_list(canon_codelist)
    #[print("the indexes with bitlength", i, "are", canon[i] ) for i in range(len(canon))]

    #get total number of characters
    #char_count = [0 for _ in range(256)]
    total_char = 0
    for node in counts:
        #char_count[node.index] = node.count
        total_char += node.count
    print("Total number of characters from encode function", total_char)

    #print all present character codes as well as their huffman code
    print("---------------------------------------------------")
    print("ENCODED CODELIST")
    print("---------------------------------------------------")
    for i in range(0,256):
        if canon_codelist[i] != None:
            print("character ", chr(i), " maps to code ", canon_codelist[i].bin)
    
    
    #encode the file
    with open(filename, 'rb') as f:
        filecode = bitstring.BitArray()
        while True:
            c = f.read(1)
            index = int.from_bytes(c, sys.byteorder)
            if c:
                filecode.append(canon_codelist[index])
            else:
                break #eof


    #write the file
    #print(filecode)
    with open(filename + ".huf", 'wb') as coded_file:
        #Write the bitstring (and any additional information necessary) to file
        #huffmantree_bytes.tofile(coded_file)

        #write the number of bits for each character to the file
        #bitlength of 0 means it doesn't appear in the text
        for length in canon_codelist:
            if length is None:
                character_count = bitstring.BitArray(uint=0, length=8)
            else:
                character_count = bitstring.BitArray(uint=len(length), length=8)
            character_count.tofile(coded_file)
        
        #write the total number of characters to the file
        bitstring.BitArray(uint=total_char, length=24).tofile(coded_file)

        #write the encoded text to file
        filecode.tofile(coded_file)
 

def huffmandecodefile(filename):
    """ Decode a Huffman-Coded File"""
    #read the file
    char_counts = [0 for _ in range(256)]
    
    decode_file_name = filename + ".dec"
    with open(filename , 'rb', buffering=0) as f, open(decode_file_name, 'w') as decode_file:
        #read all character counts
        for i in range(256):
            #print(i)
            char_counts[i] = int.from_bytes(f.read(1), "big")
        
        #read total character count
        total_char = int.from_bytes(f.read(3), "big")
    
        print("total number of characters read from decode function =", total_char)

        #find the longest number of bits in all huffman codes
        longest_length = 0
        shortest_length = 10000000
        for count in char_counts:
            if count > 0 and count < shortest_length :
                shortest_length = count
            if count > longest_length:
                longest_length = count

        #create 2d list of code lengths and indexes
        all_bitlengths = [[] for _ in range(longest_length + 1)]
        for index,count in enumerate(char_counts):
            all_bitlengths[count].append(index)

        #[print("the indexes with bitlength", i, "are", all_bitlengths[i] ) for i in range(longest_length + 1)]   
        canon_codelist = canonical_encode(all_bitlengths)
        #print all present character codes as well as their huffman code
        print("---------------------------------------------------")
        print("DECODED CODELIST")
        print("---------------------------------------------------")
        for i in range(0,256):
            if canon_codelist[i] != None:
                print("character ", chr(i), " maps to code ", canon_codelist[i].bin)

        #create a list of dictionaries with keys as codes and entries as the index
        #each entry in the list contains dictionaries with codewords of same length
        huff_code = [{} for _ in range(len(all_bitlengths))]
        for i in range(1,len(all_bitlengths)):
            for index in all_bitlengths[i]:
                codeAsDictKey = bitstring.ConstBitStream(canon_codelist[index])
                huff_code[i][codeAsDictKey] = index 

        #[print("codes with index length", i , "are ", huff_code[i]) for i in range(len(huff_code))]

        #decode the file using huff_code
        bitFile = bitstring.ConstBitStream(f.read())
        char_read = 0
        start = 0
        
        while(char_read < total_char):
            for length in range(shortest_length, longest_length+1):
                #print("checking code in range", start, "to", length)
                codeToCheck = bitFile[start:start+length]
                #print("checking code", codeToCheck)
                inDict = codeToCheck in huff_code[length]
                if inDict : #found matching code
                    decode_file.write(chr(huff_code[length].get(codeToCheck)))
                    #print("character found", chr(inDict), "at position", length)
                    start = start + length 
                    char_read = char_read + 1
                    break
                elif not inDict and length == longest_length :
                    return "invalid code found! " + str(codeToCheck)
               
    return "Done, total characters read = " + str(char_read)
    

def compareFiles(f1,f2):
    with open(f1, 'r') as f1, open(f2, 'r') as f2:
        f1_data = f1.readlines()
        f2_data = f2.readlines()
        same = True

        if len(f1_data) != len(f2_data):
            same = False

        else:
            for i in range(len(f1_data)):
                if f1_data[i] != f2_data[i]:
                    same = False
                    break
    if not same:
        return "Decreypted file different from encrypted file!"
    else:
        return "Decrypted file same as encrypted file."


#main
filename="./LoremIpsumLong.rtf"
huffmanencodefile(filename)
char_count= getfilecharactercounts(filename)
#[print(char) for char in char_count]
err = huffmandecodefile(filename + ".huf") #uncomment once this file is written

print(compareFiles(filename, filename+".huf.dec"))



