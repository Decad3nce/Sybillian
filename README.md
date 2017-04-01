# Sybillian

## What is it?

Sybillian is a twitter bot that can receive mentions or be included
in conversations to analyze the account(s) to see what their bot score
is based off of a [BotOrNot](https://truthy.indiana.edu/botornot/) score.

BotOrNot checks the activity of a Twitter account and gives it a score based on how likely the account is to be a bot.
Higher scores are more bot-like.

BotOrNot accomplishes this goal by the use of [Random Forest](https://en.wikipedia.org/wiki/Random_forest) to do ensemble learning
via a multitude of [Decision Trees](https://en.wikipedia.org/wiki/Decision_tree_learning). The model is then trained with 'known bots' and 'known human' accounts to build a heuristic decision
tree model that nullifies bias. Sybillian's role is to present BotOrNot accounts to test against this ensemble and provides a
score for multiple factors, including:
* content classification
* friend classification
* network classification
* sentiment classification
* temporal classification
* user classification
* language agnostic classification

For further details, you can reference the [Indiana University Publications](https://truthy.indiana.edu/botornot/publications/).

## What is it's purpose?

I built Sybillian because I wanted to offhand check the "truthiness" of accounts
that were pushing a specific topic or idea. Whether it be for marketing or otherwise.

## How can it be used?
You can either directly mentions [@SybilDetector](https://www.twiter.com/SybilDetector) with a username.
ex:
 ```
 @SybilDetector @SwiftOnSecurity
 ```
 and receive a response back:
 ```
 @Decad3nce SwiftOnSecurity has a bot score of 0.45. Classification of 'might be a bot'. See
 https://t.co/upkHRBwQ4S
 ```

Or, you can add it as a reply to a twitter "thread" to see the percentage of participants (including retweeters)
ex resp:
```
@Decad3nce the conversation of 76 contributors contains 4 probable bots, percentage of bots in conversation 5.26315789474.
```

## How can I deploy my own?
1. Create a Twitter [Application](https://apps.twitter.com/).
2. Populate `credentils.py` with your tokens and shared secrets from the application creation.
3. Run locally by creating a virtual environment and `pip install` the active directory.
4. Run remotely by hosting the application on whatever server of your choosing.

## Isn't this just a shell for BotOrNot?

Yes, yes it is. But it also allows the process of 'harvesting' bot data to be further decentralized.

## Future plans?

1. Move away from local sql db to a generic and pluggable backend for caching that can be hosted remotely. Then allow surrogate bots
to provide data to that central cache.