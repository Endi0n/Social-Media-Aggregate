class PostDraft:

    def __init__(self, request):
        self.__text = request.form.get('text', None)
        self.__files = request.files.getlist('files', None)
        pass

    @property
    def text(self):
        return self.__text

    @property
    def files(self):
        return self.__files
