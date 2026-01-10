class SortedMap:
    def __init__(self):
        self.map = {}
        self.sorted_keys = []

    def __setitem__(self, key, value):
        # sort regardless of capitalization
        if key not in self.map:
            self.sorted_keys.append(key)
            self.sorted_keys.sort(key=lambda x: x.lower())
        self.map[key] = value

    def __getitem__(self, key):
        return self.map[key]

    def items(self):
        for key in self.sorted_keys:
            yield (key, self.map[key])
         