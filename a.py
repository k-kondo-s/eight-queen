from engine.minconflicts_engine import MinConflictsEngine
e = MinConflictsEngine(n=8, version=6)
e.initialize_current_board()
b = e.convert_to_boards()
b[0].print()

e = MinConflictsEngine(n=8, version=6)
boards = e.solve()
boards[0].print()
print(f'{e.n}:')
print(f'  is solution: {e.has_solution()}')
print(f'  duration: {e.debug_duration_seconds} sec')
print(f'  steps: {e.debug_steps}')
