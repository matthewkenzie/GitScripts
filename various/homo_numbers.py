#!/usr/bin/env python

import math

#cache = {}
T_cache = {}

def sum_digits(n):
  s = 0
  while n:
    s += n % 10
    n //= 10
  return s

def quickerMethod( n ):
  hdigits = int(math.log10(n)+1)
  odd = hdigits%2
  hdigits //= 2

  s1 = 0
  s2 = 0

  for i in range(hdigits):
    s1 += n % 10
    n //= 10

  if odd: n //= 10

  for i in range(hdigits):
    s2 += n %10
    #if s2> s1: return False # quicker with this comparison removed
    n //= 10

  if s1==s2: return True
  else: return False

def getSumOfFirstLastDigits( number, verbose=False ):

  assert( type(number) is int )
  #global cache

  #if number < 0:
    #cache[number] = -1
    #return -1

  #if number in cache.keys():
    #return cache[number]

  st = str(number)
  ndigf = int(round(float(len(st))/2))
  ndigl = ndigf if len(st)%2==0 else ndigf-1

  sum_first_no2 = 0
  sum_last_no2 = 0

  if verbose: print 'i =', number, 'First Half = ', st[:ndigf], 'Last Half = ', st[ndigl:],

  # check pallendrome
  pall = True
  for n in range(ndigf+1):
    if st[n]!=st[-1-n]:
      pall = False
      break
  if pall:
    print 'Pallendrome'
    return 1

  for dig in st[:ndigf]:
    #print int(dig)
    sum_first_no2 += int(dig)

  if verbose: print 'SumF = ', sum_first_no2,

  for dig in st[ndigl:]:
    #print int(dig)
    sum_last_no2 += int(dig)
    if sum_last_no2 > sum_first_no2:
      #cache[number] = -1
      if verbose: print 'Not homogenous'
      return -1

  if verbose: print 'SumL = ', sum_last_no2,

  if sum_first_no2 == sum_last_no2:
    #cache[number] = sum_last_no2
    if verbose: print 'Homogenous sum = ', sum_first_no2
    return sum_first_no2
  else:
    #cache[number] = -1
    if verbose: print 'Not homogenous'
    return -1

def T(n, verbose=False):
  sum_homos = 0
  myn = 0
  for i in range(n-1,0,-1):
    if i in T_cache.keys():
      sum_homos = T_cache[i]
      myn = i
      break

  for i in range( 10**myn, 10**n ):
    #current_homo = getSumOfFirstLastDigits(i, verbose)
    current_homo = quickerMethod( i )
    if current_homo > 0:
      sum_homos += i

  T_cache[n] = sum_homos
  print 'T(%d) = '%n, sum_homos
  return sum_homos

import sys

if len(sys.argv)!=2:
  print 'Usage: python homo_numbers.py <n>'
  print '\t where n is the T(n) number you want to find'
  sys.exit()

maxn = int(sys.argv[1])
for i in range(1,maxn+1):
  T(i)
