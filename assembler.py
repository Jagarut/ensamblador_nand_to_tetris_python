import re, os, sys

SYMBOLS_TABLE = {
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SCREEN': 16384,
    'KBD': 24576,
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
}

dest = {
   'null':'000',
   'M':'001',
   'D':'010',
   'MD':'011',
   'A':'100',
   'AM':'101',
   'AD':'110',
   'ADM':'111',
}

jump = {
   'null':'000',
   'JGT':'001',
   'JEQ':'010',
   'JGE':'011',
   'JLT':'100',
   'JNE':'101',
   'JLE':'110',
   'JMP':'111',
}

comp = {
    '0':'101010',
    '1':'111111',
    '-1':'111010',
    'D':'001100',
    'A':'110000',
    'M':'110000',
    '!D':'001101',
    '!A':'110001',
    '!M':'110001',
    '-D':'001111',
    '-A':'110011',
    '-M':'110011',
    'D+1':'011111',
    'A+1':'110111',
    'M+1':'110111',
    'D-1':'001110',
    'A-1':'110010',
    'M-1':'110010',
    'D+A':'000010',
    'D+M':'000010',
    'D-A':'010011',
    'D-M':'010011',
    'A-D':'000111',
    'M-D':'000111',
    'D&A':'000000',
    'D&M':'000000',
    'D|A':'010101',  
    'D|M':'010101',  
}
# a_eq_zero = "0 1 -1 D A !D !A -D -A D+1 A+1 D-1 A-1 D+A D-A A-D D&A D|A".split()
a_eq_zero = ['0', '1', '-1', 'D', 'A', '!D', '!A', '-D', '-A', 'D+1', 'A+1', 'D-1', 'A-1', 'D+A', 'D-A', 'A-D', 'D&A', 'D|A']
# a_eq_one = "M !M -M M+1 M-1 D+M D-M M-D D&M D|M".split()
a_eq_one = ['M', '!M', '-M', 'M+1', 'M-1', 'D+M', 'D-M', 'M-D', 'D&M', 'D|M']

# file = input("Enter the file name: ")
if len(sys.argv) != 2:
    print("That is not the right format. Write the name of the program followed by the file name: '>python assembler.py xxx.asm'")
    quit()
    
file = sys.argv[1]
output_file = file.replace('.asm', '') + '.hack'

def main():

    try:
        fhand = open(file)
    except:
        print("Can not find that file!")
        quit()
    
    # Checks if the output file already exits if so delete it    
    if os.path.exists(output_file):
        os.remove(output_file)

    code = only_symbols(fhand)

    fhand.close()

   # print(code)

    label_to_memory_map = maps_label_to_memory_address(code)    

    pruned_code = replace_label_with_memory_address(code, label_to_memory_map)

    # prints_cleaned_code(pruned_code)

    # print(SYMBOLS_TABLE)
    symbol_to_machine(pruned_code)
    
    #outputs the symbols table in a file
    # count = 1
    # for symbol in SYMBOLS_TABLE:
    #     # print(count, instruction)
    #     # print('size:', len(instruction))
    #     n = ' = ' +  str(SYMBOLS_TABLE[symbol])
    #     with open('symbols.txt', 'a') as f:
    #         f.write(str (count) + ' ' + symbol + n +'\n')
    #     count +=1

    print('done')

def only_symbols(fhand):
    """
    return string list with all the code
    cleans the assembly file, deleting comments, empty lines, labels and white spaces
     
    """
    program_code = list()
    count = 0
    for line in fhand:
        line = line.strip()
        if len(line) < 1: continue
        if re.search('^//' , line): continue
        if re.search('^\(' , line):
            SYMBOLS_TABLE[line[1:].rstrip(')')] = count   #appends label to symbols_table
            continue

        code = line.split('//')[0].rstrip()
        code = code.replace(' ','')
        program_code.append(code)
        count += 1

    return(program_code)

def maps_label_to_memory_address(code):
    """
    Returns a dictionary that maps the labels to the corresponding memory address
    """
    labels = list()
    address_labels = dict()         # This list holds the entired program already cleaned
    count = 16
    
    for instruction in code:
        if instruction[0] != '@': continue
        if instruction[1][0].isdigit(): continue
        
        label = instruction[1:]

        if label in labels: continue

        labels.append(label)

        if label in SYMBOLS_TABLE:
            address_labels[label] = SYMBOLS_TABLE[label]
        else:   
            SYMBOLS_TABLE[label] = count
            address_labels[label] = count
            count = count + 1            

    return(address_labels)

def replace_label_with_memory_address(code, labels_map):
    """
    Return a list with all the labels changed by the corresponding address in memory.
    """
    for i in range(len(code)):
        if code[i][0] != '@' or code[i][1].isdigit(): continue
        label = code[i][1:]
        if label in labels_map:
            code[i] = code[i][0] + str(labels_map[label])
            # print(labels_map[label])
    # print(code)
    return (code)

def decimal_to_binary(num):
    """
    Accepts a decimal value string and return a sixting bit string
    """
    sixting_bit_binary = '0000000000000000'
    binary = bin(int(num))[2:]

    binary_instruction_length = len(binary)
    
    zeros = len(sixting_bit_binary) - binary_instruction_length

    binary = sixting_bit_binary[:zeros] + binary

    return binary

def c_instruction(instruction):
    """
    converts to the c-intruction to this format ['dest' 'comp' 'jump']
    pases it as instruction argument
    return the 16 bit binary code instruction in machine language
    """
    if '=' in instruction:
        instruction = instruction.split('=')

        if ';' not in instruction:
            instruction.append('null')
        else:
            instruction = instruction.split(';')
    elif ';' in instruction:
        instruction = instruction.split(';')
        instruction.insert(0, 'null')

    binary_code = translate_to_binary(instruction)
    return(binary_code)
 
def translate_to_binary(instruction_list):
    """
    helper to c_instruction function.
    inputs the c-instruction and return the binary code
    """
    _dest, _comp, _jump = instruction_list

    if _comp in a_eq_zero:
        a = '0'
    elif _comp in a_eq_one:
        a = '1'

    return('111' + a + comp[_comp] + dest[_dest] +jump[_jump])
    

def symbol_to_machine(code):
    """
    converts all the instructions to machine languaje    
    """
    for instruction in code:
        if instruction[0] == '@':
            b=decimal_to_binary(instruction[1:])
            
        else:
            b = c_instruction(instruction)

        write_to_file(b)

# def prints_cleaned_code(code):
#     """
#     Eventually this will be a write to file function

#     """
#     count = 1
#     for instruction in code:
#         # print(count, instruction)
#         # print('size:', len(instruction))
#         with open('debugfile.txt', 'a') as f:
#             f.write(str (count) + ' ' + instruction + '\n')
#         count +=1

#     # print(code)

def write_to_file(binary_code):
    # global output_file    
    # output_file = file.replace('.asm', '') + '.hack'

    with open(output_file, 'a') as f:
        f.write(binary_code + '\n')

main()