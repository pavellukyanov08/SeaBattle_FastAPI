from fastapi import FastAPI

from app.api import auth, player, game


def create_app():
    app = FastAPI(
        title="Игра 'Морской бой'"
    )

    @app.get("/")
    async def root():
        return {"message": "Добро пожаловать в 'Морской бой'"}

    app.include_router(auth.router)
    app.include_router(player.router)
    app.include_router(game.router)

    return app