"""# Gives an int when it can or a float when needed
def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            print("Invalid equation")

equation = "5+10*5"
nums = []
operators = []
j = 0
for i in range(len(equation)):
    if not equation[i].isnumeric():
        nums.append(num(equation[j:i]))
        operators.append(equation[i])
        j = i+1
# Gets the last number since every valid equation should end with a number
nums.append(num(equation[j:len(equation)]))

print(nums)
print(operators)

if (len(nums) != len(operators) + 1):
    print("Invalid Equation")

result = nums[0]
for i in range(len(operators)):
    if operators[i] == '+':
        result += nums[i+1]
    elif operators[i] == '-':
        result -= nums[i+1]
    elif operators[i] == '*':
        result *= nums[i+1]
    elif operators[i] == '/':
        result /= nums[i+1]
    elif operators[i] == '^':
        result = result ** nums[i+1]

print(result)
"""

from os import error
from bs4 import BeautifulSoup
import requests
equation = "x*sin(x)"
# from sympy.solvers import solve
# from sympy import Symbol
from sympy import *
i = 0
# start = 0
while i < len(equation):
    if equation[i].isalpha():
        if i != 0 and equation[i-1].isnumeric():
            equation = equation[:i] + "*" + equation[i:]
            i += 1
    # if equation[i] == '=':
    #     start = i
    #     if (not equation[i-1].isnumeric() and equation[i-1] != ')') or (not equation[i+1].isnumeric() and equation[i+1] != '('):
    #         print("Invalid equation")
    #         break
    if equation[i] == "^":
        equation = equation[:i] + "**" + equation[i+1:]
        i += 1
    i += 1
# if not equation[len(equation)-1].isnumeric():
#     print("Invlaid equation")

"""if start != 0:
    afterEquals = equation[start+1:]
    equation = equation[:start]
    equation += "-(" + afterEquals + ")"
"""
print(equation)
x = Symbol('x')
a = 0
b = 10
try:
    solution = integrate(equation, (x, a, b))
except:
    solution = "Error"

print(solution)
"""
i = 0
var = ""
start = 0
while i < len(equation):
    if equation[i].isalpha():
        if var != "":
            print("Invalid Equation")
            break
        var = equation[i]
        if i != 0 and equation[i-1].isnumeric():
            equation = equation[:i] + "*" + equation[i:]
            i += 1
    if equation[i] == '=':
        start = i
        if (not equation[i-1].isnumeric() and equation[i-1] != ')') or (not equation[i+1].isnumeric() and equation[i+1] != '('):
            print("Invalid equation")
            break
    if equation[i] == "^":
        equation = equation[:i] + "**" + equation[i+1:]
        i += 1
    i += 1
if not equation[len(equation)-1].isnumeric():
    print("Invlaid equation")

afterEquals = equation[start+1:]
equation = equation[:start]
equation += "-(" + afterEquals + ")"
print(equation)
x = Symbol(var)
try:
    solution = solve(equation, x)
except:
    solution = "Error"

print(solution)
"""
"""
i = 0
while i < len(equation):
    if equation[i] == '+':
        equation = equation[:i] + "%2B" + equation[i+1:]
        i += 1
    elif equation[i] == '/':
        equation = equation[:i] + "%2F" + equation[i+1:]
        i += 1
    elif equation[i] == '%':
        equation = equation[:i] + "%25" + equation[i+1:]
        i += 1
    i += 1

print(equation)


searchURL = "https://www.google.com/search?q=" + equation
# searchURL = "https://www.symbolab.com/solver/step-by-step/" + equation
print(searchURL)
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')

div = soup.find_all('div', class_='BNeawe iBp4i AP7Wnd')
answer = div[0].text
answer = answer.replace("\xa0", ",")
span = soup.find_all('span', class_='BNeawe tAd8D AP7Wnd')
newEquation = span[0].text
print(newEquation, answer)
"""