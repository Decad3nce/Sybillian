from sybil import Sybil
from sybil import User

from database import Base, SybilObject
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

engine = create_engine('sqlite:///test.db', connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)


def database_session():
    conn = engine.connect()
    conn.connection.connection.text_factory = str
    return DBSession(bind=conn)


if __name__ == '__main__':
    session = database_session()
    user = User()
    user.id = '123123'
    user.screen_name = 'yolo_swaggins'
    user.created_at = 'March 25, 2006'
    user.location = 'San Francisco'

    data = {}
    data['score'] = 0.40

    sybil = Sybil(user)
    sybil.provide_bot_data(data)

    session.add(sybil.to_db_object())
    session.commit()

    sybil_unicode = Sybil(user)
    sybil_unicode.user_id = '2131424'
    sybil_unicode.screen_name = 'break_your_db'
    sybil_unicode.location = '\xc3\x9cT: 30.20751,-97.785319'
    data = {}
    data['score'] = 0.75
    sybil_unicode.provide_bot_data(data)

    session.add(sybil_unicode.to_db_object())
    session.commit()

    persisted_sybils = session.query(SybilObject).all()
    for sybil_object in persisted_sybils:
        new_sybil = Sybil.from_object(sybil_object)
        print new_sybil.detail()

    print sybil.detail()