import copy
import operator
import time

def identity(a):
    return a

ops = {
    '<': operator.lt,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    '>=': operator.ge,
    '>': operator.gt
}

class BinaryConstraint():
    def __init__(self, a, b, operator, a_apply = identity, b_apply = identity):
        self.varA = a
        self.varB = b
        self.aApply = a_apply
        self.bApply = b_apply
        self.operator = operator

    def cmp(self, a, b, operator):
        if operator not in ops:
            raise f"Operator '{operator}' not recognised. Please use <,>,<=,>=,==,!="
        op = ops.get(operator)
        return op(a, b)

    def checkConstraintForValues(self, valA, valsB, verbose = True):
        for valB in valsB:
            res = self.cmp(self.aApply(valA), self.bApply(valB), self.operator)
            if verbose:
                print(f' > Testing {self} with values ({self.aApply(valA)}, {self.bApply(valB)}) => {res}')
            if res:
                return True
        return False
    
    def checkConstraintsForIndividualValues(self, valA, valB, verbose = True):
        res = self.cmp(self.aApply(valA), self.bApply(valB), self.operator)
        if verbose:
            print(f' > Testing {self} with values ({self.aApply(valA)}, {self.bApply(valB)}) => {res}')
        return res
        
    def __repr__(self):
        return f"{self.varA} {self.operator} {self.varB}"

class Problem():
    def __init__(self):
        self.variables = []
        self.domains = {}
        self.arcs = []
    
    # Add a variable and its domain to the problem
    def addVariable(self, name, domain):
        assert name
        self.variables.append(name)
        for possible_value in domain:
            if name not in self.domains:
                self.domains[name] = []
            self.domains[name].append(possible_value)

    def addUnidirectionalConstraint(self, v1, v2, operator, v1_apply = identity, v2_apply = identity):
        assert v1 in self.variables
        assert v2 in self.variables
        self.generateArc(v1, v2, operator, v1_apply=v1_apply, v2_apply=v2_apply)


    def addConstraint(self, v1, v2, operator_l_r, operator_r_l = None, v1_apply = identity, v2_apply = identity):
        assert v1 in self.variables
        assert v2 in self.variables
        
        if operator_r_l == None:
            operator_r_l = operator_l_r

        self.generateArc(v1, v2, operator_l_r, v1_apply=v1_apply, v2_apply=v2_apply)
        self.generateArc(v2, v1, operator_r_l, v1_apply=v2_apply, v2_apply=v1_apply)

    def generateArc(self, v1, v2, operator, v1_apply = identity, v2_apply = identity):
        self.arcs.append(BinaryConstraint(v1, v2, operator, a_apply=v1_apply, b_apply=v2_apply))

    def getDomainForVariable(self, v):
        if v not in self.domains:
            print(f'[Error] Domain for variable {v} not present!')
            return []
        return self.domains[v]

    def arcsWithRelationTo(self, v):
        return filter(lambda a: a.varB == v, self.arcs)

    def getArcs(self):
        return self.arcs.copy()

    def __repr__(self):
        return str(self.domains)

class ConstraintSimplifier():
    def __init__(self, problem):
        self.problem = copy.deepcopy(problem)
        self.agenda = []

    def ARC_3(self):
        print(f'[@] Running ARC3')
        start_time = time.time()
        try:
            while True:
                arc_constraint = self.agenda.pop()
                varA = arc_constraint.varA
                varB = arc_constraint.varB
                dA = self.problem.getDomainForVariable(varA)
                dB = self.problem.getDomainForVariable(varB)
                if len(dA) == 0 or len(dB) == 0:
                    print(f'[!] Inconsistency found! Problem can\'t be soved. Constraints too strong')
                    return False
                for a in dA:
                    if not arc_constraint.checkConstraintForValues(a, dB):
                        print(arc_constraint, a, dB)
                        dA.remove(a)
                        toAdd = list(filter(lambda x: x , self.problem.arcsWithRelationTo(varA)))
                        print(f'[~] Domain of {varA} modified, adding arcs {toAdd}')
                        self.agenda.extend(toAdd)
        except IndexError as ie:
            print(f'Completed ARC3 (Running time: {time.time() - start_time})')
            return True

    def makeARC_3(self):
        self.agenda = self.problem.getArcs()
        return self.problem if self.ARC_3() else None


class ProblemSolver():
    def __init__(self, problem):
        self.problem = problem

    def checkConstraintsForAssignment(self, assignment):
        for constraint in self.problem.arcs:
            if (constraint.varA not in assignment or constraint.varB not in assignment):
                continue
            valA = assignment[constraint.varA]
            valB = assignment[constraint.varB]
            if not constraint.checkConstraintsForIndividualValues(valA, valB, verbose = False):
                return False
        return True

    def forwardChecking(self, var, val):
        constraintsToCheck = filter(lambda c: c.varA == var, self.problem.arcs)
        newDomains = {}
        for constraint in constraintsToCheck:
            varB = constraint.varB
            newDomains[varB] = list(filter(lambda v: v is not None, [v if constraint.checkConstraintsForIndividualValues(val,v, verbose = False) else None for v in self.problem.domains[varB]]))
        return newDomains

    def _backtrack(self, partial_assignment, forwardChecking = True):
        assert self.problem
        if set(partial_assignment.keys()) == set(self.problem.variables):
            return partial_assignment
        to_assign = list(filter(lambda x: x is not None, [var if var not in partial_assignment else None for var in self.problem.variables]))[0]
        
        print(f"Next to assign: {to_assign}")

        for d_val in self.problem.domains[to_assign]:
            
            domains_before_fwc = copy.deepcopy(self.problem.domains)
            print(f"\t Trying assignment {to_assign}:{d_val}")
            new_assignment = {}
            new_assignment.update(partial_assignment)
            new_assignment.update({f"{to_assign}":d_val})

            if forwardChecking:
                self.problem.domains.update(self.forwardChecking(to_assign, d_val))
                print(f'New domains {self.problem.domains}')
                
            if self.checkConstraintsForAssignment(new_assignment):
                result = self._backtrack(new_assignment, forwardChecking = forwardChecking)
                if result is not None:
                    return result
                print(f'Backtracking, assignment {to_assign}:{d_val} not valid')
            self.problem.domains = domains_before_fwc
        return None

    def solveWithBacktracking(self, forwardChecking = True):
        assert self.problem
        return self._backtrack({}, forwardChecking = forwardChecking)
