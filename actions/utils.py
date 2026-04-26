import re

def calculate(expression):
    try:
        # keep only safe characters
        expression = re.sub(r"[^0-9\+\-\*/\.\(\)\s]", "", expression)

        result = eval(expression, {"__builtins__": None}, {})
        return f"Result: {result}"

    except Exception:
        return "Invalid calculation"
