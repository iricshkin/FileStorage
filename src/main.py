import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import healthcheck
from api.v1 import file, user
from core.config import app_settings
from services import my_logger

logger = my_logger.get_logger(__name__)

app = FastAPI(
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(file.router, prefix='/api/v1/files', tags=['files'])
app.include_router(user.router, prefix='/api/v1', tags=['users'])
app.include_router(healthcheck.router, tags=['healthcheck'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
    )
