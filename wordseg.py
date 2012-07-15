# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function
from core.cache import cache
from mmseg import _mmseg as seg
from os.path import join, dirname
from models import Tag
from core.utils import *

####  load dict for mmseg ####

seg.dict_load_chars(join(dirname(__file__), 'data', 'chars.dic'))
seg.dict_load_words(join(dirname(__file__), 'data', 'words.dic'))

def seg_txt(text):
    if type(text) is str:
        algor = seg.Algorithm(text)
        for tok in algor:
            yield tok.text
    else:
        yield ""

def tags_to_dict():
  file = open('data/tags', 'r')
  lines = file.readlines()
  file.close()

  output = open('data/words.dic', 'a')
  for line in lines:
    line = line[-1]
    output.write('%d %s\n' %(len(line)/3, line))
  output.close()

  print('Tags to dict Done!')

#########################

TAG_CACHE_KEY = 'TAG:'
path = 'data/tags'
class WordSeg:
  '''
  words is utf-8 coding, load it to cache, when parse it, convert it to str .Atfer seg, decode to utf-8.
  '''
  @classmethod
  def load_from_dict(cls, path=path):
    file = open(path, 'r')

    lines = file.readlines()
    for line in lines:
      line = to_unicode(line[:-1])
      key = '%s%s' %(TAG_CACHE_KEY, line)
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

    print("C ache clear Done")

  @classmethod
  def is_keyword(cls, word):
    word_utf8 = to_unicode(word)
    key = '%s%s' %(TAG_CACHE_KEY, word_utf8)
    return cache.exists(key)

  @classmethod
  def parse(cls, words):
    import random
    if isinstance(words, list):
      return []

    tmp_key = 'TMP:KEY:%s' %str(int(float(random.random()*100000)))
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
  content = ''.join([unicode(line, 'utf-8') for line in file.readlines()])
  file.close()

  keywords = WordSeg.parse(content)

  originals = [keyword.split('__')[0] for keyword in keywords]
  friends = []
  for o in originals:
    tag = Tag.get_or_create(o)
    friends.extend(tag.friends)

  friends = sum_list(friends)

  print("Original tags")
  for k in keywords:
    print(k)

  print("Friends tags")
  for f in friends:
    print(to_unicode(f[0]) + u'__' + unicode(f[1]))