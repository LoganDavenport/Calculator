import math
from collections import defaultdict
from copy import deepcopy
    
def parse(expr):
    if len(expr) == 0:
        return Error()
    # see if it's a sum of two things
    i = len(expr)-1
    while i >= 0:
        while expr[i] == ')' and i >= 0:
            i = expr.rfind("(", 0, i)-1
        if expr[i] == '+' or expr[i] == '-' and i != 0:
            left = parse(expr[:i])
            right = parse(expr[i+1:])
            if type(left) is Error or type(right) is Error:
                return Error()
            if(expr[i] == '-'):
                right = Product(Constant(-1), right)
            return Sum(left, right)
        i -= 1
    # see if it's a product of two things
    i = len(expr)-1
    while i >= 0:
        while expr[i] == ')' and i >= 0:
            i = expr.rfind("(", 0, i)-1
        if expr[i] == '*' or expr[i] == '/':
            left = parse(expr[:i])
            right = parse(expr[i+1:])
            if type(left) is Error or type(right) is Error:
                return Error()
            if expr[i] == '/':
                right = Power(right, Constant(-1))
            return Product(left, right)
        i -= 1
    # see if it's a power
    i = len(expr)-1
    while i >= 0:
        while expr[i] == ')' and i >= 0:
            i = expr.rfind("(", 0, i)-1
        if expr[i] == '^':
            left = parse(expr[:i])
            right = parse(expr[i+1:])
            if type(left) is Error or type(right) is Error:
                return Error()
            else:
                return Power(left, right)
        i -= 1
    # if it gets here, it's either enclosed in parentheses, a constant, 
    # a variable, or a basic function
    if expr[0] == '(' and expr[-1] == ')':
        return parse(expr[1:-1])
    try:
        return Constant(int(expr))
    except ValueError:
        pass
    try:
        return Constant(float(expr))
    except ValueError:
        pass
    # ln([expr]), log([expr]), log_[constant]([expr]), or log_([expr])([expr])
    if expr[:2] == 'ln' or expr[:3] == 'log':
        base = Error()
        arg_start = expr.find('(')+1
        if expr[:2] == 'ln': # ln([arg])
            base = Constant(math.e)
        elif expr[3] != '_': # log([arg])
            base = Constant(10)
        elif expr[4] == '(': # log_([base])([arg])
            end = expr.find(')', 4)
            base = parse(expr[5:end])
            arg_start = end+1
        else: #log_[constant]([arg])
            end = expr.find('(')
            base = parse(expr[4:end])
            arg_start = end+1
        arg = parse(expr[arg_start:-1])
        return Log(base, arg)
    if expr == 'e':
        return Constant(math.e)
    if expr == 'pi':
        return Constant(math.pi)
    return Variable(expr)
        
class Expression:
    
    def evaluate(self, variables):
        pass
    
    def derivative(self, variable):
        pass
    
    def __str__(self):
        pass
    
    def __eq__(self, obj):
        pass
    
    def __hash__(self):
        return hash(str(self))

class Error(Expression):

    def evaluate(self, variables):
        return "bad expression"
    
    def derivative(self, variable):
        return "bad expression"
    
    def __str__(self):
        return "bad expression"
    
    def __eq__(self, obj):
        return "bad expression"
    
    def __hash__(self):
        return hash(str(self))

class Constant(Expression):

    def __init__(self, val):
        self.val = val
        self.variables = set()
        
    def simplify(self, variables={}):
        return self
    
    def derivative(self, variable):
        return Constant(0)
    
    def __str__(self):
        return str(self.val)
    
    def __eq__(self, obj):
        return type(obj) is Constant and obj.val == self.val
    
    def __hash__(self):
        return hash(str(self))
        
class Variable(Expression):

    def __init__(self, name):
        self.name = name
        self.variables = {name}
    
    def simplify(self, variables={}):
        if self.name in variables:
            return Constant(variables[self.name])
        return self
    
    def derivative(self, variable):
        return Constant(1 if self.name == variable else 0)
        
    def __str__(self):
        return self.name
    
    def __eq__(self, obj):
        return type(obj) is Variable and obj.name == self.name
    
    def __hash__(self):
        return hash(str(self))
        
class Log(Expression):
    
    def __init__(self, base, argument):
        self.base = base
        self.argument = argument
        self.variables = base.variables | argument.variables
    
    def simplify(self, variables={}):
        self.base = self.base.simplify(variables)
        self.argument = self.argument.simplify(variables)
        if type(self.base) is Constant and type(self.argument) is Constant:
            return Constant(math.log(self.argument.val, self.base.val))
        return self
    
    def derivative(self, variable):
        if variable in self.base.variables: #log_f(x)([arg])
            return Product(Log(Constant(math.e), self.argument), 
                            Power(Log(Constant(math.e), self.base), Constant(-1))).derivative(variable)
        return Product(self.argument.derivative(variable), 
                    Power(Product(Log(Constant(math.e), self.base), self.argument), Constant(-1)))
    
    def __str__(self):
        if type(self.base) is Constant and self.base.val == math.e:
            return "ln(" + str(self.argument) + ")"
        return "log_(" + str(self.base) + ")(" + str(self.argument) + ")"
    
    def __eq__(self, obj):
        return type(obj) is Log and obj.base == self.base and obj.argument == self.argument
    
    def __hash__(self):
        return hash(str(self))
    

class Sum(Expression):

    def __init__(self, left, right):
        self.addends = []
        self.addends.append(left)
        self.addends.append(right)
        self.variables = left.variables | right.variables
    
    def simplify(self, variables={}):
        i = len(self.addends)-1
        while i >= 0:
            self.addends[i] = self.addends[i].simplify(variables)
            if type(self.addends[i]) is Sum:
                self.addends.extend(self.addends[i].addends)
                self.addends.remove(self.addends[i])
            i -= 1
      
        constant_sum = sum([addend.val for addend in self.addends 
                                            if type(addend) is Constant])
        self.addends = [addend for addend in self.addends
                                        if type(addend) is not Constant]
        if len(self.addends) == 0:
            return Constant(constant_sum)
        if constant_sum != 0:
            self.addends.append(Constant(constant_sum))
        elif len(self.addends) == 1:
            return self.addends[0]
            
        # simplify f(x)*g(x)+f(x)*h(x)
        factors = defaultdict(lambda: 0)
        
        
        return self
    
    def derivative(self, variable):
        derivative = deepcopy(self)
        for i in range(0, len(derivative.addends)):
            derivative.addends[i] = derivative.addends[i].derivative(variable)
        return derivative.simplify()
    
    def __str__(self):
        string = '(' + str(self.addends[0])
        for i in range(1, len(self.addends)):
            string += '+' + str(self.addends[i])
        string += ')'
        return string
    
    def __eq__(self, obj):
        simpl = self.simplify()
        obj = obj.simplify()
        if type(simpl) is not Sum:
            return simpl == obj
        return (type(obj) is Sum and len(obj.addends) == len(self.addends) and 
                all([addend in self.addends for addend in obj.addends]))
    
    def __hash__(self):
        return hash(str(self))
        

class Product(Expression):

    def __init__(self, left, right):
        self.multipliers = []
        self.multipliers.append(left)
        self.multipliers.append(right)
        self.variables = left.variables | right.variables
                        
    def simplify(self, variables={}):
        i = len(self.multipliers)-1
        while i >= 0:
            self.multipliers[i] = self.multipliers[i].simplify(variables)
            if type(self.multipliers[i]) is Product:
                self.multipliers.extend(self.multipliers[i].multipliers)
                self.multipliers.remove(self.multipliers[i])
            i -= 1
      
        constant_prod = math.prod([multiplier.val for multiplier in self.multipliers 
                                                if type(multiplier) is Constant])
        self.multipliers = [multiplier for multiplier in self.multipliers
                                            if type(multiplier) is not Constant]
        if constant_prod == 0:
            return Constant(0)
        if len(self.multipliers) == 0:
            return Constant(constant_prod)
        if constant_prod != 1:
            self.multipliers.insert(0, Constant(constant_prod))
        elif len(self.multipliers) == 1:
            return self.multipliers[0]
        
        # simplify f(x)^g(x)*f(x)^h(x)
        powers = defaultdict(lambda: Constant(0))
        while self.multipliers:
            multiplier = self.multipliers.pop()
            if type(multiplier) is Power:
                powers[multiplier.base] = Sum(powers[multiplier.base], multiplier.exponent).simplify()
            else:
                powers[multiplier] = Sum(powers[multiplier], Constant(1)).simplify()
        
        negative_power_base = Constant(1)
        for base, power in powers.items():
            if type(power) is Constant and power.val < 0:
                negative_power_base = Product(negative_power_base, 
                                                Power(base, Constant(-power.val)).simplify()).simplify()
            else:
                self.multipliers.append(Power(base, power).simplify())
        
        if type(negative_power_base) is not Constant or negative_power_base.val != 1:
            self.multipliers.append(Power(negative_power_base, Constant(-1)))
            
        if len(self.multipliers) == 1:
            return self.multipliers[0]
        
        return self
    
    def derivative(self, variable):
        derivative = Constant(0)
        for i in range(0, len(self.multipliers)):
            copy = deepcopy(self)
            copy.multipliers[i] = copy.multipliers[i].derivative(variable)
            derivative = Sum(derivative, copy).simplify()
        return derivative
    
    def __str__(self):
        string = '(' + str(self.multipliers[0])
        for i in range(1, len(self.multipliers)):
            string += '*' + str(self.multipliers[i])
        string += ')'
        return string
    
    def __eq__(self, obj):
        simpl = self.simplify()
        obj = obj.simplify()
        if type(simpl) is not Product:
            return simpl == obj
        return (type(obj) is Product and len(obj.multipliers) == len(self.multipliers) and 
                all([multiplier in self.multipliers for multiplier in obj.multipliers]))
    
    def __hash__(self):
        return hash(str(self))

class Power(Expression):
    
    def __init__(self, base, exponent):
        self.base = base
        self.exponent = exponent
        self.variables = base.variables | exponent.variables
        
    def simplify(self, variables={}):
        self.base = self.base.simplify(variables)
        self.exponent = self.exponent.simplify(variables)
        if type(self.base) is Constant and self.base.val == 1:
            return Constant(1)
        if type(self.exponent) is Constant:
            if self.exponent.val == 1:
                return self.base
            if self.exponent.val == 0:
                return Constant(1)
            if type(self.base) is Constant:
                return Constant(self.base.val**self.exponent.val)
        return self
        
    def derivative(self, variable):
        return Product(self, Product(self.exponent, Log(Constant(math.e), self.base)).derivative(variable)).simplify()
        
    def __str__(self):
        return str(self.base) + "^" + str(self.exponent)
    
    def __hash__(self):
        return hash(str(self))
    

if __name__ == "__main__":
    test = parse("ln(x)*ln(x)^(-1)-1").simplify()
    
    print(test)