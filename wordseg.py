# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from mmseg import seg_txt
from core.cache import cache

TAG_CACHE_KEY = 'TAG:'
path = 'data/tags'

def to_unicode(word):
  if isinstance(word, (unicode, type(None))):
    return word
  try:
    return unicode(word, 'utf-8')
  except:
    return word

def to_str(word):
  if isinstance(word, basestring):
    return word
  elif isinstance(word, unicode):
    return word.encode('utf-8')
  return str(word)

class WordSeg:
  @classmethod
  def load_from_dict(cls, path=path):
    file = open(path, 'r')
    lines = file.readlines()
    for line in lines:
      line = to_unicode(line[:-1])
      key = '%s%s' %(TAG_CACHE_KEY, line.encode('utf-8'))
      if not cache.exists(key):
        cache.incr(key, amount=1)
    print("Done loads")
    file.close()

  @classmethod
  def to_file(cls, path=path):
    import codecs
    file = codecs.open(path, 'w+', 'utf-8')
    keys = cache.keys('%s*' %TAG_CACHE_KEY)
    for key in keys:
      name = key[4:]
      file.write('%s\n' %name.decode('utf-8'))
    file.close()

  @classmethod
  def clear_cache(cls):
    cache_key = '%s*' %TAG_CACHE_KEY
    keys = cache.keys(cache_key)
    for key in keys:
      cache.delete(key)

    print("Cache clear Done")

  @classmethod
  def is_keyword(cls, word):
    word_utf8 = to_unicode(word)
    key = '%s%s' %(TAG_CACHE_KEY, word_utf8)
    return cache.exists(key)

  @classmethod
  def parse(cls, words):
    import random
    tmp_key = 'TMP:KEY:%s' %str(int(float(random.random()*100000)))

    if isinstance(words, list):
      return []
    results = []
    words = to_str(words)
    for text in seg_txt(words):
      if cls.is_keyword(text):
        results.append(text)

    for r in results:
      cache.zincrby(name=tmp_key, value=r, amount=1)

    keywords = cache.zrevrangebyscore(name=tmp_key, min='-inf', max='+inf', withscores=True)
    cache.delete(tmp_key)
    return [keyword[0].decode('utf-8') + u'__' + str(keyword[1]).decode('utf-8') for keyword in keywords]

  @classmethod
  def add_keyword(cls, word):
    word_utf8 = to_unicode(word)
    key = '%s%s' %(TAG_CACHE_KEY, word_utf8)
    if not cls.is_keyword(word):
      cache.incr(key, amount=1)

if __name__ == '__main__':
  file = open('data/content', 'r')
  content = ''.join([to_unicode(line) for line in file.readlines()])
  keywords = WordSeg.parse(content.encode('utf-8'))
  for k in keywords:
    print(k)
  file.close()