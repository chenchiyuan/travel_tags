# -*-: coding: utf-8 -*-
__author__ = 'chenchiyuan'

from mmseg import seg_txt
from django.template.defaultfilters import slugify
from unidecode import unidecode
import logging
logger = logging.getLogger('default')

SEARCH_KEY_PREFIX = 'TAG:SEARCH:'

class SearchIndex(object):
    def __init__(self):
        self.cache_key_prefix = SEARCH_KEY_PREFIX

    @staticmethod
    def cache_key_prefix():
        return SEARCH_KEY_PREFIX

    @staticmethod
    def __to_unicode(word):
        if isinstance(word, (unicode, type(None))):
            return word.encode('utf-8')
        try:
            return unicode(word, 'utf-8')
        except:
            return word.encode('utf-8')

    @staticmethod
    def score(word):
        logger.debug("will score a word %s" %word)

    def parse(self, words):
        words = SearchIndex.__to_unicode(words)
        _seg_words = [word for word in seg_txt(words)]
        seg_words = filter(None, _seg_words)
        results = []
        for word in seg_words:
            word_utf8 = SearchIndex.__to_unicode(word)
            decode_word = unidecode(word_utf8)
            key = self.cache_key_prefix + slugify(decode_word)
            results.append(key)
        return results


    def add(self, word, key, score):
        try:
            cache.zadd(word, score, key)
        except:
            logger.debug("cannot add search index key: %s score: %s" %(key, score))

    def get(self, word):
        try:
            return cache.zrevrangebyscore(name=self.cache_key_prefix + word, max='+inf', min="-inf")
        except Exception as err:
            logger("cache_key %s for err %s" %(self.cache_key_prefix + word, err))
            return None

    def search(self, words):
        keys = self.parse(words)
        try:
            cache_words = slugify(unidecode(words))
            cache.zinterstore(dest=self.cache_key_prefix + cache_words, keys=keys)
        except Exception as err:
            logger.error("Err is %s" %err)
            return None

        cache_keys = cache.zrevrangebyscore(self.cache_key_prefix + cache_words, "+inf", "-inf")
        tags = []
        for cache_key in cache_keys:
            tags.append(cache.hgetall(cache_key))
        tags = filter(None, tags)
        return {
            words: tags
        }

    def add_tag(self, tag):
        if not tag:
            return
        words = self.parse(tag.name_zh)
        words.extend(tag.name_en)
        for word in words:
            self.add(word=word, key=tag.cache_key, score=tag.score)
