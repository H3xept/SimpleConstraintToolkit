from simplifier import *

variables = ["A", "B", "C", "D"]
domain = list([n+1 for n in range(5)])

problem = Problem()

for v in variables:
    problem.addVariable(v, domain)

problem.addUnidirectionalConstraint("A", "B", "<")
problem.addUnidirectionalConstraint("B", "C", "<")
problem.addUnidirectionalConstraint("C", "D", "==", v1_apply=lambda x: x+2)

ps = ProblemSolver(problem)
print(ps.solveWithBacktracking())
