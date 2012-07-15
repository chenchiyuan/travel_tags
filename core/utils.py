# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function
from core.cache import cache

def to_unicode(word):
  if isinstance(word, (unicode, type(None))):
    return word
  try:
    return unicode(word, 'utf-8')
  except Exception as err:
    print("Err is %s" %err)
    return word.encode('utf-8').decode('utf-8')

def to_str(word):
  if isinstance(word, unicode):
    return word.encode('utf-8')
  elif isinstance(word, str):
    return word
  else:
    return str(word)

def sum_list(list):
  import random
  key = str(int(random.random()*100000))

  for l in list:
    cache.zincrby(name=key, value=l, amount=1)

  results = cache.zrevrangebyscore(name=key, min='-inf', max='+inf', withscores=True)
  cache.delete(key)
  return results
  