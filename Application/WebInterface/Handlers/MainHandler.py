from datetime import datetime, timedelta
import tornado.web
import os

from WebInterface.Handlers.RequestHandlerBase import RequestHandlerBase

class MainHandler(RequestHandlerBase):

    def get(self):
        config = self.config
        path = os.path.join(config.WebInterface.Content.IndexHtml)
        self.render(path,fps=config.Camera.Fps,ip=config.WebInterface.Ip,port=config.WebInterface.Port)
        
class WatchVideoHandler(RequestHandlerBase):
    def get(self, id:str):
        self.logger.info(f'Request from IP="{self.request.remote_ip}" to watch video with ID="{id}".')
        database = self.clipDatabase
        entry = database.Get(id)
        if entry is None:
            self.logger.warn(f'Request from IP="{self.request.remote_ip}" to watch video with ID="{id}". Id was not found!')
            return
        (prev,next) = database.GetPreviousAndNext(entry)
        print(f'Requested {entry} | < {next} | > {prev}')
        
        
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
        
        entries = database.GetEntriesOfDate(requestedDateTime)
        
        if(len(entries) == 0):
            self.send_error(404)
            
              
        
        