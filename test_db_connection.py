from config.database import test_connection

try:
    result = test_connection()
    print("DB connection success:", result)
except Exception as e:
    print("DB connection failed:")
    print(e)