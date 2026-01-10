class Dask:
  def __init__(self, expression, value, independent=False):
    self.expression = expression
    self.value = value
    self.independent = independent
  def __repr__(self):
    return f'{"".join(self.expression)}=> {self.value}'
  
class HashTable:
    def __init__(self , size):
        self.size = size
        self.keys = [None] * size
        self.buckets= [None] * size

    # this returns a index in my self.keys
    def hashKey(self , key):
      if isinstance(key , str):
        hash_sum = 0
        for char in key:
            hash_sum += ord(char)
      else:
        # just int key
        hash_sum = key

      # idk where i found this formula
      return (hash_sum * 2654435761) & 0xFFFFFFFF % self.size

    def items(self):
      return ((k, v) for k, v in zip(self.keys, self.buckets) if k is not None)


    def __setitem__(self , key , value):
        index = self.hashKey(key)
        start_index = index

        while True:
            # if empty we just use
            if self.keys[index] == None: 
                # assign the key to this index (hash)
                # assign value to same index
                self.keys[index] = key
                self.buckets[index] = value
                break

            # overwrite if same
            elif self.keys[index] == key:
                self.buckets[index] = value
                break
            
            # Find new key (we have hash collision)
            else:
                index = self.hashKey(index + 1) # +1 for linear progression

                if index == start_index:
                    # here we have considered the entire table
                    # we litterally cannot accomodate for any more key-value-pairs
                    break

    def __getitem__(self, key):
        # same idea of hashing and going over entire keys list
        index = self.hashKey(key)

        start_index = index


        while True:
            if self.keys[index] == key:
                return self.buckets[index]

            # there was collision during entry so we have to linearly cycle to the key
            else:
                index = self.hashKey(index + 1)

                if index == start_index:
                    return None 


    def __repr__(self):
        output_string = "{"
        for k, v in zip(self.keys, self.buckets):
            output_string += f'\n\t{k}:  {v}'
        return output_string + "\n}"



        




