class VariableDb:
    _items = {}

    def __getitem__(self, key):
        return self._items.get(key, 0) if self._items is not None else 0

    def __setitem__(self, key, value):
        if value is not None:
            self._items[key] = value
        else:
            del self._items[key]

    def __delitem__(self, key):
        del self._items[key]

    def clear(self):
        self._items.clear()
