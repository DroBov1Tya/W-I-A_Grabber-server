import os
import logging
import motor.motor_asyncio
from enum import Enum
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from fastapi_offline import FastAPIOffline
from fastapi import FastAPI
from typing import Any, Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

debug: str = os.getenv('FASTAPI_DEBUG')
apikey: str = os.getenv('FASTAPI_KEY')
mongodb_dsn: str = os.getenv('MONGODB_DSN')
db_mongo:str = os.getenv('MONGODB_DB')

# VARS # 
SECRET_VALUE: str = apikey
SECRET_HEADER: str = 'X-API-Key'


docs_title: str = 'Apps API'
docs_description: str = 'Не лезь, убьёт!'

class Tags(Enum):
    apps = "Apps"


def auth401():
    X_API_KEY = APIKeyHeader(name=SECRET_HEADER)

    def api_key_auth(x_api_key: str = Depends(X_API_KEY)):
        if x_api_key != SECRET_VALUE:
            raise HTTPException(status_code=401, detail="Invalid API Key")

    auth_dep = [Depends(api_key_auth)]
    return auth_dep

def api_init():
    """
    Инициализирует и возвращает экземпляр FastAPI с учетом режима отладки.

    Args:
        debug (bool): Флаг, указывающий, находится ли приложение в режиме отладки.
        docs_title (str): Заголовок документации API.
        docs_description (str): Описание документации API.

    Returns:
        FastAPI: Экземпляр FastAPI с соответствующими настройками.
    """
    if debug == "TRUE":
        app = FastAPIOffline(
            title=docs_title,
            description=docs_description
        )
        logging.info("FastAPI app initialized in debug mode.")
    else:
        app = FastAPIOffline(
        dependencies = auth401(),
        title = docs_title,
        description = docs_description,
        )

    return app

# motor wrapper
class MongoDB:
    def __init__(self):
        self.mongo = None
        self.db = None

    async def connect(self, db_name):
        if self.mongo is None:
            self.mongo = motor.motor_asyncio.AsyncIOMotorClient(mongodb_dsn)
        self.db = self.mongo[db_name]
        return self.db

    async def insert_one(self, collection_name, document):
        collection = self.db[collection_name]
        result = await collection.insert_one(document)
        return result.inserted_id

    async def find_one(self, collection_name, query):
        collection = self.db[collection_name]
        document = await collection.find_one(query)
        return document

    async def find(self, collection_name, query):
        collection = self.db[collection_name]
        document = await collection.find_one(query)
        return document

    async def delete_one(self, collection_name, query):
        collection = self.db[collection_name]
        result = await collection.delete_one(query)
        return result.deleted_count

    async def check_table(self, table_name): # table_name means collecetion name
        list_of_collections = await self.db.list_collection_names()
        return table_name in list_of_collections

    async def delete_table(self, table_name): # table_name means collecetion name
        collection = self.db[table_name]
        await collection.drop()


    async def close(self):
        if self.mongo is not None:
            self.mongo.close()

    async def find_filtered(self, collection_name):
        collection = self.db[collection_name]
        
        # Фильтр для поиска документов, где from_user._ = "User"
        filter_criteria = {
            "from_user._": "User"
        }
        
        # Проекция, исключающая _id, from_user._, и chat._
        projection = {
            "_id": 0,
            "id": 1,
            # "from_user._": 0,
            # "chat._": 0,
            "from_user.id": 1,
            "from_user.is_support": 1,
            "from_user.is_premium": 1,
            "from_user.first_name": 1,
            "from_user.username": 1,
            "date": 1,
            "reply_to_message_id": 1,
            "reply_to_top_message_id": 1,
            "text": 1,
            "outgoing": 1,
            "web_page.display_url": 1,
            "web_page.type": 1,
            "web_page.title": 1,
            "web_page.description": 1,
            "forward_from_chat.title": 1,
            "forward_from_message_id": 1,
            "forward_date": 1,
            "edit_date": 1,
            "views": 1,
            "forwards": 1,
            "caption_entities.url": 1
        }
        
        cursor = collection.find(filter_criteria, projection)
        return await cursor.to_list(length=None)