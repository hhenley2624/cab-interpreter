import re

def varmap(targetVar, state):
    if targetVar in state:
        return state[targetVar]
    elif "'" in targetVar:
        return targetVar.strip("'")
    else:
        raise ValueError("Error: Var not found")
    
state = dict()

# Function to compute the arithmetic operations
def compute(value):
    '''Initialize a dictionary with arithmetic operators as keys and the operations as values'''
    operators = {'==': 'equal to', 
                '+': 'add', 
                 '-': 'sub', 
                 '*': 'mul', 
                 '/': 'div', 
                 '%': 'mod', 
                 '>=': 'greater than or equal', 
                 '<=': 'less than or equal',
                 '>': 'greater than', 
                 '<': 'less than'}
    
    for operator in operators.keys():
        if operator in value:
            left_hand, right_hand = value.split(operator, 1)
            '''Recursively compute the left and right hand side expressions'''
            match operator:
                case '+':
                    return compute(left_hand) + compute(right_hand)
                case '-':
                    return compute(left_hand) - compute(right_hand)
                case '*':
                    return compute(left_hand) * compute(right_hand)
                case '/':
                    return compute(left_hand) / compute(right_hand)
                case '%':
                    return compute(left_hand) % compute(right_hand)
                case '>':
                    return compute(left_hand) > compute(right_hand)
                case '<':
                    return compute(left_hand) < compute(right_hand)
                case '==': 
                    return compute(left_hand) == compute(right_hand)
                case '>=':
                    return compute(left_hand) >= compute(right_hand)
                case '<=':
                    return compute(left_hand) <= compute(right_hand) 
    '''If the value is not one of the arithmetic expressions, try to convert it to an integer'''
    result = None
    
    '''If the value is a boolean, return that bool'''
    if isinstance(value, bool):
        return value
    
    try:
        result = float(value)
    except:
        '''If not convertible look it up in the state'''
        result = varmap(value, state)
    finally:
        return result

def if_else(expression, idx, program):
    '''pass the condition into the compute function to evaluate true or false'''
    condition = compute(expression)
    '''if condition is true a var to store the conditional block of code is created and a var to store the next index and the full program split'''
    if condition:
        conditional_program = ""
        next_idx = idx + 1
        full_program = program.splitlines()
        '''As long as there are lines remaining in the program after the current line the while loop continues'''
        while len(full_program) > next_idx:
            next_line = full_program[next_idx]
            if next_line.startswith("end") or next_line.startswith("else"):
                break
            '''If the next line is indented with four spaces it is part of the conditonal block and the indentation is stripped'''
            if next_line.startswith("    "):
                next_line = next_line[4:]
                '''Adds the next line if it is the first line and if not is added with a newline'''
                if len(conditional_program) < 1:
                    conditional_program += next_line
                else:
                    conditional_program += "\n" + next_line
            next_idx += 1
        executeProgram(conditional_program)
    else:
        conditional_program = ""
        next_idx = idx + 1
        full_program = program.splitlines()
        has_seen_else = False
        while len(full_program) > next_idx:
            next_line = full_program[next_idx]
            if next_line.startswith("end"):
                break
            if next_line.startswith("    ") and has_seen_else:
                next_line = next_line[4:]
                if len(conditional_program) < 1:
                    conditional_program += next_line
                else:
                    conditional_program += "\n" + next_line
            if next_line.startswith("else"):
                has_seen_else = True
            next_idx += 1
        executeProgram(conditional_program)

# Function to compute while loops        
def while_loops(expression, idx, program):
    condition = compute(expression)
    '''While the condtion is true the loop will continue to execute'''
    while condition:
        conditional_program = ""
        next_idx = idx + 1
        full_program = program.splitlines()
        while len(full_program) > next_idx:
            next_line = full_program[next_idx]
            if next_line.startswith("end") or next_line.startswith("else"):
                break
            if next_line.startswith("    "):
                next_line = next_line[4:]
                if len(conditional_program) < 1:
                    conditional_program += next_line.strip()
                else:
                    conditional_program += "\n" + next_line.strip()
            next_idx += 1  

        executeProgram(conditional_program)
        '''Re-evaluate the condition by calling the compute function at the end of the loop'''
        condition = compute(expression)

# Function to compute for loops
def for_loop(line, idx, program):
    '''Use RegEx to grab the variable, start value, and end value for my loop condition'''
    loop_var, start, end = re.search(r'FOR\s(.*?)\s*=\s*(.*?)\s*TO\s*(.*?)$', line).groups()
    
    start_val = int(start)
    end_val = int(end)

    for loop_val in range(start_val, end_val + 1):
        '''Update the variable in my state with the value after every iteration'''
        state[loop_var] = loop_val
   
        conditional_program = ""
        next_idx = idx + 1
        full_program = program.splitlines()
        while len(full_program) > next_idx:
            next_line = full_program[next_idx]
            if next_line.startswith("end") or next_line.startswith("else"):
                break
            if next_line.startswith("    "):
                next_line = next_line[4:]
                if len(conditional_program) < 1:
                    conditional_program += next_line
                else:
                    conditional_program += "\n" + next_line
            next_idx += 1

        executeProgram(conditional_program)
        
def create_function(idx,program):
    conditional_program = ""
    next_idx = idx + 1
    full_program = program.splitlines()
    while len(full_program) > next_idx:
        next_line = full_program[next_idx]
        if next_line.startswith("end") or next_line.startswith("else"):
            break
        if next_line.startswith("    "):
            next_line = next_line[4:]
            if len(conditional_program) < 1:
                conditional_program += next_line
            else:
                conditional_program += "\n" + next_line
        next_idx += 1

    executeProgram(conditional_program)

def executeProgram(program):
    '''Change the original loop to use enumerate to grab the index and the line'''
    for idx, line in enumerate(program.splitlines()):
        if line.startswith("    ") or line.startswith('end') or line.startswith('else'):
            continue
        
        instruction, expression = line.split(" ", 1)
        
        if instruction == "let":
            '''Implemented RegEx to grab the variable after assign and the value after the ='''
            var = re.search(r'let\s(.*?)=', line).group(1)
            val = re.search(r'\=(.*)', line).group(1)
            valPar = re.findall(r'\((.*?)\)', val)
            for exp in valPar:
                result = compute(exp)
                val = val.replace(f'({exp})',str(result))             
            '''store the var as the key and assign the value the result of the compute function with val passed as a param'''
            state[var] = compute(val)
        elif instruction == "sendit":
            try:
                val = varmap(expression, state)
                print(val)
            except:
                print("Error: Val not found")
        elif instruction == "bang":
            try:
                val = varmap(expression, state)
                print(val)
            except:
                print("Error: Val not found")
        elif instruction == "if":
            if_else(expression, idx, program)
        elif instruction == "while":
            while_loops(expression, idx, program) 
        elif instruction == "for":
            for_loop(line, idx, program)
        elif instruction == "clang":
            create_function(idx,program)
        else:
             print("Error! Instruction not found")
             
with open('/Users/harrisonhenley/Desktop/CS420/final_project/program_3.cab', 'r') as file:
    sampleProgram = file.read()
    
executeProgram(sampleProgram)
    

