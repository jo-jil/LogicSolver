import itertools
import sys

# Function to parse clauses and extract unique atoms
def parse_clauses(input_lines):
    clauses = []
    atoms = set()
    for line in input_lines:
        clause = line.strip().split(',')
        clauses.append(set(clause))
        for literal in clause:
            atoms.add(literal.strip('~'))
    return clauses, atoms

# Function to find a unit clause in the set of clauses
def find_unit_clause(clauses):
    for clause in clauses:
        if len(clause) == 1:
            return next(iter(clause))
    return None

# Function to find a pure literal across all clauses
def find_pure_literal(clauses, assignments):
    all_literals = set(itertools.chain(*clauses))
    candidate_literals = {literal.strip('~') for literal in all_literals}
    for atom in candidate_literals:
        if atom in assignments or f'~{atom}' in assignments:
            continue
        if {atom}.issubset(all_literals) ^ {f'~{atom}'}.issubset(all_literals):
            return atom if {atom}.issubset(all_literals) else f'~{atom}'
    return None

# Function to apply DPLL algorithm
def dpll(clauses, assignments, use_unit=True, use_pure=True):
    # Check for contradictions in assignments: If an atom and its negation are both assigned as true, it's unsatisfiable.
    for atom in assignments:
        if atom.startswith('~'):
            if atom[1:] in assignments:
                return None
        else:
            if f'~{atom}' in assignments:
                return None

    # Early termination
    if not clauses:
        return assignments
    if any(not clause for clause in clauses):
        return None

    # Unit clause heuristic
    if use_unit:
        unit = find_unit_clause(clauses)
        if unit:
            # Avoid adding contradictory assignments
            if (unit.startswith('~') and unit[1:] in assignments) or (not unit.startswith('~') and f'~{unit}' in assignments):
                return None
            new_assignments = assignments.copy()
            new_assignments.add(unit)
            return dpll([clause - {unit} for clause in clauses if unit not in clause],
                        new_assignments, use_unit, use_pure)

    # Pure literal heuristic
    if use_pure:
        pure = find_pure_literal(clauses, assignments)
        if pure:
            # Avoid adding contradictory assignments
            if (pure.startswith('~') and pure[1:] in assignments) or (not pure.startswith('~') and f'~{pure}' in assignments):
                return None
            new_assignments = assignments.copy()
            new_assignments.add(pure)
            return dpll([clause for clause in clauses if pure not in clause and f'~{pure}' not in clause],
                        new_assignments, use_unit, use_pure)

    # Backtracking search
    chosen_literal = next(iter(clauses[0]))
    for option in (chosen_literal, f'~{chosen_literal}'):
        # Avoid adding contradictory assignments
        if (option.startswith('~') and option[1:] in assignments) or (not option.startswith('~') and f'~{option}' in assignments):
            continue
        new_assignments = assignments.copy()
        new_assignments.add(option)
        result = dpll([clause - {option} for clause in clauses if option not in clause],
                      new_assignments, use_unit, use_pure)
        if result is not None:
            return result

    return None


# Main function to read input, process clauses, and find a satisfying assignment
def main():
    input_lines = sys.stdin.readlines()
    clauses, atoms = parse_clauses(input_lines)
    # Initialize assignments as a set instead of a list for easier addition and removal.
    solution = dpll(clauses, set(), '--nounit' not in sys.argv, '--nopure' not in sys.argv)
    if solution is not None:
        # Ensure the solution considers all atoms. If an atom is not in the solution, it can be assigned False.
        formatted_solution = ' '.join(f'{atom}=T' if atom in solution else f'{atom}=F' for atom in atoms)
        print(f'satisfiable {formatted_solution}')
    else:
        print('unsatisfiable')

if __name__ == "__main__":
    main()
