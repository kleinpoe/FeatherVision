import tornado.web

from WebInterface.Handlers.RequestHandlerBase import RequestHandlerBase

class MainHandler(RequestHandlerBase):

    def get(self):
        config = self.config
        path = config.WebInterface.Content.IndexHtml
        self.render(path,fps=config.Camera.Fps,ip=config.WebInterface.Ip,port=config.WebInterface.Port)
        
        
        
        
    
        
        
        
        
        
            
        
            
              
        
        