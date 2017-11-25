import sys
#csv is the output we'll write to
import csv

#http://www.tweepy.org/
import tweepy

#for timing function
import time

#regex library
import re

#Get your Twitter API credentials and enter them in a txt file
#These are keys that twitter gives you when you register an App
#
keys = []
inFile = open("/home/colin/Desktop/keys", "r")
for line in inFile:
    line = line.strip()
    keys.append(line)

consumer_key = str(keys[0])
consumer_secret = str(keys[1])
access_key = str(keys[2])
access_secret = str(keys[3])

rate_limit = 15 #minutes

# http://tweepy.readthedocs.org/en/v3.1.0/getting_started.html#api
# this block of code authenticates us with twitter's db
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

def get_followers(username, original_user, new_user, first_loop):

    ids = []
    user_names = []
    i = 0

    #finds follower ids up to 1000
    for page in tweepy.Cursor(api.followers_ids, screen_name = username).pages():

        ids.extend(page)
        i += 1
        print("getting followers: %s" %(len(ids)))

        if len(ids) >= 1000:
                break

        #3 queries then 5 min break, 500 users per query
        if i == 3:
            print("Avoiding rate_limit. Wait 5 mins.")
            time.sleep(300)
            i = 0

    #prints total gathered followers
    print("Follower count gathered: ", len(ids))
    start = 0
    chunk = 100
    #while the ids still has more.
    #if it's first loop, find followers, else, just use ids.
    while start < len(ids):
        if first_loop:
            upper_bound = min(len(ids), start + chunk)

            #twitter only allows getting usernames for chunks of 100 ids
            user_objs = api.lookup_users(user_ids = ids[start:upper_bound])
            for user in user_objs:
                user_names.append(user.screen_name)
            print("loading usernames... ", len(user_names))

            #iterate by 100
            start += chunk
        else:
            user_names = ids
            break

    #shows writing to a new file
    print ("writing to {0}_followers_tweets.csv".format(original_user))
    with open("{0}_followers.csv".format(original_user) , 'a') as file:
        writer = csv.writer(file, delimiter= '|')

        #each row is 1 ID

        out_list = user_names
        out_list.insert(0, new_user)
        writer.writerow(out_list)

    return(user_names)


def main():

    username = str(input("Enter a twitter username (no @):"))

    #for timer
    start = time.time()

    original_user = username
    new_user = username
    first_loop = True
    user_names = get_followers(username, original_user, new_user, first_loop)

    #runs origianl user's followers through get_tweets
    print("\nNow searching followers' followers:")
    i = 0
    for name in user_names:
        i += 1
        first_loop = False
        new_user = name
        print("\nfinding", name, "'s followers...")

        if i >= 5:
            print("\nWait 15 mins\n")
            time.sleep(900)
            i = 0
        #if looking up an account and privacy prevents it from accessing
        try:
            get_followers(name, original_user, new_user, first_loop)

        #skip account and print this message
        except:
            print("THIS USERS ACCOUNT IS HIDDEN.")
            continue

    end = time.time()
    print("\n elapsed time: ", end - start)

main()
