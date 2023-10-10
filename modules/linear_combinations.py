import numpy as np

def linear_combinations(step):
    combinations = []
    for i in np.arange(0, 1+step, step):
        for j in np.arange(0, 1-i+step, step):
            k = 1.0 - i - j
            i_rounded, j_rounded, k_rounded = round(i, 2), round(j, 2), round(k, 2)

            # Check if k_rounded is within valid range and the summation equals 1.0
            if 0 <= k_rounded <= 1 and i_rounded + j_rounded + k_rounded == 1.0:
                combinations.append([i_rounded, j_rounded, k_rounded])

    return combinations