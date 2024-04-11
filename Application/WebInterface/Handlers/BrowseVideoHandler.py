from WebInterface.Handlers.RequestHandlerBase import RequestHandlerBase


from dataclasses import dataclass
from datetime import datetime, timedelta


class BrowseVideoHandler(RequestHandlerBase):

    def get(self, requestedText:str):
        self.logger.info(f'Request from IP="{self.request.remote_ip}" to browse video with request parameter="{requestedText}".')
        database = self.clipDatabase

        if requestedText.lower() == "today":
            requestedDateTime = self.clock.Now()
        elif requestedText.lower() == "yesterday":
            requestedDateTime = self.clock.Now() - timedelta(days=1)
        else:
            try:
                requestedDateTime = datetime.strptime(requestedText, '%y-%m-%d')
            except ValueError:
                self.send_error(404)
                return

        entries = database.GetEntriesOfDate(requestedDateTime)
        pastDate,futureDate = database.GetPreviousAndNextDate(requestedDateTime)

        @dataclass
        class EntryPayload:
            time: str
            duration: str
            id: str
            thumbnailLink: str
            videoLink: str

        @dataclass
        class Payload:
            videoEntries: list[EntryPayload]
            date: str
            linkRight: str
            linkLeft: str

        entriesPayload = [EntryPayload(time=x.DateOfRecording.strftime('%H:%M'),
                                       duration=f'{x.HighResClipDuration.total_seconds():.0f}',
                                       id=x.Id,
                                       thumbnailLink=f'/thumbnails/{x.Id}',
                                       videoLink=f'/watch/{x.Id}') for x in entries]

        linkRight = f'{(pastDate.strftime("%y-%m-%d"))}' if pastDate is not None else ''
        linkLeft = f'{(futureDate.strftime("%y-%m-%d"))}' if futureDate is not None else ''

        payload = Payload(videoEntries=entriesPayload,
                          date=requestedDateTime.strftime('%d.%m.%y'),
                          linkRight= linkRight,
                          linkLeft=linkLeft)
        path = self.config.WebInterface.Content.BrowseClipsHtml
        self.render(path,payload=payload)