from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy import Table, Column, Integer, Text, DateTime, ForeignKey
from datetime import datetime


class SybilObject(Base):

    __tablename__ = 'sybils'

    id                          =   Column(Integer, primary_key=True)
    user_id                     =   Column(Integer, unique=True, nullable=False)
    screen_name                 =   Column(Text(convert_unicode=True), nullable=False)
    analysis_time               =   Column(Integer, default=0)
    account_age                 =   Column(Text(convert_unicode=True), nullable=False)
    location                    =   Column(Text(convert_unicode=True), nullable=False)
    bot_score                   =   Column(Integer, default=0)
    content_classification      =   Column(Integer, default=0)
    friend_classification       =   Column(Integer, default=0)
    network_classification      =   Column(Integer, default=0)
    sentiment_classification    =   Column(Integer, default=0)
    temporal_classification     =   Column(Integer, default=0)
    user_classification         =   Column(Integer, default=0)
    languageagnostic_classification = Column(Integer, default=0)
    classification              =   Column(Text(convert_unicode=True), nullable=False)
    interacted_with             =   Column(Text(convert_unicode=True), nullable=False)

    def __repr__(self):
        return "<SybilObject (user_id='%s', screen_name='%d', analysis_time=%s)>" % (self.user_id, self.screen_name,
                                                                               self.analysis_time)

    def update(self, sybil):
        self.screen_name = sybil.screen_name
        self.analysis_time = sybil.analysis_time
        self.account_age = sybil.account_age
        self.location = sybil.location
        self.bot_score = sybil.bot_score
        self.content_classification = sybil.content_classification
        self.friend_classification = sybil.friend_classification
        self.network_classification = sybil.network_classification
        self.sentiment_classification = sybil.sentiment_classification
        self.temporal_classification = sybil.temporal_classification
        self.user_classification = sybil.user_classification
        self.languageagnostic_classification = sybil.languageagnostic_classification
        self.classification = sybil.classification
        self.interacted_with = ",".join(map(str, sybil.interacted_with))