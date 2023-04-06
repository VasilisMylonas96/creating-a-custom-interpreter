#Basilis Mylwnas 2777 cse42777
#Andreas Theofilopoulos 2701 cse42701

class Tokens(object):

    def __init__(self, type, value, line, col):
                self.type = type
                self.value = value
                self.line = line
                self.col = col

    def __str__(self):
        return '%s(%s) at starting line %s, col %s' % (self.type, self.value, self.line, self.col)









# Classes needed for the intermediate code
class Quad():
    def __init__(self, label, op, arg1, arg2, res):
        self.label = label
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.res = res

    def __str__(self):
        return '%s:\t%s, %s, %s, %s' % (self.label, self.op, self.arg1, self.arg2, self.res)

    def write_to_file(self):
        return '%s:\t%s, %s, %s, %s' % (self.label, self.op, self.arg1, self.arg2, self.res)

















#Classes needed for the symbol table
class Scope():
    def __init__(self, nestingLevel=0,enclosingScope=None):
        self.entities = list()
        self.nestingLevel = nestingLevel
        self.enclosingScope = enclosingScope
        self.tmp_offset = 12

    def add_entity(self, entity):
        self.entities.append(entity)

    def get_offset(self):
        retval = self.tmp_offset
        self.tmp_offset += 4
        return retval

    def __str__(self):
        return self.__repr__() + ': (' + self.nestingLevel + ', ' + self.enclosingScope.__repr__() + ')'

class Argument():
    def __init__(self, parMode, nextArg=None):
        self.parMode = parMode          # also the arg type
        self.nextArg = nextArg

    def set_next(self, nextArg):
        self.nextArg = nextArg

    def __str__(self):
        return self.__repr__() +': (' + self.parMode + ',\t'+ self.nextArg.__repr__() + ')'

class Entity():
    def __init__(self, name, etype):
        self.name = name
        self.etype = etype
        self.next = None

    def __str__(self):
        return self.etype +': ' + self.name

class Variable(Entity):
    def __init__(self, name, offset=-1):
        super().__init__(name, "VARIABLE")
        self.offset = offset

    def __str__(self):
        return super().__str__() + ', offset: ' + self.offset


class Function(Entity):
    def __init__(self, name, ret_type, startQuad=-1):
        super().__init__(name, "FUNCTION")
        self.ret_type = ret_type
        self.startQuad = startQuad
        self.args = list()
        self.framelength = -1

    def add_arg(self, arg):
        self.args.append(arg)

    def set_framel(self, framelength):
        self.framelength = framelength

    def set_startQuad(self, startQuad):
        self.startQuad = startQuad

    def __str__(self):
        return super().__str__() + ', retv: ' + self.ret_type + ', startquad: ' + self.startQuad + ', framelength: ' + self.framelength

class Parameter(Entity):
    def __init__(self, name, parMode, offset=-1):
        super().__init__(name, "PARAMETER")
        self.parMode = parMode
        self.offset = offset


    def __str__(self):
        return super().__str__() + ', mode: ' + self.parMode + ', offset: ' + self.offset


class TmpVar(Entity):
    def __init__(self, name, offset=-1):
        super().__init__(name, "TMPVAR")
        self.offset = offset

    def __str__(self):
        return super().__str__() + ', offset: ' + self.offset


















# all of the functions for the intermediate code


def nextquad():
    return nextlabel


def genquad(op, arg1, arg2, res):
    global nextlabel
    label= nextlabel
    nextlabel += 1
    genquad= Quad(label, op, arg1, arg2, res)
    quadcode.append(genquad)


def newtemp():
    global tmp_vars, tmpvar
    tmp= 'T_' + str(tmpvar)
    tmp_vars[tmp] = None
    offset = scopes[-1].get_offset()
    scopes[-1].add_entity(TmpVar(tmp, offset))
    tmpvar += 1
    return tmp

def merge(list1, list2):
    merged_list = list1 + list2
    return merged_list

def emptylist():
    return list()


def backpatch(alist,res):
    global quadcode
    for q in quadcode:
        if q.label in alist:
            q.res = res

def makelist(label):
    newlist= list()
    newlist.append(label)
    return newlist

















# Here the intermediate code get written to file
def interm_to_file():
    global create_int
    for q in quadcode:
        create_int.write(q.write_to_file() + '\n')
    create_int.close()






# Finds all the variable declarations
def var_decls(quad):
    vars_dec = dict()
    index = quadcode.index(quad) + 1
    quad = quadcode[index]
    while quad.op!= 'end_block':
        if quad.op not in ('print','call','jump','begin_block') and quad.arg2 not in ('CV','REF','RET'):
            if quad.arg1!='_':
                vars_dec[quad.arg1] = 'int'
            if quad.arg2!='_':
                vars_dec[quad.arg2] = 'int'
            if quad.res!='_':
                vars_dec[quad.res] = 'int'
        index += 1
        quad = quadcode[index]

    for key in list(vars_dec.keys()):
        if isinstance(key, int):
            del vars_dec[key]
    return vars_dec

















# The function to take these variables and write them in c code
def trans_decls(vars_dec):
    res = '\n\t int '
    for var in vars_dec:
        res += var + ', '
    return res[:-2] + ';'

# The rest c code function generation
def translate_to_c(quad):
    addlabel = True
    if quad.op =='begin_block':
        addlabel =False
        if quad.arg1 == NameOfProgram:
            res ='int main(void)\n{'
        vars=var_decls(quad)
        res += trans_decls(vars) +'\n'
        res += 'L_' + str(quad.label) + ':'
    elif quad.op =='end_block':
        addlabel = False
        res ='L_' + str(quad.label) + ': {}\n' + '}\n'
    elif quad.op in ('=', '<>', '<', '>', '<=', '>='):
        op = quad.op
        if op =='=':
            op ='=='
        elif op =='<>':
            op ='!='
        res ='if (' + str(quad.arg1) + ' ' + op + ' ' + str(quad.arg2) + ') goto L_' + str(quad.res) + ';'
    elif quad.op in ('+', '-', '*', '/'):
        res =quad.res + ' = ' + str(quad.arg1) + ' ' + quad.op + ' ' + str(quad.arg2) + ';'
    elif quad.op == 'out':
        res ='printf("%d\\n", ' + str(quad.arg1) + ');'
    elif quad.op ==':=':
        res =quad.res + ' = ' + str(quad.arg1) + ';'
    elif quad.op =='retv':
        res ='return ' + str(quad.arg1) + ';'
    elif quad.op =='jump':
        res ='goto L_' + str(quad.res) + ';'
    elif quad.op == 'halt':
        res ='return 0;'
    else:
        return None
    if addlabel ==True:
        res ='L_' + str(quad.label) + ': ' + res
    return res



# Save the c code to the file with the  #include declaration (ready to run)
def save_code_file():
    create_c.write('#include <stdio.h>\n')
    for quad in quadcode:
        temp = translate_to_c(quad)
        if temp != None:
            create_c.write(temp + '\n')
    create_c.close()























# Functions needed for the symbol table

# Add new scope when we start the translation of a function
def add_new_scope():
    enclosingScope = scopes[-1]
    currScope = Scope(enclosingScope.nestingLevel + 1, enclosingScope)
    scopes.append(currScope)

# Functions for adding & updating Entity

def add_function(name):
    nestingLevel = scopes[-1].enclosingScope.nestingLevel
    if unique_entity(name, "FUNCTION", nestingLevel):
        if ins_func[-1] == True:
            ret_type = "int"

        else:
            ret_type = "void"
        scopes[-2].add_entity(Function(name, ret_type))
    else:
        ER(token.line, token.col, 'There is another definition of \'%s\'' % name)


def upd_str_quad(name): #Update the start quad label of a function entity
    startQuad = nextquad()
    if name == NameOfProgram:
        return startQuad
    func_ent = search_ent(name, "FUNCTION")[0]
    func_ent.set_startQuad(startQuad)
    return startQuad



def upd_frm(name, framelength): # Update the framelength of a function entity.
    global main_framelength
    if name == NameOfProgram:
        main_framelength = framelength
        return
    func_ent = search_ent(name, "FUNCTION")[0]
    func_ent.set_framel(framelength)

# The rest add new parameters, variables , arguments to a function entity

def add_param(name, parMode):
    nestingLevel = scopes[-1].nestingLevel
    offset = scopes[-1].get_offset()
    if unique_entity(name, "PARAMETER", nestingLevel):
        scopes[-1].add_entity(Parameter(name, parMode, offset))
    else:
        ER(token.line, token.col, 'There is another definition of \'%s\'' % name)




def add_var(name):
    nestingLevel = scopes[-1].nestingLevel
    offset = scopes[-1].get_offset()
    if not var_is_param(name, nestingLevel) and unique_entity(name, "VARIABLE", nestingLevel):
        scopes[-1].add_entity(Variable(name, offset))
    else:
        ER(token.line, token.col, 'There is another definition of \'%s\' or \'%s\' already exists as a PARAM' % name)



def add_arg(func_name, parMode):
    if parMode == 'inout':
        new_arg = Argument('REF')
    else:
        new_arg = Argument('CV')
    func_ent = search_ent(func_name, "FUNCTION")[0]
    if func_ent == None:
        ER(token.line, token.col, 'No definition of \'%s\' found' % func_name)
    if func_ent.args != list():
        func_ent.args[-1].set_next(new_arg)
    func_ent.add_arg(new_arg)


# Search for an entity with specific (name, etype).
def search_ent(name, etype):
    if scopes == list():
        return
    tmp_scope = scopes[-1]
    while tmp_scope != None:
        for entity in tmp_scope.entities:
            if entity.name == name and entity.etype == etype:
                return entity, tmp_scope.nestingLevel
        tmp_scope = tmp_scope.enclosingScope


# Ability to search entity by the given name
def search_ent_based_name(name):
    if scopes == list():
        return
    tmp_scope = scopes[-1]
    while tmp_scope != None:
        for entity in tmp_scope.entities:
            if entity.name == name:
                return entity, tmp_scope.nestingLevel
        tmp_scope = tmp_scope.enclosingScope

# Function to assure that there is NOT a redefinition of an entity with (name, etype) at nested level
def unique_entity(name, etype, nestingLevel):
    if scopes[-1].nestingLevel < nestingLevel:
        return
    scope = scopes[nestingLevel]
    list_len = len(scope.entities)
    for i in range(list_len):
        for j in range(list_len):
            ent1 = scope.entities[i]
            ent2 = scope.entities[j]
            if ent1.name == ent2.name and ent1.etype == ent2.etype and ent1.name == name and ent1.etype == etype:
                return False
    return True

# Check if a variable entity already exists as a parameter

def var_is_param(name, nestingLevel):
    if scopes[-1].nestingLevel < nestingLevel:
        return
    scope = scopes[nestingLevel]
    list_len = len(scope.entities)
    for i in range(list_len):
        ent = scope.entities[i]
        if ent.name == name and ent.etype == "PARAMETER":
            return True
    return False





















# Functions needed for create_final code

#Puts the address of the non-local variable in $t0
def gnvlcode(v):
    try:
        var_entity, nesting_level  = search_ent_based_name(v)
    except:
        print('Undeclared variable:', v)
        exit(1)
    if var_entity.etype == 'FUNCTION':  #for non-local vars
        print('Undeclared variable:', v)
        exit(1)
    curr_nesting = scopes[-1].nestingLevel          #store current nesting of non-local var
    create_final.write('\t lw\t $t0, -4($sp)\n')        #parent stack
    lev_dif = curr_nesting - nesting_level - 1      #calculate the level difference (should be positive)
    while  lev_dif > 0:
        create_final.write('\t lw\t $t0, -4($t0)\n')    #ancestor's stack (var)
        lev_dif -= 1                                        #until all levels are consumed
    create_final.write('\t addi\t $t0, $t0, -%d\n' % var_entity.offset) #update the var addr

#Stores data from a register (r) to the memory (v)
def storerv(r, v):
    global nestng_level
    try:
        var_entity, nestng_level = search_ent_based_name(v)
    except:
        print('Undeclared variable:', v)
        exit(1)
    curr_nesting  = scopes[-1].nestingLevel
    if var_entity.etype == 'VARIABLE' and nestng_level == 0:    # case 1 : global var
        create_final.write('\t sw\t $t%s, -%d($s0)\n' % (r, var_entity.offset))
    elif (var_entity.etype == 'VARIABLE' and nestng_level == curr_nesting) or (var_entity.etype =='PARAMETER' and var_entity.parMode =='in' and nestng_level ==curr_nesting) or (var_entity.etype =='TMPVAR'):  # case 2 : (a) local var, eq nesting  (b) par cv, eq nesting (c) tmp var
        create_final.write('\t sw\t $t%s, -%d($sp)\n' % (r, var_entity.offset))
    elif var_entity.etype =='PARAMETER' and var_entity.parMode =='inout' and nestng_level==curr_nesting:  # case 3 : par ref, eq nesting
        create_final.write('\t lw\t $t0, -%d($sp)\n' % var_entity.offset)
        create_final.write('\t sw\t $t%s, 0($t0)\n' % r)
    elif (var_entity.etype == 'VARIABLE' and nestng_level < curr_nesting) or (var_entity.etype == 'PARAMETER' and var_entity.parMode == 'in' and nestng_level < curr_nesting): # case 4 : (a) local var, < curr nesting (b) : par cv, < curr nesting
        gnvlcode(v)
        create_final.write('\t sw\t $t%s, 0($t0)\n' % r)
    elif var_entity.etype == 'PARAMETER' and var_entity.parMode == 'inout' and nestng_level < curr_nesting: # case 5 : par ref, < curr nesting
        gnvlcode(v)
        create_final.write('\t lw\t $t0, 0(%t0)\n')
        create_final.write('\t sw\t $t%s, 0($t0)\n' % r)

# loads data from mem or an immediate (v) to a register (r)
def loadvr(v, r):
    if str(v).isdigit():    #case 1 : immediate
        create_final.write('\t li\t $t%s, %d\n' % (r, v))
    else:
        try:
            var_entity, nesting_level = search_ent_based_name(v)
        except:
            print('Undeclared variable:', v)
            exit(1)
        curr_nesting  = scopes[-1].nestingLevel
        if var_entity.etype == 'VARIABLE' and nesting_level == 0: # case 2 : global var
            create_final.write('\t lw\t $t%s, -%d($s0)\n' % (r, var_entity.offset))
        elif (var_entity.etype =='VARIABLE' and nesting_level == curr_nesting) or (var_entity.etype =='PARAMETER' and var_entity.parMode =='in' and nesting_level ==curr_nesting) or (var_entity.etype =='TMPVAR'):  # case 3 : (a) local var, eq nesting  (b) par cv, eq nesting (c) tmp var
            create_final.write('\t lw\t $t%s, -%d($sp)\n' % (r, var_entity.offset))
        elif var_entity.etype == 'PARAMETER' and var_entity.parMode == 'inout'  and nesting_level == curr_nesting:  # case 4 : par ref, eq nesting
            create_final.write('\t lw\t $t0, -%d($sp)\n' % var_entity.offset)
            create_final.write('\t lw\t $t%s, 0($t0)\n' % r)
        elif (var_entity.etype == 'VARIABLE' and nestng_level < curr_nesting) or (var_entity.etype == 'PARAMETER' and var_entity.parMode == 'in' and nesting_level < curr_nesting):  # case 5 : (a) local var, < curr nesting (b) : par cv, < curr nesting
            gnvlcode(v)
            create_final.write('\t lw\t $t%s, 0($t0)\n' % r)
        elif var_entity.etype == 'PARAMETER' and var_entity.parMode == 'inout' and nesting_level < curr_nesting:    # case 6 : par ref, < curr nesting
            gnvlcode(v)
            create_final.write('\t lw\t $t0, 0(%t0)\n')
            create_final.write('\t lw\t $t%s, 0($t0)\n' % r)



# Generates the assembly code for quad
# block_name is the currently translated block.
def translate_to_asm(quad, block_name):
    global pars
    create_final.write('\nL_' + str(quad.label) + ':\n')
    relop = ('<','<=','>','>=','=','<>')
    branch = ('blt','ble','bgt','bge','beq','bne')
    c_ops = ('+','-','*','/')
    asm_ops = ('add','sub','mul','div')

    if quad.op == 'jump':
        create_final.write('\t j\t L_%s\n' % quad.res)
    elif quad.op in relop:
        relop = branch[relop.index(quad.op)]
        loadvr(quad.arg1, '1')
        loadvr(quad.arg2, '2')
        create_final.write('\t %s\t $t1, $t2, L_%s\n' % (relop, quad.res))
    elif quad.op == ':=':
        loadvr(quad.arg1, '1')
        storerv('1', quad.res)
    elif quad.op in c_ops:
        op = asm_ops[c_ops.index(quad.op)]
        loadvr(quad.arg1, '1')
        loadvr(quad.arg2, '2')
        create_final.write('\t %s\t $t1, $t1, $t2\n' % op)
        storerv('1', quad.res)
    elif quad.op == 'out':
        create_final.write('\t li\t $v0, 1\n')
        create_final.write('\t li\t $a0, %s\n' % quad.arg1)
        create_final.write('\t syscall\n')
    elif quad.op == 'in':
        create_final.write('\t li\t $v0, 5\n')
        create_final.write('\t syscall\n')
    elif quad.op == 'retv':
        loadvr(quad.arg1, '1')
        create_final.write('\t lw\t $t0, -8($sp)\n')
        create_final.write('\t sw\t $t1, 0($t0)\n')
    elif quad.op == 'halt':
        create_final.write('\t li\t $v0, 10\n')
        create_final.write('\t syscall\n')
    elif quad.op == 'par':
        if block_name == program_name: # determine caller
            caller_level = 0
            framelength = main_framelength
        else:
            caller_entity, caller_level = search_ent(block_name, 'FUNCTION')
            framelength = caller_entity.framelength
        if pars == []: # before the first par update the stack's pointer
            create_final.write('\t addi\t $fp, $sp, %d\n' % framelength)
        pars.append(quad)
        par_offset = 12 + 4 * pars.index(quad) # the increasing position of the par
        if quad.arg2 == 'CV':
            loadvr(quad.arg1, '0')
            create_final.write('\t sw\t $t0, -%d($fp)\n' % par_offset)
        elif quad.arg2 == 'REF':
            try:
                var_entity, var_level = search_ent_based_name(quad.arg1)
            except:
                print('Undeclared variable:', quad.arg1)
                exit(1)
            if caller_level == var_level:
                # if eq nesting level, par is local var in caller or par cv
                if var_entity.etype =='VARIABLE' or (var_entity.etype =='PARAMETER' and var_entity.parMode =='in'):
                    create_final.write('\t addi\t $t0, $sp, -%d\n' % var_entity.offset)
                    create_final.write('\t sw\t $t0, -%d($fp)\n' % par_offset)
                # else par ref
                elif var_entity.etype =='PARAMETER' and var_entity.parMode =='inout':
                    create_final.write('\t lw\t $t0, -%d($sp)\n' % var_entity.offset)
                    create_final.write('\t sw\t $t0, -%d($fp)\n' % par_offset)
            else:
                # same cases when not eq
                if var_entity.etype =='VARIABLE' or (var_entity.etype =='PARAMETER' and var_entity.parMode =='in'):
                    gnvlcode(quad.arg1)
                    create_final.write('\t sw\t $t0, -%d($fp)\n' % par_offset)
                elif var_entity.etype =='PARAMETER' and var_entity.parMode =='inout':
                    gnvlcode(quad.arg1)
                    create_final.write('\t lw\t $t0, ($t0)\n')
                    create_final.write('\t sw\t $t0, -%d($fp)\n' % par_offset)
        elif quad.arg2 == 'RET':
            try:
                var_entity, var_level = search_ent_based_name(quad.arg1)
            except:
                print('Undeclared variable:', quad.arg1)
                exit(1)
            create_final.write('\t addi\t $t0, $sp, -%d\n' % var_entity.offset)
            create_final.write('\t sw\t $t0, -8($fp)\n')
    elif quad.op == 'call':
        if block_name == program_name:
            caller_level = 0
            framelength = main_framelength
        else:
            caller_entity, caller_level = search_ent(block_name, 'FUNCTION')
            framelength = caller_entity.framelength
        try:
            callee_entity, callee_level = search_ent(quad.arg1, 'FUNCTION')
        except:
            print('Undefined function or procedure:', quad.arg1)
            exit(1)
        if caller_level == callee_level: # in this case caller and callee have the same parent
            create_final.write('\t lw\t $t0, -4($sp)\n')
            create_final.write('\t sw\t $t0, -4($fp)\n')
        else: # else caller is the parent of callee
            create_final.write('\t sw\t $sp, -4($fp)\n')
        # update stack pointer to callee
        create_final.write('\t addi\t $sp, $sp, %d\n' % framelength)
        # call jal (jump and allocate)
        create_final.write('\t jal\t L_%s\n' % str(callee_entity.startQuad))
        # then return and update stack pointer to caller
        create_final.write('\t addi\t $sp, $sp, -%d\n' % framelength)
    elif quad.op == 'begin_block':
        if block_name == NameOfProgram:
            create_final.write('\t sw\t $ra, 0($sp)\n')
            #create_final.seek(0,0) # write to the start
            create_final.write('\t j\t L_%d # MAIN\n' % quad.label) # jump to main program
            create_final.write('\t addi\t $sp, $sp, %d\n' % main_framelength)
            create_final.write('\t move\t $s0, $sp\n')
    elif quad.op == 'end_block':
        if block_name == NameOfProgram:
            create_final.write('\t j\t L_%d\n' % halt)
        else:
            create_final.write('\t lw\t $ra, 0($sp)\n')
            create_final.write('\t jr\t $ra\n')





scopes = list()         # a list that contains the scopes
#the class for all the symbols and reserved words
class Stokens(object):
    #TOKEN DEFINTIONS
    idtk            = 0
    numbertk = constk = 1
    leftpartk       = '('
    rightpartk      = ')'
    leftbrtk        = '['
    rightbrtk       = ']'
    commatk         = ','
    colontk         = ':'
    semicolontk     = ';'
    lttk            = '<'
    gttk            = '>'
    ltetk           = '<='
    gtetk           = '>='
    eqtk            = '='
    neqtk           = '<>'
    assigntk        = ':='
    plustk          = '+'
    minustk         = '-'
    multk           = '*'
    divtk           = '/'
    defaulttk       ='default'
    andtk           = 'and'
    nottk           = 'not'
    ortk            = 'or'
    declaretk       = 'declare'
    iftk            = 'if'
    thentk          = 'then'
    elsetk          = 'else'
    endiftk         = 'endif'
    exittk          = 'exit'
    proceduretk     = 'procedure'
    endproceduretk  = 'endprocedure'
    functiontk      = 'function'
    endincasetk     = 'endincase'
    endfunctiontk   = 'endfunction'
    printtk         = 'print'
    inputtk         = 'input'
    calltk          = 'call'
    intk            = 'in'
    inouttk         = 'inout'
    inandouttk      = 'inandout'
    programtk       = 'program'
    endprogramtk    = 'endprogram'
    returntk        = 'return'
    whiletk         = 'while'
    loopstattk      = 'loop'
    incasetk        = 'incase'
    loopendtk       = 'endloop'
    enddefaulttk    = 'enddefault'
    endwhiletk      = 'endwhile'
    dowhiletk       = 'do'
    enddowhiletk    = 'enddowhile'
    endrepeattk     = 'endrepeat'
    endwhiletk      = 'endwhile'
    switchtk        = 'switch'
    endswitchtk     = 'endswitch'
    casetk          = 'case'
    forcasetk       = 'forcase'
    whentk          = 'when'
    endforcasetk    = 'endforcase'
    falsetk         = 'false'
    truetk          = 'true'
    EOF             = ''
# A simple function to print the error messages   (Line, Column, Error Message)
def ER(line, col, msg):
    print('\nERROR at line: ' + str(line),' col: ' + str(col),' msg: ' + str(msg) + '\n')
    exit(1)

# parser initiates here
def parser():
    global token
    token=lex()
    program()
    if token.type != Stokens.EOF:
        ER(token.line, token.col, 'Expected \'EOF\', instead found \'%s\'' % token.value)
    interm_to_file()
    # don't check to translate functions or procedure into c code
    if proc_func == False:
        save_code_file()
def program():
    global token ,NameOfProgram
    if token.type==Stokens.programtk:
        token=lex()
        if token.type==Stokens.idtk:
            NameOfProgram=token.value
            name=token.value
            token=lex()
            scopes.append(Scope())
            while token.type!=Stokens.endprogramtk:
                block(name)
            if token.type==Stokens.endprogramtk:
                token=lex()
            else:
                ER(token.line,token.col, 'Keyword \'endprogram\' expected, instead found \'%s\'' % token.value)
        else:
            ER(token.line, token.col, 'Program name expected, instead found \'%s\'' % token.value)
    else:
        ER(token.line, token.col, 'Keyword \'program\' expected, instead found \'%s\'' % token.value)

def block(name):
    global token, halt, scopes, NameOfProgram
    declarations()
    subprograms()
    # Classes needed for the intermediate code
    block_startQuad = upd_str_quad(name)
    genquad('begin_block', name, '_', '_')
    statements()
    if name == NameOfProgram:
        halt = nextquad()
        genquad('halt', '_', '_', '_')
    genquad('end_block', name, '_', '_')
    upd_frm(name, scopes[-1].tmp_offset)
    for quad in quadcode[block_startQuad:]:
        translate_to_asm(quad, name)
    scopes.pop()
  
def declarations():
    global token
    while token.type==Stokens.declaretk:#while we have declarations, stay here
        token=lex()
        varlist()
        if token.type==Stokens.semicolontk:#declare ends with ; 
            token=lex()
        else:
            ER(token.line, token.col, 'Keyword \'enddeclare\' expected, instead found \'%s\'' % token.value)

def varlist():
    global token
    if token.type==Stokens.idtk: #if the token type is id, procceed
        add_var(token.value)
        token=lex()
        while token.type==Stokens.commatk: #while the token type is , continue #if ; is found then stops 
            token=lex()
            if token.type==Stokens.idtk: #We need to have id here or else it's invalid and we print a message accordingly 
                add_var(token.value)
                token=lex()
            else:
                ER(token.line, token.col, 'Expected variable declaration instead found \'%s\'' % token.value)


def subprograms():
    global token,proc_func, ret_st, ins_func
    while token.type==Stokens.functiontk:
        ret_st.append(False)
        ins_func.append(False)
        proc_func = True
        ins_func[-1] = True
        token=lex()
        func()
        if ins_func.pop() == False:
            ret_st.pop()
        

def func():
    global token
    add_new_scope()
    if token.type==Stokens.idtk:
        name = token.value
        token=lex()
        add_function(name)
        if token.type==Stokens.leftpartk:
            while token.type!=Stokens.endfunctiontk:
                funcbody(name)
        else:
            ER(token.line, token.col, 'Expected \'(\' instead found \'%s\'' % token.value)
        if  token.type==Stokens.endfunctiontk:
            token=lex()
        else:
            ER(token.line, token.col,'Keyword \'endfunction\' expected, instead found \'%s\'' % token.value)
    else: ER(token.line, token.col, 'Function name expected instead found \'%s\'' % token.value)


def funcbody(name):#This is the loop where it always enters block until one of the 3 blocks does not exist
    formalpars(name)
    block(name)
    
def formalpars(name):
    global token
    if token.type==Stokens.leftpartk:
        token=lex()
        if token.type==Stokens.intk or token.type==Stokens.inouttk or token.type==Stokens.inandouttk:
            formalparlist(name)        
        if token.type==Stokens.rightpartk:
            token=lex()
        else:
            ER(token.line, token.col, 'Expected \')\' instead found \'%s\'' % token.value)
    
def formalparlist(name):
    global token
    if token.type==Stokens.intk or token.type==Stokens.inouttk or token.type==Stokens.inandouttk:
        formalparitem(name)
    while token.type==Stokens.commatk:
        token=lex()
        formalparitem(name)

def formalparitem(name):
    global token
    if token.type==Stokens.intk or token.type==Stokens.inouttk or token.type==Stokens.inandouttk:
        parMode=token.value
        token=lex()
        if token.type==Stokens.idtk:
            pname = token.value
            add_arg(name, parMode)
            add_param(pname, parMode)
            token=lex()
        else:
             ER(token.line, token.col, 'Expected formal parameter declaration instead found \'%s\'' % token.value)
    
    else:
        ER(token.line, token.col, 'Expected type of parameter instead found \'%s\'' % token.value)

    
    
    
def statements():
    global token
    statement()
    while token.type==Stokens.semicolontk:
        token=lex()
        statement()



def statement():
    global token , ret_st
    if token.type==Stokens.idtk:
        assign_to = token.value
        token=lex()
        assignment_stat(assign_to)
    elif token.type==Stokens.iftk:
        token=lex()
        if_stat()
    elif token.type==Stokens.whiletk:
        token=lex()
        while_stat()
    elif token.type==Stokens.dowhiletk:
        token=lex()
        do_while_stat()
    elif token.type==Stokens.loopstattk:
        token=lex()
        loop_stat()   
    elif token.type==Stokens.exittk:
        mk = makelist(nextquad())
        genquad('jump', '_', '_', '_')
        token=lex()
    elif token.type==Stokens.forcasetk:
        token=lex()
        forcase_stat()
    elif token.type==Stokens.incasetk:
        token=lex()
        incase_stat()
    elif token.type==Stokens.returntk:
        if ins_func[-1] == True:
            ret_st[-1] = True
        else:
            ER(token.line, token.col, '\'return\' keyword must be inside function definition')
        token=lex()
        exp = expression()
        genquad('retv', exp, '_', '_')
        #we don't need return_stat() definition
    elif token.type==Stokens.inputtk:
        token=lex()
        input_stat()
    elif token.type==Stokens.printtk:
        token=lex()
        exp=expression()
        genquad('out', exp, '_', '_')
        #we don't need print_stat() definition


def assignment_stat(assing_to):
    global token
    if token.type == Stokens.assigntk:
        token=lex()
        exp = expression()
        genquad(':=', exp, '_', assing_to)
        if token.type == Stokens.leftpartk:
            token=lex()
            if token.type == Stokens.intk or token.type == Stokens.inouttk or token.type == Stokens.inandouttk:
                token=lex()
                while token.type == Stokens.commatk:
                    token=lex()
                    if token.type == Stokens.intk or token.type == Stokens.inouttk or token.type == Stokens.inandouttk:
                        token=lex()
                    else:
                        ER(token.line, token.col,'Parameter type expected instead found \'%s\'' % token.value)
            else:
                ER(token.line, token.col,'Parameter type expected instead found \'%s\'' % token.value)
            if  token.type==Stokens.rightpartk:
                token=lex()
            else:
                ER(token.line, token.col,'\')\' expected instead found \'%s\'' % token.value)
        if token.type == Stokens.intk or token.type == Stokens.inouttk or token.type == Stokens.inandouttk:
            ER(token.line, token.col,'\'( ;\' expected instead found \'%s\'' % token.value)
                
                        
    else:
        ER(token.line, token.col,' \':=\' operator expected instead found \'%s\'' % token.value)


def expression():
    op_s =optional_sign()
    t1 =term()
    if op_s != None:
        ntmp = newtemp()
        genquad('-', 0, t1, ntmp)
        t1 = ntmp
    while token.type==Stokens.plustk or token.type==Stokens.minustk:
        op = add_oper()
        t2 = term()
        tvar = newtemp()
        genquad(op, t1, t2, tvar)
        t1 = tvar
    return t1

def optional_sign():
    if token.type==Stokens.minustk or token.type==Stokens.plustk:
        return add_oper()
    
    
def term():
    f1 =factor()
    while token.type==Stokens.multk or token.type==Stokens.divtk:
        op = mul_oper()
        f2 = factor()
        tvar = newtemp()
        genquad(op, f1, f2, tvar)
        f1 = tvar
    return f1


def add_oper():
    global token
    op = token.value
    if token.type==Stokens.plustk or token.type==Stokens.minustk:
        token=lex()
        return op
    else:
        ER(token.line, token.col,'\'+\' or \'-\' operation expected instead found \'%s\'' % token.value)

def mul_oper():
    global token
    op = token.value
    if token.type==Stokens.multk or token.type==Stokens.divtk:
        token=lex()
        return op
    else:
        ER(token.line, token.col, '\'*\' or \'/\' operation expected instead found \'%s\'' % token.value)



def factor():
    global token
    if token.type==Stokens.numbertk :
        res = const()
    elif token.type==Stokens.idtk:
        res = token.value
        token=lex()
        tail_id = idtail()
        if tail_id != None:
            funcres = newtemp()
            genquad('par', funcres, 'RET', '_')
            try:
                func_ent, func_level = search_ent_based_name(res)
            except:
                ER(token.line, token.col, 'Undefined function \'%s\'' % res)
            genquad('call', res, '_', '_')
            res = funcres
    elif token.type==Stokens.leftpartk:
        token=lex()
        res =expression()
        if token.type==Stokens.rightpartk:
            token=lex()
        else :
            ER(token.line, token.col,'\')\' expected instead found \'%s\'' % token.value)
    else :
        ER(token.line, token.col,'Factor expected instead found \'%s\'' % token.value)
    return res


def const():
    global token
    if token.type == Stokens.plustk or token.type == Stokens.minustk:
        sign = token.value
        token = lex()
    else:
        sign = '+'
    if token.type == Stokens.numbertk:
        res = int(''.join((sign, token.value)))
        if res < -32768 or res > 32767:
            ER( token.line, token.col, 'Number constants should be between -32768 and 32767')
    else:
        ER( token.line, token.colon, 'Expected number constant, instead found \'%s\'' % token.value)
    token= lex()
    return res

def idtail():
    if token.type==Stokens.leftpartk:
        return actualpars()

def actualpars():
    global token
    if token.type==Stokens.leftpartk:
        token=lex()
        actualparlist()
        if token.type==Stokens.rightpartk:
            token=lex()
            return True
        else:
            ER(token.line, token.col,'\')\' expected instead found \'%s\'' % token.value)
    else:
        ER(token.line, token.col,'\'(\' expected instead found \'%s\'' % token.value)


def actualparlist():
    global token
    if token.type == Stokens.intk or token.type == Stokens.inouttk or token.type == Stokens.inandouttk:
        actualparitem()
        while token.type==Stokens.commatk:
            token=lex()
            actualparitem()


def actualparitem():
    global token
    if token.type==Stokens.intk:
        token=lex()
        exp = expression()
        genquad('par', exp, 'CV', '_')
    elif token.type==Stokens.inouttk or token.type==Stokens.inandouttk:
        token=lex()
        par_id = token.value
        if token.type==Stokens.idtk:
            token=lex()
            genquad('par', par_id, 'REF', '_')
        else:
            ER(token.line, token.col,'Variable identifier expected instead found \'%s\'' % token.value)
    else:
        ER(token.line, token.col,'Parameter type expected instead found \'%s\'' % token.value)


def if_stat():
    global token
    if token.type==Stokens.leftpartk:  
        token=lex()
        (b_true, b_false) = condition()
        if token.type==Stokens.rightpartk:
            token=lex()
            if token.type==Stokens.thentk:
                token=lex()
                backpatch(b_true, nextquad())
                statements()
                iflist = makelist(nextquad())
                genquad('jump', '_', '_', '_')
                backpatch(b_false, nextquad())
                elsepart()
                backpatch(iflist, nextquad())
                if token.type==Stokens.endiftk:
                    token=lex()
                else: ER(token.line, token.col,'Keyword \'endif\' expected instead found \'%s\'' % token.value)
            else: ER(token.line, token.col,'Keyword \'then\' expected instead found \'%s\'' % token.value)
        else:
            ER(token.line, token.col,'Keyword \')\' expected instead found \'%s\'' % token.value)
    else:
        ER(token.line, token.col,'Keyword \'(\' expected instead found \'%s\'' % token.value)
    
    

def condition():
    global token
    (b_true, b_false) = (q1_true, q1_false) = boolterm()
    while token.type==Stokens.ortk:
        backpatch(b_false, nextquad())
        token=lex()
        (q2_true, q2_false) = boolterm()
        b_true  = merge(b_true, q2_true)
        b_false = q2_false
    return (b_true, b_false)

def boolterm():
    global token
    (q_true, q_false) = (r1_true, r1_false) = boolfactor()
    while token.type==Stokens.andtk:
        backpatch(q_true, nextquad())
        token=lex()
        (r2_true, r2_false) = boolfactor()
        q_false = merge(q_false, r2_false)
        q_true  = r2_true
    return (q_true, q_false)
   
def boolfactor():
    global token
    if token.type==Stokens.nottk:
        token=lex()
        if token.type==Stokens.leftbrtk:
            token=lex()
            res=condition()
            res=res[::-1]
            if token.type==Stokens.rightbrtk:
                token=lex()
            else:
                ER(token.line, token.col,'\']\' expected instead found \'%s\'' % token.value)
        else: ER(token.line, token.col,'\'[\' expected instead found \'%s\'' % token.value)
    elif token.type==Stokens.leftbrtk:
        token=lex()
        res =condition()
        if token.type==Stokens.rightbrtk:
            token=lex()
        else:
            ER(token.line, token.col,'\']\' expected instead found \'%s\'' % token.value)
    else:
        exp1 = expression()
        relop = relation_oper()
        exp2 = expression()
        r_true = makelist(nextquad())
        genquad(relop, exp1, exp2, '_')
        r_false = makelist(nextquad())
        genquad('jump', '_', '_', '_')
        res = (r_true, r_false)
    return res
     
     
def relation_oper():
    global token
    if token.type==Stokens.eqtk or token.type==Stokens.lttk or token.type==Stokens.gttk:
        op = token.value
        if token.type==Stokens.eqtk:
            token=lex()
            return op
            if token.type==Stokens.eqtk or token.type==Stokens.lttk or token.type==Stokens.gttk:
                ER(token.line, token.col,'Relational operation expected instead found \'%s\'' % token.value)
        
        elif token.type==Stokens.lttk:
            token=lex()
            if token.type==Stokens.eqtk or token.type==Stokens.gttk:
                op += token.value
                token=lex()
            elif token.type==Stokens.lttk:
                ER(token.line, token.col,'Relational operation expected instead found \'%s\'' % token.value)       
        elif token.type==Stokens.gttk:
            token=lex()
            if token.type==Stokens.eqtk:
                op += token.value
                token=lex()
            elif token.type==Stokens.gttk or token.type==Stokens.lttk:
                ER(token.line, token.col,'Relational operation expected instead found \'%s\'' % token.value)      
    else:
        ER(token.line, token.col,'Relational operation expected instead found \'%s\'' % token.value)

def elsepart():
    global token
    if token.type==Stokens.elsetk:
        token=lex()
        statements()

def while_stat():
    global token
    if token.type==Stokens.leftpartk:
        token=lex()
        b_quad = nextquad()
        (b_true, b_false) = condition()
        backpatch(b_true, nextquad())
        if token.type==Stokens.rightpartk:
            token=lex()
            statements()
            genquad('jump', '_', '_', b_quad)
            backpatch(b_false, nextquad())
        else:
            ER(token.line, token.col,'\')\' expected instead found \'%s\'' % token.value)
    else:
        
        ER(token.line, token.col,'\'(\' expected instead found \'%s\'' % token.value)
    if token.type==Stokens.endwhiletk:
        token=lex()
    else:
        ER(token.line, token.col,'Keyword \'endwhile\' expected instead found \'%s\'' % token.value)
def do_while_stat():
    global token
    while token.type!=Stokens.enddowhiletk:
        statements()
        genquad('jump', '_', '_', b_quad)
    if token.type==Stokens.enddowhiletk:
        token=lex()
        if token.type==Stokens.leftpartk:
            token=lex()
            b_quad = nextquad()
            (b_true, b_false) = condition()
            backpatch(b_true, nextquad())
            if token.type==Stokens.rightpartk:
                token=lex()
                statements()
                genquad('jump', '_', '_', b_quad)
                backpatch(b_false, nextquad())
            else:
                ER(token.line, token.col,'\')\' expected instead found \'%s\'' % token.value)
        else:
            ER(token.line, token.col,'\'(\' expected instead found \'%s\'' % token.value)    
    else:
        ER(token.line, token.col,'Keyword \'enddowhile\' expected instead found \'%s\'' % token.value)   
        
def loop_stat():
    global token
    while token.type!=Stokens.loopendtk:
        statements()
    if  token.type==Stokens.loopendtk:
        token=lex()
    else:
        ER(token.line, token.col,'Keyword \'endloop\' expected instead found \'%s\'' % token.value)


def forcase_stat():
    global token
    if tokens.type==Stokens.leftpartk:
        b_quad = nextquad()
        while token.type==Stokens.leftpartk:
            token=lex()
            if token.type==Stokens.whentk:
                token=lex()
                if token.type==Stokens.leftpartk:
                    token=lex()
                    (b_true, b_false) = condition()
                    if tokens.type == Stokens.rightpartk:
                        token = lex()
                        if token.type==Stokens.colontk:
                            token = lex()
                            backpatch(b_true, nextquad())
                            statements()
                            genquad('jump', '_', '_', b_quad)
                            backpatch(b_false, nextquad())
                            if tokens.type == Stokens.rightpartk:
                                token=lex()
                            else:
                                ER(token.line, token.col,'Keyword \')\' expected instead found \'%s\'' % token.value)
                        else:
                             ER(token.line, token.col,'Keyword \':\' expected instead found \'%s\'' % token.value)      
                    else:
                        ER(token.line, token.col,'Keyword \')\' expected instead found \'%s\'' % token.value) 
                else:
                    ER(token.line, token.col,'Keyword \'(\' expected instead found \'%s\'' % token.value)
            else:
                ER(token.line, token.col,'Keyword \'when\' expected instead found \'%s\'' % token.value)
        if token.type==Stokens.defaulttk:
            token=lex()
            if token.type==Stokens.colontk:
                token=lex()
                backpatch(b_true, nextquad())
                statements()
                genquad('jump', '_', '_', b_quad)
                backpatch(b_false, nextquad())
                if token.type==Stokens.enddefaulttk:
                    token=lex()
                    if token.type==Stokens.endforcasetk:
                        token=lex()  
                    else:
                        ER(token.line, token.col,'Keyword \'endforcase\' expected instead found \'%s\'' % token.value)
                else:
                    ER(token.line, token.col,'Keyword \'enddefault\' expected instead found \'%s\'' % token.value)
            else:
                ER(token.line, token.col,'Keyword \':\' expected instead found \'%s\'' % token.value)
        else:
             ER(token.line, token.col,'Keyword \'default\' expected instead found \'%s\'' % token.value)        
        
    else:
        ER(token.line, token.col,'Keyword \'(\' expected instead found \'%s\'' % token.value)
                       
                           
    
def incase_stat():
    global token
    if token.type==Stokens.leftpartk:
        b_quad = nextquad()
        while token.type==Stokens.leftpartk:
            token=lex()
            if token.type==Stokens.whentk:
                token=lex()
                condition()
                if token.type==Stokens.colontk:
                    token=lex()
                    statements()
                    if tokens.type==Stokens.rightpartk:
                        token=lex()
                        if token.type==Stokens.endincasetk:
                            token=lex()
                        else:
                            ER(token.line, token.col,'Keyword \'endincase\' expected instead found \'%s\'' % token.value)
                    else:
                        ER(token.line, token.col,'Keyword \')\' expected instead found \'%s\'' % token.value)
                else:
                    ER(token.line, token.col,' \':\' expected instead found \'%s\'' % token.value)
            else:
                ER(token.line, token.col,'Keyword \'when\' expected instead found \'%s\'' % token.value)
    else:
        ER(token.line, token.col,'Keyword \'(\' expected instead found \'%s\'' % token.value)
        
def input_stat():
    global token
    if token.type==Stokens.idtk:
        token=lex()
        genquad('inp', token.value, '_', '_')
    else:
        ER(token.line, token.col,'Keyword \'id\' expected instead found \'%s\'' % token.value)







token = Tokens(None,None,None,None)
ch = " "    # dummy first char
col = 0
col2=0
line = 1


nextlabel = 0                   # defintion of next label
tmp_vars = dict()               # for temporary var names
tmpvar = 1              # for the numbering of temp var names
scopes = list()         # list for adding scopes
quadcode = list()               # list of quadruples
halt = 0                        # defintion of halt label
proc_func = False               # var to avoid functions or procedures translating in c
ret_st = []          # means having return statement
ins_func = []           # to determine if we are inside a fucntion
main_framelength = 0    # main program's framelenght
pars = list()       # list to hold the parameters



reserved = Stokens()
tokens = [getattr(reserved, attr) for attr in dir(reserved) if not attr.startswith("__")]
#trexei ton epomeno xaraktira
def next_ch(buff):
    global ch, col2, col, line
    ch = input_file.read(1)
    buff.append(ch)
    col += 1
    col2+=1
    if ch == '\n':
        line += 1
        col = 0
    return ch, line, col, col2


# Lexical analyser (Finite-State Machine Implementation)
def lex():
    buff = [] # stores ch
    OK = -1     # when it's ok
    backtrack = False # if i have to backtrack a character
    state = 0
    
    while state!=OK:
        r, line, col, col2 = next_ch(buff)
        if state==0:
            if r.isalpha():
                state=1
            elif r.isdigit():
                state=2
            elif r=='<':
                state=3
            elif r=='>':
                state=4
            elif r==':':
                state=5
            elif r=='{':
                state=6
            elif r in ('/n','+','-','*','/',',','=',';','(',')','[',']'):
                state=OK
            elif r=='':
                state=OK
            elif r.isspace():
                state=0
            else:
                ER(line, col, 'Invalid character \'%c\' given ' % r)
        elif state==1:
            if not r.isalnum():
                state=OK
                backtrack = True
        elif state==2:
            if not r.isdigit():
                if r.isalpha():
                    ER(line, col,'Invalid variable name')
                state=OK
                backtrack =True
        elif state==3:
            if r!='=' or r!='>':
                backtrack=True
            state=OK
        elif state==4:
            if r!='=':
                backtrack=True
            state=OK
        elif state==5:
            if r!='=':
                backtrack=True
                ER(line, col,'\':\' expected to be followed by \'=\'')
            state=OK

        elif state==6:
            if r == '}':
                state = 0
            elif r == '':
                ER(line, col,' \'*\' or \'/\' after \'/\' expected')

        if state==OK:
            the_line = line
            if col!=0:
                the_col = col-1
            else:
                the_col=col2+col
                col2=0
                
        if r.isspace():
            del buff[-1]
            backtrack=False

    if backtrack==True:
        del buff[-1]
        if r!='':
            input_file.seek(input_file.tell()-1)
        col -=1
    #empty for the result token object
    ret = ''.join(buff)
    if ret in tokens:
        for attr in dir(reserved):
            if ret == getattr(reserved, attr):
                resbuf = attr
        resbuf = eval("Stokens." + resbuf)
        tokret = Tokens(resbuf, ret, the_line, the_col)
    else:
        if ret.isdigit():
            tokret = Tokens(Stokens.numbertk, ret, the_line, the_col)
        else:
            tokret = Tokens(Stokens.idtk, ret, the_line, the_col)
    del buff[:]
    print (tokret)
    return tokret


import sys
def main(argv):
    global input_file, create_c, create_int, create_final
    input_file = sys.stdin
    c_file =''
    int_file=''
    fin_file=''
    if len(sys.argv) > 1:
        try:
            input_file = open(sys.argv[1], 'r', 4096)
        except IOError as e:
            ER(0, 0, 'Cant open \'%s\'' % sys.argv[1])

    create_c = open('c_file.c', 'w+')
    create_int = open('int_file.int', 'w+')
    create_final  = open('fin_file.asm', 'w+')

    parser()

    create_c.close()
    create_int.close()
    create_final.close()
if __name__ == "__main__":
    main(sys.argv[1:])
