#!/usr/bin/env python

#cache = {}
T_cache = {}

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
    current_homo = getSumOfFirstLastDigits(i, verbose)
    if current_homo > 0:
      sum_homos += i

  T_cache[n] = sum_homos
  print 'T(%d) = '%n, sum_homos
  return sum_homos

#for i in range(101):
  #print i, getSumOfFirstLastDigits(i, False)
#st = str(i)
#ndigf = int(round(float(len(st))/2))
#ndigl = ndigf if len(st)%2==0 else ndigf-1
#print i, st[:ndigf], st[ndigl:]

#getSumOfFirstLastDigits(22,True)
import sys
maxn = int(sys.argv[1])
for i in range(1,maxn+1):
  T(i)
