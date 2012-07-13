# -*-: coding: utf-8 -*-
from mongoengine.document import Document
from mongoengine.fields import StringField, FloatField

class Tag(Document):
  name = StringField(max_length=36)
  score = FloatField(default=0.0)

class Item(Document):
  name = StringField(max_length=36)