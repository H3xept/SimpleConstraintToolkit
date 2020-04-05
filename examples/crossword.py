from simplifier import *

words = ["aft", "ale", "eel", "heel", "hike", "roses", "keel", "knot", "laser", "lee", "line", "sails", "sheet", "steer", "tie"]

problem = Problem()
problem.addVariable("W1", filter(lambda w: len(w) == 5, words))
problem.addVariable("W2", filter(lambda w: len(w) == 5, words))
problem.addVariable("W3", filter(lambda w: len(w) == 5, words))
problem.addVariable("W4", filter(lambda w: len(w) == 4, words))
problem.addVariable("W5", filter(lambda w: len(w) == 4, words))

problem.addConstraint("W1", "W2", "==", v1_apply=lambda w1:w1[2], v2_apply=lambda w2:w2[0])
problem.addConstraint("W1", "W3", "==", v1_apply=lambda w1:w1[4], v2_apply=lambda w2:w2[0])
problem.addConstraint("W2", "W4", "==", v1_apply=lambda w1:w1[2], v2_apply=lambda w2:w2[1])
problem.addConstraint("W3", "W4", "==", v1_apply=lambda w1:w1[2], v2_apply=lambda w2:w2[3])
problem.addConstraint("W4", "W5", "==", v1_apply=lambda w1:w1[2], v2_apply=lambda w2:w2[0])
problem.addConstraint("W4", "W2", "==", v1_apply=lambda w1:w1[1], v2_apply=lambda w2:w2[2]) 

cs = ConstraintSimplifier(problem)
arc_complete_problem = cs.makeARC_3()

ps = ProblemSolver(problem)
full_assignment = ps.solveWithBacktracking()

print(full_assignment)
