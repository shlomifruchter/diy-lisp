import sys
from diylisp.parser import parse
from diylisp.evaluator import evaluate
from diylisp.types import Environment


program = """(
(define fact 
;; Factorial function
(lambda (n) 
    (if (eq n 0) 
        1 ; Factorial of 0 is 1
        (* n (fact (- n 1))))))

(print (fact 3))
(print (fact 6))
)
"""

evaluate(parse(program), Environment())