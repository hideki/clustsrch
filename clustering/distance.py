#!/usr/bin/env python

import math
import itertools
import operator

def pearson(v1, v2):
    if len(v1) == 0:
        return 1.0

    # simple sums
    sum1 = sum(v1)
    sum2 = sum(v2)

    # sums of the squares
    sum1square = sum([pow(v, 2) for v in v1])
    sum2square = sum([pow(v, 2) for v in v2])

    # sum of the products
    sumproduct = sum([v1[i] * v2[i] for i in range(len(v1))])

    # calcurate r (pearson score)
    num = sumproduct - (sum1 * sum2 / len(v1))
    den = math.sqrt( (sum1square - pow(sum1,2) / len(v1)) * (sum2square - pow(sum2, 2) / len(v1) ) )

    if den == 0: return 0

    return 1.0 - num /den

def dotproduct(v1, v2):
    n = min(len(v1), len(v2))
    return sum([v1[i] * v2[i] for i in range(n)])

def cosine(v1, v2):
    dot = dotproduct(v1, v2)
    sum1square = sum([pow(v, 2) for v in v1])
    sum2square = sum([pow(v, 2) for v in v2])
    return dot / math.sqrt(sum1square * sum2square)


def euclidean(v1, v2):
    sum_square = 0.0
    # add up the squared disfferences
    for i in range(len(v1)):
        sum_square += pow((v1[i] - v2[i]), 2)
    # take the square root
    return math.sqrt(sum_square)

def main():
    print pearson([0.0,1.0,1.0,1.0],[0.0,0.0,1.0,2.0])    
    print euclidean([0.0,1.0,1.0,1.0],[0.0,0.0,1.0,2.0])    
    print dotproduct([0.0,1.0,1.0,1.0],[0.0,0.0,1.0,2.0])    
    print cosine([0.0,1.0,1.0,1.0],[0.0,0.0,1.0,2.0])    
    print cosine([0.9,0.4],[1.5,1.0])    
    print cosine([0.9, 0.4, 0.2],[1.5,1.0])    
    print cosine([0.5, 0.8, 0.3],[1.5,1.0])    

if __name__ == "__main__":
    main()
