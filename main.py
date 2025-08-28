import uvicorn
from app import create_app


proj_app = create_app()

if __name__ == '__main__':
    uvicorn.run("main:proj_app", host="0.0.0.0", port=7000, reload=True)