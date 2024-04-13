from WebInterface.Handlers.RequestHandlerBase import RequestHandlerBase


import json


class DeleteClipsHandler(RequestHandlerBase):
    def post(self):
        data = json.loads(self.request.body)
        videoIdsToDelete = data['videosIdsToDelete']
        self.logger.info(f'Request from IP="{self.request.remote_ip}" to delete videos with IDs={videoIdsToDelete}".')
        database = self.clipDatabase
        for id in videoIdsToDelete:
            database.Remove(id)