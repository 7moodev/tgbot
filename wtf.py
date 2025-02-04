import sys

try:
    1 / 0  # This will cause a ZeroDivisionError
except Exception as e:
    print("Caught an exception:", e)

exc_type, exc_value, exc_traceback = sys.exc_info()
print("Latest Exception Type:", exc_type)
print("Latest Exception Message:", exc_value)
