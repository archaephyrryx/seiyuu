from collections import defaultdict

'''AssocMap:
    a specialized data structure that associates a set of unique integer 'ID' with
    string-based 'labels' for the abstract item given that ID value.
    Every ID registered can correspond to one label, but a given label may be shared by
    multiple items with different IDs.

    Actual implementation maintains a forward- and reverse-lookup dictionary,
    one mapping IDs to labels, and another mapping labels to sets of IDs
'''
class AssocMap:
    def __init__(self):
        self.id_to_label = dict()
        self.label_to_id = defaultdict(set)

    def __add_assoc(self, iden: int, label: str):
        self.id_to_label[iden] = label
        self.label_to_id[label].add(id)

    def add_assoc(self, iden: int, label: str):
        if iden not in self.id_to_label:
            self.__add_assoc(iden, label)

    def lookup_by_id(self, iden: int):
        if iden in self.id_to_label:
            return self.id_to_label[iden]
        else:
            raise KeyError

    def lookup_by_label(self, label: str):
        if label in self.label_to_id:
            return self.label_to_id[label]
        else:
            raise KeyError
