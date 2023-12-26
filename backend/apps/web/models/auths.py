from pydantic import BaseModel
from typing import List, Union, Optional
import time
import uuid
from peewee import *


from apps.web.models.users import UserModel, Users
from utils.utils import (
    verify_password,
    get_password_hash,
    bearer_scheme,
    create_token,
)

from apps.web.internal.db import DB

####################
# DB MODEL
####################


class Auth(Model):
    id = CharField(unique=True)
    email = CharField()
    password = CharField()
    active = BooleanField()

    class Meta:
        database = DB


class AuthModel(BaseModel):
    id: str
    email: str
    password: str
    active: bool = True


####################
# Forms
####################


class Token(BaseModel):
    token: str
    token_type: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    profile_image_url: str


class SigninResponse(Token, UserResponse):
    pass


class SigninForm(BaseModel):
    email: str
    password: str


class SignupForm(BaseModel):
    name: str
    email: str
    password: str


class AuthsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Auth])

    def insert_new_auth(
        self, email: str, password: str, name: str, role: str = "pending"
    ) -> Optional[UserModel]:
        print("insert_new_auth")

        id = str(uuid.uuid4())

        auth = AuthModel(
            **{"id": id, "email": email, "password": password, "active": True}
        )
        result = Auth.create(**auth.model_dump())
        print(result)

        user = Users.insert_new_user(id, name, email, role)

        print(result, user)
        if result and user:
            return user
        else:
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        print("authenticate_user", email)

        auth = Auth.get(Auth.email == email, Auth.active == True)
        print(auth.email)

        if auth:
            print(password, str(auth.password))
            print(verify_password(password, str(auth.password)))
            if verify_password(password, auth.password):
                user = Users.get_user_by_id(auth.id)

                print(user)
                return user
            else:
                return None
        else:
            return None


Auths = AuthsTable(DB)
