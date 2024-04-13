import io
from WebInterface.Handlers.RequestHandlerBase import RequestHandlerBase


class ClipHandler(RequestHandlerBase):
    def get(self, requestedId:str):
        self.logger.debug(f'Request from IP="{self.request.remote_ip}" for video file of clip with id "{requestedId}".')

        database = self.clipDatabase
        entry = database.Get(requestedId)
        if entry is None:
            self.send_error(404)
            return

        path = entry.HighResClipFilePath
        movie = io.open(path, "rb").read()
        self.set_header('Content-type', 'video/mp4')
        self.set_header('Content-length', len(movie))
        self.write(movie)