from main import app
from config import app_config

import uvicorn


if __name__ == "__main__":
    uvicorn.run(app, host=app_config["host"], port=app_config["port"])
