import sys
from engine.minconflicts_engine import MinConflictsEngine
from engine.minconflicts_engine_3 import MinConflictsEngine as E3
from engine.minconflicts_engine_4 import MinConflictsEngine as E4
from engine.minconflicts_engine_5 import MinConflictsEngine as E5
from engine.minconflicts_engine_6 import MinConflictsEngine as E6

n = int(sys.argv[1]) if len(sys.argv) >= 2 else 8
t = True if len(sys.argv) >= 3 else False
e = E6(n=n)
boards = e.solve(enable_print=t)
if t:
    boards[0].print()
print(f'{e.n}:')
print(f'  is solution: {e.has_solution()}')
print(f'  duration: {e.debug_duration_seconds} sec')
print(f'  steps: {e.debug_steps}')