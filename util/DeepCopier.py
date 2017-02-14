from collections import defaultdict


class DeepCopier(object):

    def __init__(self, target):
        """
        :type target: defaultdict
        """
        self._target = target

    def make_copy(self):
        copy = self._target.copy()
        for key in copy.keys():
            copy[key] = self._target[key].copy()
        return copy
