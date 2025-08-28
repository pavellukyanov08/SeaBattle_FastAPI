from pydantic import BaseModel


class PlayerRegister(BaseModel):
    username: str
    password: str


class PlayerRead(BaseModel):
    id: str
    name: str
    is_playing: bool

    model_config = {
        "from_attributes": True
    }


class PlayerResponse(BaseModel):
    username: str

    model_config = {
        "from_attributes": True
    }