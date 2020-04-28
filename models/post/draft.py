class PostDraft:

    def __init__(self, request):
        self.__text = request.form.get('text', '')
        self.__files = request.files.getlist('files[]', None)
        self.__files_url = request.form.getlist('files_url[]', None)

    @property
    def text(self):
        return self.__text

    @property
    def files(self):
        return self.__files

    @property
    def files_url(self):
        return self.__files_url
