

class WeightsMatrixParser(object):

    def __init__(self, weight_map):
        self.weight_map = weight_map

    def read_matrix_from(self, file_name):

        def parse(entry):
            args = entry.split(':')
            weight = float(args[1])
            args = args[0].split('-')
            s1 = int(args[0])
            s2 = int(args[1])
            self.weight_map[s1][s2] = weight
            self.weight_map[s2][s1] = weight

        try:
            with open(file_name, 'r') as f:
                entries = f.readlines()
        except IOError as e:
            print e.message
            return

        for entry in entries:
            parse(entry)
