import time
import tweepy
import botornot
from responder import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_SECRET, ACCESS_TOKEN
from sybil import Sybil
from database import Base, SybilObject
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

twitter_app_auth = {
    'consumer_key': CONSUMER_KEY,
    'consumer_secret': CONSUMER_SECRET,
    'access_token': ACCESS_TOKEN,
    'access_token_secret': ACCESS_SECRET,
}
bon = botornot.BotOrNot(**twitter_app_auth)
engine = create_engine('sqlite:///test.db', connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)


def database_session():
    conn = engine.connect()
    conn.connection.connection.text_factory = str
    return DBSession(bind=conn)


class SybilPopulator(object):

    def __init__(self, api):
        self.api = api
        self.sybil_database = SybilDatabase()

    def process_many(self, user_ids):
        """
        Process many user id's to get meta data about the accounts as well as bot classification.

        :param user_ids:
        :return: list of Sybil(s)
        """
        print 'Processing {} length of {}'.format(user_ids, len(user_ids))
        sybils = {}
        for user_id in user_ids:
            print 'Checking if {} is in knowledge base'.format(user_id)
            known_sybil = self.sybil_database.get_sybil_for_id(user_id)
            if known_sybil:
                print 'Adding {} to processed sybils'.format(known_sybil.screen_name)
                sybils[known_sybil.screen_name] = known_sybil
                print 'Removing {} from user id process count'.format(user_id)
                user_ids.remove(user_id)

        if len(user_ids) > 0:
            print 'Looking up users via tweepy'
            users = self.api.lookup_users(user_ids=user_ids)
            accounts_to_check = list()

            for user in users:
                print 'Creating new sybil'
                new_sybil = Sybil(user)
                print 'Created new sybil {}'.format(new_sybil.screen_name)
                sybils[new_sybil.screen_name] = new_sybil
                accounts_to_check.append(new_sybil.screen_name)

            print 'Querying for bots'
            results = list(bon.check_accounts_in(accounts_to_check))

            for result in results:
                name = result[0]
                data = result[1]
                sybil = sybils[name]
                if sybil and data and 'score' in data:
                    print 'Adding bot data to {}'.format(sybil.screen_name)
                    sybil.provide_bot_data(data)

        sybil_list = list()
        for k, v in sybils.iteritems():
            sybil_list.append(v)

        self.sybil_database.add_to_knowledge_base(sybil_list)

        return sybil_list


class SybilDatabase(object):

    def __init__(self):
        self.session = database_session()
        persisted_sybils = self.session.query(SybilObject).all()
        self.sybil_knowledge = {}
        for sybil_object in persisted_sybils:
            known_sybil = Sybil.from_object(sybil_object)
            print 'Adding {} from persisted sybils'.format(known_sybil.detail())
            self.sybil_knowledge[known_sybil.user_id] = known_sybil

    def add_to_knowledge_base(self, list_of_sybils):
        for sybil in list_of_sybils:
            if sybil.user_id in self.sybil_knowledge:
                print '{} already in knowledge base'.format(sybil.user_id)
                # account exists, lets when we analyzed it last
                cur_time = int(round(time.time() * 1000))
                if cur_time > self.sybil_knowledge[sybil.user_id].analysis_time + 86400000:
                    print 'Updating {} in knowledge base'.format(sybil.user_id)
                    self._update_row(sybil)
            else:
                print 'Adding {} to knowledge base'.format(sybil.user_id)
                self._add_row(sybil)

    def get_sybil_for_id(self, user_id):
        print 'Get sybil for id {}'.format(user_id)
        if user_id in self.sybil_knowledge:
            print 'Getting {} from knowledge base'.format(user_id)
            # account exists, lets when we analyzed it last
            cur_time = int(round(time.time() * 1000))
            analysis_time = int(self.sybil_knowledge[user_id].analysis_time)
            if cur_time > analysis_time + 86400000:
                print 'Analysis time {} longer than 24 hours of current time {}'.format(analysis_time, cur_time)
                return None
            else:
                known_sybil = self.sybil_knowledge[user_id]
                print 'Returning known sybil {} for id {}'.format(known_sybil.detail(), user_id)
                return known_sybil
        print '{} not in knowledge base'.format(user_id)
        return None

    def _add_row(self, sybil):
        print 'Adding row {}'.format(sybil.user_id)
        self.sybil_knowledge[sybil.user_id] = sybil
        self.session.add(sybil.to_db_object())
        self.session.commit()

    def _update_row(self, sybil):
        print 'Updating row {}'.format(sybil.user_id)
        self.sybil_knowledge[sybil.user_id] = sybil
        sybil_object = self.session.query(SybilObject).filter_by(user_id=sybil.user_id).first()
        sybil_object.update(sybil)
        self.session.commit()