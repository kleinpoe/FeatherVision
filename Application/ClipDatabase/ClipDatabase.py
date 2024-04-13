from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import Logger
import os
from threading import Lock
from typing import Optional
import uuid
from tinydb import TinyDB, Query

from ClipDatabase.Serializers.TimeDeltaSerializer import TimeDeltaSerializer
from Video.ClipSaver import ClipSaver
from Config.Config import Config
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from tinydb.storages import JSONStorage

class ClipDatabase:
    def __init__(self, config: Config, logger: Logger):
        self.logger = logger
        self.config = config
        serialization = SerializationMiddleware(JSONStorage)
        serialization.register_serializer(DateTimeSerializer(), 'DateTime')
        serialization.register_serializer(TimeDeltaSerializer(), 'TimeDelta')
        self.database = TinyDB(config.Database.ClipDatabaseFilePath, storage = serialization)
        self.lock = Lock()
        with self.lock:
            self.memoryStorage = self.loadAll(self.database)
    
    def loadAll(self, database: TinyDB) -> dict[str,'ClipDatabase.Entry']:
        dicts = database.all()
        entries = dict((sorted([(x['Id'],ClipDatabase.Entry.FromDictionary(x)) for x in dicts], key=lambda y: y[1].DateOfRecording)))
        return entries
        
    def Add(self, clip: ClipSaver.Result):
        identifier = str(uuid.uuid4())
        entry = ClipDatabase.Entry.FromClipSaverResult(clip,identifier)
        with self.lock:
            self.memoryStorage[identifier] = entry
            self.memoryStorage = dict((sorted(self.memoryStorage.items(), key=lambda x: x[1].DateOfRecording)))
            self.database.insert(entry.__dict__)
            
    def Remove(self, entry: 'ClipDatabase.Entry'):
        self.Remove(entry.Id)
            
    def Remove(self, id:str) -> None:
        # Todo delete files
        if id not in self.memoryStorage.keys:
            self.logger.warn(f'Cannot Remove Clip with id "{id}". It does not exist.')
        with self.lock:
            removedItem = self.memoryStorage.pop(id)
            query = Query()
            self.database.remove(query.Id == id)
        os.remove(removedItem.AnnotatedClipFilePath)
        os.remove(removedItem.ThumbnailFilePath)
        os.remove(removedItem.HighResClipFilePath)
            
    def RemoveOlderThan(self, datetime:datetime) -> None:
        with self.lock:
            entries = [x for x in self.memoryStorage.values() if x.DateOfRecording < datetime]
        for entry in entries:
            self.Remove(entry)
        
    def Get(self, id:str)->Optional['ClipDatabase.Entry']:
        with self.lock:
            entry = self.memoryStorage.get(id)
        return entry
    
    def GetNewest(self)->Optional['ClipDatabase.Entry']:
        with self.lock:
            entry = max(self.memoryStorage.values(), key=lambda x: x.DateOfRecording, default=None)
        return entry
    
    def GetPreviousAndNext(self, entry: 'ClipDatabase.Entry')->tuple[Optional['ClipDatabase.Entry'],Optional['ClipDatabase.Entry']]:
        with self.lock:
            values = list(self.memoryStorage.values())
        idx = values.index(entry)
        nextEntry = values[idx+1] if len(values) > idx+1 else None
        previousEntry = values[idx-1] if idx > 0 else None
        return (previousEntry, nextEntry)
    
    def GetEntriesOfDate(self, date: datetime)->list['ClipDatabase.Entry']:
        with self.lock:
            entries = [x for x in self.memoryStorage.values() if x.DateOfRecording.date() == date.date()]
        return entries
    
    def GetPreviousAndNextDate(self, datetime: datetime)->tuple[Optional[datetime],Optional[datetime]]:
        date =  datetime.date()
        # Todo optimize
        with self.lock:
            dateInFuture = next((x for x in self.memoryStorage.values() if x.DateOfRecording.date() > date), None)
            dateInPast = next((x for x in reversed(self.memoryStorage.values()) if x.DateOfRecording.date() < date), None)
        return dateInPast.DateOfRecording.date() if dateInPast is not None else None,dateInFuture.DateOfRecording.date() if dateInFuture is not None else None

    @dataclass
    class Entry:
        DateOfRecording: datetime
        HighResClipDuration: timedelta
        HighResClipFilePath: str
        AnnotatedClipFilePath: str
        ThumbnailFilePath: str
        Id: str
        
        @classmethod
        def FromClipSaverResult(cl, clipSaverResult: ClipSaver.Result, identifier:str) -> 'ClipDatabase.Entry':
            entry = ClipDatabase.Entry(DateOfRecording=clipSaverResult.DateOfRecording,
                                       HighResClipDuration=clipSaverResult.ClipDuration,
                                       HighResClipFilePath=clipSaverResult.HighResClipFilePath,
                                       AnnotatedClipFilePath=clipSaverResult.AnnotatedClipFilePath,
                                       ThumbnailFilePath=clipSaverResult.ThumbnailFilePath,
                                       Id=identifier)
            return entry
        
        @classmethod
        def FromDictionary(cl, dictionary: ClipSaver.Result) -> 'ClipDatabase.Entry':
            entry = ClipDatabase.Entry(None,None,None,None,None,None)
            entry.__dict__ = dictionary
            return entry

        