import logging
import inspect
import os


class CommonMixin:

    @classmethod
    def get_logger(cls):
        return logging.getLogger(__name__.split('.')[0] + '.' +
                                 os.path.basename(inspect.getsourcefile(cls)) + ':' + cls.__name__)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, id):
        try:
            probe = cls.objects.get(id=id)
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
    def get_nb_last(cls, nbr):
        try:
            objects = cls.objects.all()[:nbr]
        except IndexError:
            cls.get_logger().warning('Tries to access an object that does not exist', exc_info=True)
            return None
        return objects
