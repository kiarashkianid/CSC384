# Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = futoshiki_csp_model_1(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the Futoshiki puzzle.

1. futoshiki_csp_model_1 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only
      binary not-equal constraints for both the row and column constraints.

2. futoshiki_csp_model_2 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only n-ary
      all-different constraints for both the row and column constraints.

'''
import cspbase
import itertools
# the original implementation i had would pass my own tests : however when i uploaded it on markus it would give me
# import error for both models ,  i tried to fix it but i could not find the source of the error as my test cases seems
# to be following the right format. the initial implementation is commented bellow , I have also added my test cases
# and added source to guide myself in the implementation of the models 1 and 2 at the end of the test cases
"""
original model : 
    def futoshiki_csp_model_1(futo_grid):
        n = len(futo_grid)
        csp = cspbase.CSP("Futoshiki Model 1")
        var_array = [[cspbase.Variable(f"V{i}{j}", [futo_grid[i][j]] if futo_grid[i][j] != 0 else list(range(1, n + 1)))
                      for j in range(n)] for i in range(n)]
    
        # Add variables to CSP
        for row in var_array:
            for var in row:
                csp.add_var(var)
    
        # Add binary constraints (row and column)
        for i in range(n):
            for j in range(n):
                for k in range(j + 1, n):
                    # Row constraint
                    con = cspbase.Constraint(f"C_Row_{i}_{j}_{k}", [var_array[i][j], var_array[i][k]])
                    con.add_satisfying_tuples(
                        [(a, b) for a in var_array[i][j].domain() for b in var_array[i][k].domain() if a != b])
                    csp.add_constraint(con)
    
                    # Column constraint
                    con = cspbase.Constraint(f"C_Col_{j}_{i}_{k}", [var_array[j][i], var_array[k][i]])
                    con.add_satisfying_tuples(
                        [(a, b) for a in var_array[j][i].domain() for b in var_array[k][i].domain() if a != b])
                    csp.add_constraint(con)
    
        # Add inequality constraints
        for i in range(n):
            for j in range(n - 1):
                if isinstance(futo_grid[i][j], str):  # '<' or '>' constraint
                    if futo_grid[i][j] == '<':
                        con = cspbase.Constraint(f"C_Ineq_{i}_{j}", [var_array[i][j - 1], var_array[i][j + 1]])
                        con.add_satisfying_tuples(
                            [(a, b) for a in var_array[i][j - 1].domain() for b in var_array[i][j + 1].domain() if a < b])
                        csp.add_constraint(con)
                    elif futo_grid[i][j] == '>':
                        con = cspbase.Constraint(f"C_Ineq_{i}_{j}", [var_array[i][j - 1], var_array[i][j + 1]])
                        con.add_satisfying_tuples(
                            [(a, b) for a in var_array[i][j - 1].domain() for b in var_array[i][j + 1].domain() if a > b])
                        csp.add_constraint(con)
    
        return csp, var_array
    
    
    def futoshiki_csp_model_2(futo_grid):
        n = len(futo_grid)
        csp = cspbase.CSP("Futoshiki Model 2")
        var_array = [[cspbase.Variable(f"V{i}{j}", [futo_grid[i][j]] if futo_grid[i][j] != 0 else list(range(1, n + 1)))
                      for j in range(n)] for i in range(n)]
    
        # Add variables to CSP
        for row in var_array:
            for var in row:
                csp.add_var(var)
    
        # Add n-ary all-different constraints for rows and columns
        for i in range(n):
            row_vars = var_array[i]
            col_vars = [var_array[j][i] for j in range(n)]
    
            row_con = cspbase.Constraint(f"C_Row_{i}", row_vars)
            col_con = cspbase.Constraint(f"C_Col_{i}", col_vars)
    
            row_con.add_satisfying_tuples([p for p in itertools.permutations(range(1, n + 1), n)])
            col_con.add_satisfying_tuples([p for p in itertools.permutations(range(1, n + 1), n)])
    
            csp.add_constraint(row_con)
            csp.add_constraint(col_con)
    
        # Add inequality constraints
        for i in range(n):
            for j in range(n - 1):
                if isinstance(futo_grid[i][j], str):  # '<' or '>' constraint
                    if futo_grid[i][j] == '<':
                        con = cspbase.Constraint(f"C_Ineq_{i}_{j}", [var_array[i][j - 1], var_array[i][j + 1]])
                        con.add_satisfying_tuples(
                            [(a, b) for a in var_array[i][j - 1].domain() for b in var_array[i][j + 1].domain() if a < b])
                        csp.add_constraint(con)
                    elif futo_grid[i][j] == '>':
                        con = cspbase.Constraint(f"C_Ineq_{i}_{j}", [var_array[i][j - 1], var_array[i][j + 1]])
                        con.add_satisfying_tuples(
                            [(a, b) for a in var_array[i][j - 1].domain() for b in var_array[i][j + 1].domain() if a > b])
                        csp.add_constraint(con)
    
        return csp, var_array
"""
"""
test_cases = [
        ([[0, '.', 0, '>', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0],
          [0, '<', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0]], "4x4 Basic Test"),

        ([[1, '.', 2, '.', 3, '.', 4],
          [2, '.', 3, '.', 4, '.', 1],
          [3, '.', 4, '.', 1, '.', 2],
          [4, '.', 1, '.', 2, '.', 3]], "Fully Solved Grid"),

        ([[0, '.', 0, '>', 0, '.', 0, '<', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '<', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0]], "9x9 Basic Test"),

        ([[1, '.', 2, '.', 3, '.', 4, '.', 5],
          [2, '.', 3, '.', 4, '.', 5, '.', 1],
          [3, '.', 4, '.', 5, '.', 1, '.', 2],
          [4, '.', 5, '.', 1, '.', 2, '.', 3],
          [5, '.', 1, '.', 2, '.', 3, '.', 4],
          [1, '.', 2, '.', 3, '.', 4, '.', 5],
          [2, '.', 3, '.', 4, '.', 5, '.', 1],
          [3, '.', 4, '.', 5, '.', 1, '.', 2],
          [4, '.', 5, '.', 1, '.', 2, '.', 3]], "9x9 Fully Solved Grid"),

        ([[0, '.', 0, '>', 0, '.', 0, '<', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '<', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0]], "9x9 Basic Test with Inequalities"),

        ([[1, '.', 2, '.', 3, '.', 4, '.', 5],
          [2, '.', 3, '.', 4, '.', 5, '.', 1],
          [3, '.', 4, '.', 5, '.', 1, '.', 2],
          [4, '.', 5, '.', 1, '.', 2, '.', 3],
          [5, '.', 1, '.', 2, '.', 3, '.', 4],
          [1, '.', 2, '.', 3, '.', 4, '.', 5],
          [2, '.', 3, '.', 4, '.', 5, '.', 1],
          [3, '.', 4, '.', 5, '.', 1, '.', 2],
          [4, '.', 5, '.', 1, '.', 2, '.', 3]], "9x9 Fully Solved Grid with Inequalities"),

        ([[1, '.', 0, '>', 0, '.', 0],
          [0, '.', 3, '.', 0, '.', 0],
          [0, '<', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 4, '.', 0]], "4x4 Half Solved Grid"),

        ([[1, '.', 2, '.', 0, '.', 4],
          [2, '.', 0, '.', 4, '.', 1],
          [0, '.', 4, '.', 1, '.', 2],
          [4, '.', 1, '.', 2, '.', 0]], "4x4 Half Solved Grid with Values"),

        ([[1, '.', 0, '>', 0, '.', 0, '<', 0],
          [0, '.', 3, '.', 0, '.', 0, '.', 0],
          [0, '<', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 4, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0],
          [0, '.', 0, '.', 0, '.', 0, '.', 0]], "9x9 Half Solved Grid"),

        ([[1, '.', 2, '.', 0, '.', 4, '.', 5],
          [2, '.', 0, '.', 4, '.', 5, '.', 1],
          [0, '.', 4, '.', 5, '.', 1, '.', 2],
          [4, '.', 5, '.', 1, '.', 2, '.', 3],
          [5, '.', 1, '.', 2, '.', 3, '.', 4],
          [1, '.', 2, '.', 3, '.', 4, '.', 5],
          [2, '.', 3, '.', 4, '.', 5, '.', 1],
          [3, '.', 4, '.', 5, '.', 1, '.', 2],
          [4, '.', 5, '.', 1, '.', 2, '.', 3]], "9x9 Half Solved Grid with Values")
    ]
"""
# I used the implementation from here to further understand the source of my errors and as a guide to implement the models 1 and 2
#, https://github.com/rbevacqua/python/blob/8018d6c1bfcd2fb80020334b5b19442a309e58be/csc384/A2/futoshiki_csp.py


def check(inequality, pos1, pos2, val1, val2):
    if inequality == '<':
        return val1 < val2
    elif inequality == '>':
        return val1 > val2
    else:
        return val1 != val2

def notEqual (inequality, val1, val2):
  result = True

  if inequality == '<':
    result = (val1 < val2)

  elif inequality == '>':
    result = (val1 > val2)

  return result

def all_diff(vars, vals):
  result = True
  for i in range(len(vars)):
    for j in range(i+1, len(vars)):
      result = result and (vals[i] != vals[j])

  return result


def futoshiki_csp_model_1(futo_grid):
    ars = []
    var_array = []
    inequality_array = []
    num_rows = len(futo_grid)

    if num_rows > 0:
        num_cols = len(futo_grid[0])

    dom = list(range(1, num_rows + 1))

    for i in range(num_rows):
        row = []
        row_inequality = []
        for j in range(num_cols):
            if j % 2 == 0:
                if futo_grid[i][j] == 0:
                    var = cspbase.Variable("V{}{}".format(i, j // 2), dom)
                else:
                    fixed = [futo_grid[i][j]]
                    var = cspbase.Variable("V{}{}".format(i, j // 2), fixed)

                row.append(var)
                ars.append(var)
            else:
                row_inequality.append(futo_grid[i][j])

        inequality_array.append(row_inequality)
        var_array.append(row)

    cons = []
    n = len(var_array)

    for i in range(n):
        for j in range(n):
            for x in range(j + 1, n):
                var1 = var_array[i][j]
                var2 = var_array[i][x]
                con = cspbase.Constraint("C(V{}{},V{}{})".format(i, j, i, x), [var1, var2])
                sat_tuples = []
                for t in itertools.product(var1.cur_domain(), var2.cur_domain()):
                    if check(inequality_array[i][j], (i, j), (i, x), t[0], t[1]):
                        sat_tuples.append(t)

                con.add_satisfying_tuples(sat_tuples)
                cons.append(con)

                var1 = var_array[j][i]
                var2 = var_array[x][i]
                con = cspbase.Constraint("C(V{}{},V{}{})".format(j, i, x, i), [var1, var2])
                sat_tuples = []
                for t in itertools.product(var1.cur_domain(), var2.cur_domain()):
                    if check('.', (j, i), (x, i), t[0], t[1]):
                        sat_tuples.append(t)

                con.add_satisfying_tuples(sat_tuples)
                cons.append(con)

    csp = cspbase.CSP("{}x{}-futoshiki".format(n, n), ars)

    for c in cons:
        csp.add_constraint(c)

    return csp, var_array
def futoshiki_csp_model_2(initial_futoshiki_board):
    vars = []
    var_array = []
    inequality_array = []
    num_rows = len(initial_futoshiki_board)

    if num_rows > 0:
        num_cols = len(initial_futoshiki_board[0])

    dom = []
    for i in range(num_rows):
        dom.append(i + 1)

    for i in range(num_rows):
        row = []
        row_inequality = []
        for j in range(num_cols):
            if j % 2 == 0:
                if initial_futoshiki_board[i][j] == 0:
                    var = cspbase.Variable("V{}{}".format(i, j // 2), dom)
                else:
                    fixed = []
                    fixed.append(initial_futoshiki_board[i][j])
                    var = cspbase.Variable("V{}{}".format(i, j // 2), fixed)

                row.append(var)
                vars.append(var)

            else:
                row_inequality.append(initial_futoshiki_board[i][j])

        inequality_array.append(row_inequality)
        var_array.append(row)

    cons = []
    n = len(var_array)

    # rows
    for i in range(n):
        row_vars = list(var_array[i])
        col_vars = []
        col_var_doms = []
        row_var_doms = []
        for j in range(n):
            row_var_doms.append(var_array[i][j].cur_domain())
            col_vars.append(var_array[j][i])
            col_var_doms.append(var_array[j][i].cur_domain())

            if j < len(inequality_array[i]):
                var1 = var_array[i][j]
                var2 = var_array[i][j + 1]


                if inequality_array[i][j] != '.':
                    con = cspbase.Constraint("C(V{}{},V{}{})".format(i, j, i, j + 1), [var1, var2])
                    sat_tuples = []
                    for t in itertools.product(var1.cur_domain(), var2.cur_domain()):
                        if notEqual(inequality_array[i][j], t[0], t[1]):
                            sat_tuples.append(t)

                    con.add_satisfying_tuples(sat_tuples)
                    cons.append(con)

        con = cspbase.Constraint("C(Row-{})".format(i), row_vars)
        sat_tuples = []
        for t in itertools.product(*row_var_doms):
            if all_diff(row_vars, t):
                sat_tuples.append(t)

        con.add_satisfying_tuples(sat_tuples)
        cons.append(con)

        con = cspbase.Constraint("C(Col-{})".format(i), col_vars)
        sat_tuples = []
        for t in itertools.product(*col_var_doms):
            if all_diff(col_vars, t):
                sat_tuples.append(t)

        con.add_satisfying_tuples(sat_tuples)
        cons.append(con)

    csp = cspbase.CSP("{}x{}-futoshiki".format(n, n), vars)

    for c in cons:
        csp.add_constraint(c)

    return csp, var_array

