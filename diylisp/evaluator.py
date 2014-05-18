# -*- coding: utf-8 -*-

from types import Environment, LispError, Closure
from ast import is_boolean, is_atom, is_symbol, is_list, is_closure, is_integer
from asserts import assert_exp_length, assert_valid_definition, assert_boolean
from parser import unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports, 
making your work a bit easier. (We're supposed to get through this thing 
in a day, after all.)
"""

commands = set(["quote", "atom", "eq", "if", "define","lambda", "print"])
arithmeticOps = set(["+", "-", "*", "/", "mod", ">", "<"])
listOps = set(["cons", "head", "tail", "empty"])
commands = commands | arithmeticOps | listOps;

def evaluate(ast, env):
	"""Evaluate an Abstract Syntax Tree in the specified environment."""

	if is_symbol(ast):
		return env.lookup(ast)
	elif is_boolean(ast) or is_integer(ast):
		return ast
	elif is_closure(ast):
		return evalClosure(ast, [], env)
	elif is_list(ast) and len(ast) > 0:
		first = ast[0]

		# handle string commands
		if isinstance(first, basestring):
			if first in commands:
				return evalCommand(first, ast[1:], env)
			# When a non-keyword symbol is the first element of the AST list, it is resolved to its value in
			# the environment (which should be a function closure). An AST with the variables
			# replaced with its value should then be evaluated instead.
			else:
				func = env.lookup(first)
				if not is_closure(func):
					raise LispError("Symbol %s must evaluate to a function" % first)

				ast[0] = func
				return evaluate(ast, env)
		# handle closure objects
		elif is_closure(first):
			return evalClosure(first, ast[1:], env)
		else: # otherwise - evaluate the first expression on the list
			firstEval = evaluate(first, env);
			if is_closure(firstEval): # if closure - treat the rest of the list as arguments
				return evalClosure(first, ast[1:], env)
			else : # not a closure, just evaluate the rest of the list and return the last expression
				if len(ast) > 1:
					return evaluate(ast[1:], env)
				else:
					return firstEval

	raise LispError("Invalid AST: %s" % ast)

def evalCommand(command, args, env):
	if command == "quote":
		return evalQuoteCommand(args, env)
	elif command == "atom":
		return evalAtomCommand(args, env)
	elif command == "eq":
		return evalEqCommand(args, env)
	elif command == "if":
		return evalIfCommand(args, env)
	elif command == "define":
		return evalDefineCommand(args, env)
	elif command == "lambda":
		return evalLambdaCommand(args, env)
	elif command == "print":
		return evalPrintCommand(args, env)
	elif command in arithmeticOps:
		return evalArithmeticCommand(command, args, env)
	elif command in listOps:
		return evalListCommand(command, args, env)

def evalQuoteCommand(args, env):
	if len(args) != 1:
		raise LispError("quote command expects exactly one argument")
	
	return args[0]

def evalAtomCommand(args, env):
	if len(args) != 1:
		raise LispError("atom command expects exactly one argument")
	
	return is_atom(args[0])

def evalEqCommand(args, env):
	if len(args) != 2:
		raise LispError("eq command expects exactly two arguments")
	
	return evaluate(args[0], env) == evaluate(args[1], env)

def evalIfCommand(args, env):
	if len(args) != 3:
		raise LispError("if command expects exactly three arguments")

	predicate = evaluate(args[0], env)

	if predicate:
		return evaluate(args[1], env)
	else:
		return evaluate(args[2], env)

def evalDefineCommand(args, env):
	if len(args) != 2:
		raise LispError("define command expects exactly two arguments")

	if not is_symbol(args[0]):
		raise LispError("define command expects a symbol as parameter 1")

	env.set(args[0], evaluate(args[1], env))

	return None

def evalPrintCommand(args, env):
	if len(args) != 1:
		raise LispError("print command expects exactly one arguments")

	arg = evaluate(args[0], env)

	print arg

	return arg

def evalArithmeticCommand(command, args, env):
	if len(args) != 2:
		raise LispError(command + " command expects exactly two arguments")

	try:
		x = int(evaluate(args[0], env))
		y = int(evaluate(args[1], env))
	except ValueError:
		raise

	if command == "+":
		return x + y
	elif command == "-":
		return x - y
	elif command == "*":
		return x * y
	elif command == "/":
		return int(x / y)
	elif command == "mod":
		return x % y
	elif command == ">":
		return x > y
	elif command == "<":
		return x < y

	raise LispError("Invalid arithmetic command")

def evalLambdaCommand(args, env):
	if len(args) != 2:
		raise LispError("lambda command expects exactly two arguments")

	params = args[0]
	body = args[1]

	if not is_list(params):
		raise LispError("lambda first parameter is expected to be a list")

	# In case the lambda has no parameters, evaluate its body and return the result
	if len(params) == 0:
		return evaluate(body, env)
	else:
		return Closure(env, params, body)

def evalClosure(closure, params, env):
	if not is_closure(closure):
		raise LispError("Expect a function closure")

	if len(closure.params) != len(params):
		raise LispError("%d parameters expected by function, %d are passed" % (len(closure.params), len(params)))

	evaluatedParams = map(lambda p: evaluate(p, env), params)
	closureEnv = closure.env.extend(dict(zip(closure.params, evaluatedParams)))
	return evaluate(closure.body, closureEnv);


def evalListCommand(command, args, env):
	if command == "cons":
		return evalConsCommand(args, env)
	elif command == "head":
		return evalHeadCommand(args, env)
	elif command == "tail":
		return evalTailCommand(args, env)
	elif command == "empty":
		return evalEmptyCommand(args, env)

	raise LispError("Invalid list command")

def evalConsCommand(args, env):
	if len(args) != 2:
		raise LispError("cons command expects exactly two arguments")

	head = evaluate(args[0], env)
	rest = evaluate(args[1], env)

	if not is_list(rest):
		raise LispError("cons command expects a list as second argument")

	output = list(rest)
	output.insert(0, head)

	return output

def evalHeadCommand(args, env):
	if len(args) != 1:
		raise LispError("head command expects exactly one argument")

	arg = evaluate(args[0], env)

	if not is_list(arg):
		raise LispError("head command expects a list as argument")

	if len(arg) == 0:
		raise LispError("head command expect non-empty list")

	return arg[0]

def evalTailCommand(args, env):
	if len(args) != 1:
		raise LispError("tail command expects exactly one argument")

	arg = evaluate(args[0], env)

	if not is_list(arg):
		raise LispError("tail command expects a list as argument")

	if len(arg) == 0:
		raise LispError("tail command expect non-empty list")

	return arg[1:]

def evalEmptyCommand(args, env):

	if len(args) != 1:
		raise LispError("tail command expects exactly one argument")

	arg = evaluate(args[0], env)

	if not is_list(arg):
		raise LispError("tail command expects a list as argument")

	return len(arg) == 0