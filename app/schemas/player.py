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
    name: str

    model_config = {
        "from_attributes": True
    }