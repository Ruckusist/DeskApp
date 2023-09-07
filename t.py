from time import sleep
from timeit import default_timer as timer


start = timer()

import deskapp

runtime = timer() - start
print(f"Import Runtime:  {runtime:.4f}")
sleep(3)
t = deskapp.Test().run()

runtime = timer() - start
print(f"Runtime:  {runtime:.4f}")
sleep(3)
a = deskapp.App()

runtime = timer() - start
print(f"Runtime:  {runtime:.4f}")
sleep(3)

a.run()
runtime = timer() - start
print(f"Runtime:  {runtime:.4f}")
sleep(3)
print("Done.")