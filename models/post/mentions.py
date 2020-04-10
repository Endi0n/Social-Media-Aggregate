class UserMention:

    def __init__(self, id, name=None, tag=None):
        self.__id = id
        self.__name = name
        self.__tag = tag

    def as_dict(self):
        user = {'id': self.__id}

        if self.__name:
            user['name'] = self.__name

        if self.__tag:
            user['tag'] = self.__tag

        return user
