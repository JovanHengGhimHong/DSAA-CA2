class SortedMap:
    def __init__(self, sorting_function=None):
        self.map = {}
        self.sorted_keys = []
        self.sorting_function = sorting_function

    def __setitem__(self, key, value):
        # sort regardless of capitalization
        if key not in self.map:
            self.sorted_keys.append(key)
            if self.sorting_function:
                self.sorted_keys.sort(key=self.sorting_function)
            else:
                self.sorted_keys.sort()
        self.map[key] = value

    def __getitem__(self, key):
        return self.map[key]

    def items(self):
        for key in self.sorted_keys:
            yield (key, self.map[key])
         