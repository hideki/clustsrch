#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

def mi(N11, N01, N10, N00):
  """
  N00 - The number of documents that does not contain t(et=0), and are not in c(ec=0)
  N01 - The number of documents that does not contain t(et=0), and are in c(ec=1)
  N10 - The number of documents that contain t(et=1), and are not in c(ec=0). 
  N11 - The number of documents that contains t(et=1), and are in c(ec=1)
  N  = N00 + N01 + N10 + N11 - total document
  """
  if N00 <= 0.0 or N01 <= 0.0 or N10 <= 0.0 or N11 <= 0.0:
    return 0.0;

  N = N00 + N01 + N10 + N11
  score = 0.0
  score += ( N11 / N ) * math.log( N * N11 / ((N11 + N10) * (N11 + N01)), 2) 
  score += ( N01 / N ) * math.log( N * N01 / ((N01 + N00) * (N11 + N01)), 2)
  score += ( N10 / N ) * math.log( N * N10 / ((N10 + N11) * (N10 + N00)), 2)
  score += ( N00 / N ) * math.log( N * N00 / ((N01 + N00) * (N10 + N00)), 2)
  return score

def main():
  print "TEST 1:"
  print "\t0.000105 =? %.6f" % mi(49.0, 27652.0, 141.0, 774106.0)

if __name__ == '__main__':
  main()
