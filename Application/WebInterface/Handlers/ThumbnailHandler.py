from WebInterface.Handlers.RequestHandlerBase import RequestHandlerBase


import io


class ThumbnailHandler(RequestHandlerBase):
    def get(self, requestedId:str):
        self.logger.debug(f'Request from IP="{self.request.remote_ip}" for thumbnail of clip with id "{requestedId}".')

        database = self.clipDatabase
        entry = database.Get(requestedId)
        if entry is None:
            self.logger.warn(f'Request from IP="{self.request.remote_ip}" for thumbnail of clip with id "{id}". Id was not found!')
            self.send_error(404)
            return

        path = entry.ThumbnailFilePath
        img = io.open(path, "rb").read()
        self.set_header('Content-type', 'image/jpg')
        self.set_header('Content-length', len(img))
        self.write(img)