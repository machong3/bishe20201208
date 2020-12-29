import time
import matlab.engine
eng=matlab.engine.start_matlab()
a=eng.func(1.0,2.0)
print(a)
