import time
from database import SybilObject


class User(object):

    def __init__(self):
        self.id = None
        self.screen_name = None
        self.created_at = None
        self.location = None


class Sybil(object):
    NOT_A_BOT = "not_a_bot"
    MIGHT_BE_A_BOT = "maybe_bot"
    PROBABLY_A_BOT = "probably_bot"
    BOT = "bot"

    def __init__(self, user):
        self.user_id = user.id
        self.screen_name = user.screen_name
        self.analysis_time = int(round(time.time() * 1000))
        self.account_age = user.created_at
        self.location = user.location
        self.bot_score = None
        self.content_classification = None
        self.friend_classification = None
        self.network_classification = None
        self.sentiment_classification = None
        self.temporal_classification = None
        self.user_classification = None
        self.languageagnostic_classification = None
        self.classification = None
        self.interacted_with = list()

    @classmethod
    def from_object(cls, sybil_object):
        user = User()
        user.id = sybil_object.user_id
        user.screen_name = sybil_object.screen_name
        user.location = sybil_object.location
        sybil = cls(user)
        sybil.analysis_time = sybil_object.analysis_time
        sybil.account_age = sybil_object.account_age
        sybil.bot_score = sybil_object.bot_score
        sybil.content_classification = sybil_object.content_classification
        sybil.friend_classification = sybil_object.friend_classification
        sybil.network_classification = sybil_object.network_classification
        sybil.sentiment_classification = sybil_object.sentiment_classification
        sybil.temporal_classification = sybil_object.temporal_classification
        sybil.user_classification = sybil_object.user_classification
        sybil.languageagnostic_classification = sybil_object.languageagnostic_classification
        sybil.classification = sybil_object.classification
        if sybil_object.interacted_with:
            sybil.interacted_with = sybil_object.interacted_With.split(",")
        return sybil

    def provide_bot_data(self, data):
        self.bot_score = data['score']
        print data
        self.content_classification = data['categories']['content_classification']
        self.friend_classification = data['categories']['friend_classification']
        self.network_classification = data['categories']['network_classification']
        self.sentiment_classification = data['categories']['sentiment_classification']
        self.temporal_classification = data['categories']['temporal_classification']
        self.user_classification = data['categories']['user_classification']
        self.languageagnostic_classification = data['categories']['languageagnostic_classification']
        self.classification = self._classify(self.bot_score)

    def _classify(self, score):
        if score < 0.45:
            return self.NOT_A_BOT
        if 0.45 <= score < 0.55:
            return self.MIGHT_BE_A_BOT
        if 0.55 <= score < 0.75:
            return self.PROBABLY_A_BOT
        if score >= 0.75:
            return self.BOT

    def get_classification_as_string(self):
        if self.classification == self.NOT_A_BOT:
            return "not a bot"
        elif self.classification == self.MIGHT_BE_A_BOT:
            return "might be a bot"
        elif self.classification == self.PROBABLY_A_BOT:
            return "probably a bot"
        else:
            return "definite bot"

    def to_db_object(self):
        return SybilObject(user_id=self.user_id,
                           screen_name=self.screen_name,
                           analysis_time=self.analysis_time,
                           account_age=self.account_age,
                           location=self.location,
                           bot_score=self.bot_score,
                           content_classification=self.content_classification,
                           friend_classification=self.friend_classification,
                           network_classification=self.network_classification,
                           sentiment_classification=self.sentiment_classification,
                           temporal_classification=self.temporal_classification,
                           user_classification=self.user_classification,
                           languageagnostic_classification=self.languageagnostic_classification,
                           classification=self.classification,
                           interacted_with=",".join(map(str, self.interacted_with)))

    def detail(self):
        return 'Sybil \'{}\':\n' \
               '  user id: {}\n' \
               '  account age: {}\n' \
               '  location: {}\n' \
               '  bot_score: {}\n' \
               '    content_classification: {}\n' \
               '    friend_classification: {}\n' \
               '    network_classification: {}\n' \
               '    sentiment_classification: {}\n' \
               '    temporal_classification: {}\n' \
               '    user_classification: {}\n' \
               '  classification: {}\n' \
               '  interacted_with: {}\n'.format(self.screen_name, self.user_id, self.account_age,
                                             self.location, self.bot_score, self.content_classification,
                                             self.friend_classification, self.network_classification,
                                             self.sentiment_classification, self.temporal_classification,
                                             self.user_classification, self.classification,
                                             self.interacted_with)
