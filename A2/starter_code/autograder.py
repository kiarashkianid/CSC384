#!/usr/bin/env python3
"""
Refactored Autograder for CSP Futoshiki Assignments.

Usage:
  python autograder.py
  python autograder.py --verbose
  python autograder.py --test test_simple_fc test_tiny_adder_fc

Runs a suite of tests for both CSP propagators (FC, GAC) and
Futoshiki CSP models (Model 1 and Model 2). Each test is a small,
self-contained function that returns (score, details, max_score).

All try/except blocks are done *outside* these test functions, so that each
test remains as lean as possible.
"""

import argparse
import signal
import traceback
import itertools
import io
import contextlib

import cspbase
import propagators as soln_propagators
from A2.starter_code.futoshiki_csp import futoshiki_csp_model_1, futoshiki_csp_model_2

TIMEOUT = 2000

#######################################
# UTILITIES & TIMEOUTS
#######################################
class TimeoutException(Exception):
    """Raised when time is up."""
    pass

def _timeout_handler(signum, frame):
    raise TimeoutException("Timeout occurred")

def set_timeout(seconds):
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)

def reset_timeout():
    """Disable alarm."""
    signal.alarm(0)

def contains_list(lst):
    return any(isinstance(e, list) for e in lst)

def sort_innermost_lists(lst):
    """
    Sort the innermost lists in a list-of-lists-of-lists recursively.
    Used for comparing nested lists ignoring order in the innermost layer.
    """
    if not isinstance(lst, list):
        return
    elif contains_list(lst):
        for e in lst:
            sort_innermost_lists(e)
    else:
        lst.sort()

def log(msg, verbose):
    if verbose:
        print(msg)

def w_eq_sum_x_y_z(values):
    w, x, y, z = values
    return w == (x + y + z)


#######################################
# TEST FUNCTIONS
#######################################
def example_csp_test(propagator, name=""):
    x = cspbase.Variable('X', [1, 2, 3])
    y = cspbase.Variable('Y', [1, 2, 3])
    z = cspbase.Variable('Z', [1, 2, 3])
    w = cspbase.Variable('W', [1, 2, 3, 4])

    c1 = cspbase.Constraint('C1', [x, y, z])
    # c1 is constraint x == y + z. Below are all of the satisfying tuples
    c1.add_satisfying_tuples([[2, 1, 1], [3, 1, 2], [3, 2, 1]])

    c2 = cspbase.Constraint('C2', [w, x, y, z])
    # c2 is constraint w == x + y + z.
    var_doms = []
    for v in [w, x, y, z]:
        var_doms.append(v.domain())

    sat_tuples = []
    for t in itertools.product(*var_doms):
        if w_eq_sum_x_y_z(t):
            sat_tuples.append(t)

    c2.add_satisfying_tuples(sat_tuples)

    simple_csp = cspbase.CSP("SimpleEqs", [x, y, z, w])
    simple_csp.add_constraint(c1)
    simple_csp.add_constraint(c2)

    btracker = cspbase.BT(simple_csp)
    # btracker.trace_on()

    set_timeout(TIMEOUT)
    btracker.bt_search(propagator)
    curr_vars = simple_csp.get_all_vars()
    answer = [[2], [1], [1], [4]]
    var_vals = [x.cur_domain() for x in curr_vars]
    reset_timeout()
    if var_vals != answer:
        details = "Failed while testing a propagator (%s): variable domains don't match expected results" % name
        return 0, details, 1
    else:
        return 1, "", 1
 

#######################################
# MAIN FUNCTION
#######################################
def main():
    parser = argparse.ArgumentParser(description="Run CSP Futoshiki autograder.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--test", "-t", nargs="+",
                        help="Specify one or more test names to run (e.g. test_simple_fc test_tiny_adder_fc). "
                             "If omitted, all tests will be run.")
    args = parser.parse_args()
    verbose = args.verbose

    print("Running Futoshiki/Propagators Autograder...\n")

    # Import student modules (fallback to solution modules if needed)
    try:
        import propagators as student_propagators
    except ImportError:
        print("Could not import student's propagators. Using solution_propagators as fallback.\n")
        student_propagators = soln_propagators

    try:
        import futoshiki_csp as student_models
    except ImportError:
        student_models = None
        
    # Helper function: run an individual test.
    # If verbose is not set, redirect output (stdout) to an in-memory buffer.
    def run_test(test_func, *test_args, test_name=""):
        try:
            with contextlib.redirect_stdout(io.StringIO()) if not verbose else contextlib.nullcontext():
                set_timeout(TIMEOUT)  # 10s timeout per test
                s, detail, ms = test_func(*test_args)
                reset_timeout()
            return s, detail, ms
        except TimeoutException:
            return 0, f"{test_name} - TIMEOUT", 1
        except Exception:
            tb = traceback.format_exc()
            return 0, f"{test_name} - RUNTIME ERROR:\n{tb}", 1

    # List of tests including an extra field for the test group
    # 
    tests = [
        (example_csp_test, student_propagators.prop_BT, "example_csp_test", "Other"),
    ]

    # If the user provided specific test names, filter out tests not matching those names.
    if args.test:
        specified = set(args.test)
        tests = [t for t in tests if t[2] in specified]
        if not tests:
            print("No matching tests found for the provided names. Exiting.")
            return

    # Initialize dictionaries to track scores per group.
    group_scores = {}
    group_maxes = {}
    overall_score = 0
    overall_max = 0

    # Run each test, and print a formatted result.
    for test_func, test_arg, test_name, test_group in tests:
        s, detail, ms = run_test(test_func, test_arg, test_name=test_name)
        overall_score += s
        overall_max += ms
        group_scores[test_group] = group_scores.get(test_group, 0) + s
        group_maxes[test_group] = group_maxes.get(test_group, 0) + ms

        # Determine status tag based on score
        if s == ms:
            status = "[PASSED]"
        elif s > 0:
            status = "[PARTIAL]"
        else:
            status = "[FAIL]"

        # If no details, print "None"
        detail_to_print = detail.strip() if detail.strip() else "None"

        # Print the test result in the desired format.
        print(f"{status} {test_name} ({test_group}) => score: {s}/{ms} details: {detail_to_print}")


    # Print out the scores by section.
    print("\n----- Scores by Section -----")
    print("FC Score: %d/%d" % (group_scores.get("FC", 0), group_maxes.get("FC", 0)))
    print("GAC Score: %d/%d" % (group_scores.get("GAC", 0), group_maxes.get("GAC", 0)))
    print("Model 1 Score: %d/%d" % (group_scores.get("Model 1", 0), group_maxes.get("Model 1", 0)))
    print("Model 2 Score: %d/%d" % (group_scores.get("Model 2", 0), group_maxes.get("Model 2", 0)))
    print("Ord MRV Score: %d/%d" % (group_scores.get("Ord", 0), group_maxes.get("Ord", 0)))
    print("Other Score: %d/%d" % (group_scores.get("Other", 0), group_maxes.get("Other", 0)))
    print("Total A3 Score: %d/%d" % (overall_score, overall_max))



def test_futoshiki_models():
    """
    Run tests for Futoshiki CSP models.
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

    for grid, desc in test_cases:
        print(f"Testing {desc} on Model 1...")
        csp1, vars1 = futoshiki_csp_model_1(grid)
        assert len(csp1.get_all_cons()) > 0, "Model 1 should have constraints."

        print(f"Testing {desc} on Model 2...")
        csp2, vars2 = futoshiki_csp_model_2(grid)
        assert len(csp2.get_all_cons()) > 0, "Model 2 should have constraints."

    print("All tests passed!")


if __name__ == "__main__":
    test_futoshiki_models()
