import logging
import inspect
import os
import shutil
import time
from contextlib import contextmanager

from django.conf import settings


class CommonMixin:

    @classmethod
    def get_logger(cls):
        return logging.getLogger(__name__.split('.')[0] + '.' +
                                 os.path.basename(inspect.getsourcefile(cls)) + ':' + cls.__name__)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, key):
        try:
            probe = cls.objects.get(id=key)
        except cls.DoesNotExist:
            cls.get_logger().warning('Tries to access an object that does not exist', exc_info=True)
            return None
        return probe

    @classmethod
    def get_last(cls):
        try:
            obj = cls.objects.last()
        except cls.DoesNotExist:
            cls.get_logger().warning('Tries to access an object that does not exist', exc_info=True)
            return None
        return obj

    @classmethod
    def get_nbr(cls, nbr):
        try:
            objects = cls.objects.all()[:nbr]
        except IndexError:
            cls.get_logger().warning('Tries to access an object that does not exist', exc_info=True)
            return None
        return objects

    @classmethod
    @contextmanager
    def get_tmp_dir(cls, folder_name=None):
        if folder_name:
            tmp_dir = settings.BASE_DIR + '/tmp/' + cls.__name__ + '/' + str(folder_name) + '/' + str(time.time()) + '/'
        else:
            tmp_dir = settings.BASE_DIR + '/tmp/' + cls.__name__ + '/' + str(time.time()) + '/'
        try:
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            yield tmp_dir
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
