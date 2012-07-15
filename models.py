# -*-: coding: utf-8 -*-
from mongoengine.document import Document
from mongoengine.fields import StringField, FloatField, ListField
from core.utils import *

from mongoengine import connect
from core.cache import cache

connect("parser_tag")

cache_key = 'TAG:'

class Tag(Document):
  name = StringField(max_length=36, unique=True)
  score = FloatField(default=1.0)
  friends = ListField(StringField(max_length=36), default=[])
  items = ListField(StringField(max_length=36), default=[])

  meta = {
    'indexes': ['name', ],
  }

  @classmethod
  def create(cls, name, *args, **kwargs):
    name = to_unicode(name)
    instance = cls(name=name, *args, **kwargs)
    try:
      instance.save()
    except Exception as err:
      print("Tag save err %s" %err)
      return None
    return instance

  @classmethod
  def get_or_create(cls, name):
    instance = cls.get_by_name(name)

    if not instance:
      return cls.create(name)

    return instance

  @classmethod
  def get_by_name(cls, name):
    try:
      instance = cls.objects.get(name=name)
    except:
      print("Can not find tag name %s" %name)
      return None

    return instance

  @classmethod
  def load_from_file(cls):
    path = 'data/tags'
    file = open(path, 'r')
    lines = file.readlines()
    file.close()

    for line in lines:
      name = to_unicode(line[:-1])
      instance = cls.create(name=name)

    print('Load Done')

  @classmethod
  def all_to_cache(cls):
    instances = cls.objects()
    for instance in instances:
      name = '%s%s' %(cache_key, instance.name)
      cache.zincrby(name=name, value=instance.name, amount=instance.score)
      for f in instance.friends:
        cache.zincrby(name=name, value=f)

    print("To cache Done")

  @classmethod
  def clear_cache(cls):
    keys = cache.keys('%s*' %cache_key)
    for key in keys:
      cache.delete(key)

    print("Delete Done")

  def get_friends(self):
    return self.friends

  def add_friend(self, name):
    friend = Tag.get_by_name(name)
    if not friend:
      self.__class__.create(name=name)

    self.update(add_to_set__friends=name)
    key = '%s%s' %(cache_key, self.name)
    cache.zincrby(name=key, value=name, amount=1)

  def get_info(self):
    key = '%s%s' %(cache_key, self.name)
    results = cache.zrevrangebyscore(name=key, min='-inf', max='+inf', withscores=False)
    return results

class Item(Document):
  name = StringField(max_length=36)