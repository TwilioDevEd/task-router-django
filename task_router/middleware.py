

class AppendSlashWithoutRedirect:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path_info.endswith('/'):
            request.path += '/'
            request.path_info += '/'
        return self.get_response(request)
