from Parse import Parser
from BadSyntaxException import BadSyntaxException

while True:
    userInput = input("Enter an SQL statement: ")
    if userInput == "exit":
        break

    p = Parser(userInput)
    try:
        if userInput.startswith("select"):
            p.query()
        else:
            p.updateCmd()
        print("yes")
    except BadSyntaxException:
        print("no")


