import time
import math

start = time.time()
# print(start)
# print(time.time())
while int(time.time() - start) < int(10):
    print(10 - math.floor(time.time() - start))
    time.sleep(1)