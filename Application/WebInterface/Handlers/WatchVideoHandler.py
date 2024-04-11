from WebInterface.Handlers.RequestHandlerBase import RequestHandlerBase


from dataclasses import dataclass


class WatchVideoHandler(RequestHandlerBase):
    def get(self, id:str):
        self.logger.info(f'Request from IP="{self.request.remote_ip}" to watch video with ID="{id}".')
        database = self.clipDatabase
        entry = database.Get(id)
        if entry is None:
            self.logger.warn(f'Request from IP="{self.request.remote_ip}" to watch video with ID="{id}". Id was not found!')
            return
        (prev,next) = database.GetPreviousAndNext(entry)

        @dataclass
        class Payload:
            date: str
            time: str
            linkRight: str
            linkLeft: str
            id: str

        payload = Payload(date=entry.DateOfRecording.strftime("%d.%m.%y"),
                          time=entry.DateOfRecording.strftime("%H:%M"),
                          linkLeft=f"/watch/{prev.Id}",
                          linkRight=f"/watch/{next.Id}",
                          id=entry.Id)
        path = self.config.WebInterface.Content.WatchClipHtml
        self.render(path,payload=payload)