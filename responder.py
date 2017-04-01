#!/usr/bin/env python

import tweepy
import Queue
import multiprocessing
import threading
from threading import Thread
import time
import botornot
import datetime
from credentials import *
from sybil import *
from populator import *

import sys;
reload(sys);
sys.setdefaultencoding("utf8")


## Auth
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)
lasttweet = None
sybil_populator = SybilPopulator(api)

worker_queue = Queue.Queue()


def runtime():
    print "Setting up Sybillian streamer"
    myStreamListener = SybillianStreamListener()
    myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
    print "Filtering on @{}".format(TWITTER_USERNAME)
    myStream.filter(track=['@{}'.format(TWITTER_USERNAME)], async=True)
    cpus = multiprocessing.cpu_count()
    print "Spawning {} worker threads".format(cpus)
    for i in range(cpus):
        t = threading.Thread(target=worker)
        t.start()


def worker():
    while True:
        request = worker_queue.get()
        print "Getting {} work".format(request.status.text)
        analyze(request)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def percentage(part, whole):
    return 100 * float(part)/float(whole)


class StatusAnalysisRequest(object):
    Mention, Direct_Message = range(2)

    def __init__(self, status):
        self.status = status
        self.context = self.Mention


def analyze(request):
    mostrecenttweet = request.status
    print 'New tweet at {}'.format(datetime.datetime.now())
    print 'Is a reply to status: {}'.format(mostrecenttweet.in_reply_to_status_id)
    print 'Screen Name: {}'.format(mostrecenttweet.user.screen_name)
    print 'Created At: {}'.format(mostrecenttweet.user.created_at)
    print 'Tweet id: {}'.format(mostrecenttweet.id)
    print 'Tweet Text: {}'.format(mostrecenttweet.text)
    print '\n\nTweet Content\n\n'

    user_id_mentions = list()
    retweeter_ids = list()
    tweets = list()
    retweets = list()
    contributors = 0

    if not mostrecenttweet.in_reply_to_status_id and request != StatusAnalysisRequest.Direct_Message:
        print 'Not in reply to a status, they just want to know who the bots are'
        for user_mention in mostrecenttweet.entities['user_mentions']:
            screen_name = user_mention['screen_name']
            if screen_name != TWITTER_USERNAME:
                user_id_mentions.append(user_mention['id'])
    else:
        print 'In reply to a status, lets figure out if bots are dominating this conversation'
        cur_tweet = mostrecenttweet
        while True:
            print 'Adding tweet {}'.format(cur_tweet.text)
            tweets.append(cur_tweet)
            print 'User: {}'.format(cur_tweet.user.screen_name)
            print 'User id: {}'.format(cur_tweet.user.id)
            print 'Text: {}'.format(cur_tweet.text)
            user_id_mentions.append(cur_tweet.user.id)
            try:
                prev_tweet = api.get_status(cur_tweet.in_reply_to_status_id_str)
            except tweepy.TweepError as e:
                print e
                break
            results = api.retweets(prev_tweet.id)
            for retweet in results:
                print 'Adding retweeter id {}'.format(retweet.user.id)
                retweeter_ids.append(retweet.user.id)
                retweets.append(retweet)
            for user_mention in prev_tweet.entities['user_mentions']:
                screen_name = user_mention['screen_name']
                if screen_name != TWITTER_USERNAME:
                    user_id_mentions.append(user_mention['id'])
            cur_tweet = prev_tweet
            if not cur_tweet.in_reply_to_status_id_str:
                break

    bots = list()
    not_bots = list()
    sybils = list()

    # Process in 25 user id chunks
    list_of_ids = user_id_mentions + list(set(retweeter_ids) - set(user_id_mentions))
    ids = chunks(list_of_ids, 25)
    for chunk in ids:
        print 'Processing chunk {} as type {}'.format(chunk, type(chunk))

        # Hacky way to handle single union items
        if isinstance(chunk, int):
            temp = chunk
            chunk = list()
            chunk.append(temp)

        sybils.extend(sybil_populator.process_many(chunk))

    if not mostrecenttweet.in_reply_to_status_id:
        for sybil in sybils:
            print 'Creating status update for bot check'
            status_update = '@{} {} has a bot score of {}. Classification of \'{}\'. ' \
                            'See https://truthy.indiana.edu/botornot/?sn={}'.format(
                mostrecenttweet.user.screen_name,
                sybil.screen_name, sybil.bot_score,
                sybil.get_classification_as_string(), sybil.screen_name)
            print status_update
            api.update_status(status=status_update)
    else:
        for sybil in sybils:
            print 'Sub set classification for this conversation'
            contributors += 1
            if sybil.classification != Sybil.NOT_A_BOT and sybil.classification != Sybil.MIGHT_BE_A_BOT:
                bots.append(sybil)
            else:
                not_bots.append(sybil)

        print 'Creating status update for conversation analysis'
        num_of_bots = len(bots)
        print 'Count of bots {}'.format(num_of_bots)
        print 'Count of contributors {}'.format(contributors)
        percentage_of_bots = percentage(num_of_bots, contributors)
        print 'Percentage of bots {}'.format(percentage_of_bots)
        if percentage_of_bots > 0:
            status_update = '@{} the conversation of {} contributors contains {} probable bots, ' \
                            'percentage of bots in conversation {}.' \
                .format(mostrecenttweet.user.screen_name, contributors, num_of_bots, percentage_of_bots)
        else:
            status_update = '@{} the conversation of {} contributor(s) contains no probable bots'.format(
                mostrecenttweet.user.screen_name, contributors)
        print status_update
        api.update_status(status=status_update)

        print 'Providing full bot details'
        for bot in bots:
            print bot.detail()

        print 'Providing non bot details'
        for not_bot in not_bots:
            print not_bot.detail()

        print 'Providing tweet details'
        for tweet in tweets:
            print 'Tweet {}: '.format(tweet.id)
            print ' Text: {}'.format(tweet.text)
            print ' Favorites: {}'.format(tweet.favorite_count)
            print ' Retweets: {}'.format(tweet.retweet_count)

        print 'Providing retweet details'
        for tweet in retweets:
            print 'Retweet {}: '.format(tweet.id)
            print ' Text: {}'.format(tweet.text)
            print ' Favorites: {}'.format(tweet.favorite_count)
            print ' Retweets: {}'.format(tweet.retweet_count)


class SybillianStreamListener(tweepy.StreamListener):

    def on_direct_message(self, status):
        print "Found direct message {}".format(status.text)
        request = StatusAnalysisRequest(status)
        request.context = StatusAnalysisRequest.Direct_Message
        worker_queue.put(request)

    def on_status(self, status):
        print "Found status {}".format(status.text)
        request = StatusAnalysisRequest(status)
        request.context = StatusAnalysisRequest.Mention
        worker_queue.put(request)

    def on_error(self, status_code):
        print "Received error status code: {}".format(status_code)
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

if __name__ == '__main__':
    runtime()
