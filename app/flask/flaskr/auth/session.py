import datetime
from flask import request
from flask_jwt_extended import decode_token, create_access_token
from jwt import ExpiredSignatureError
import uuid
import time
from typing import Tuple

from ..extensions import mongo


def get_session() -> Tuple[str, str]:
    """
    Determines current active session for request.
    Expired sessions will be deleted.
    If the session is within a certain threshold towards expiration, a new token is issued.

    Raises:
        ExpiredSignatureError: Error raised if token is expired

    Returns:
        tuple: session id, session token
    """
    access_token = None

    session = None

    try:

        token = request.headers.get("Authorization").split(sep=" ")[1]

        decoded_token = decode_token(token, allow_expired=True)

        session = decoded_token["sub"]

        expiration = decoded_token["exp"]

        current_time = time.time()

        if expiration < current_time:
            raise ExpiredSignatureError

        elif 300 > (expiration - current_time) > 0:
            expiration = datetime.timedelta(days=7)
            access_token = access_token = create_access_token(
                identity=session, expires_delta=expiration
            )
            print("Session refreshed:", session)

    except:
        print("No valid token found. \n")

        if session is not None:
            mongo.db.drop_collection(session+".chunks")
            mongo.db.drop_collection(session+".files")

        expiration = datetime.timedelta(days=7)
        session = str(uuid.uuid1())
        access_token = create_access_token(identity=session, expires_delta=expiration)

        print("New session: \n", session)

    return session, access_token
