import sys
#csv is the output we'll write to
import csv

#http://www.tweepy.org/
import tweepy

#for timing function
from time import gmtime, strftime
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

def get_followers(username):

	ids = []
	i = 0

	#finds follower ids
	for page in tweepy.Cursor(api.followers_ids, screen_name = username).pages():

		ids.extend(page)
		i += 1
		print("getting followers: %s" %(len(ids)))

		#only collect up to 1000
		if len(ids) >= 1000:
				break

		#3 queries then 5 min break, 500 users per query
		if i == 3:
			print("Avoiding rate_limit. Wait 5 mins.")
			time.sleep(300)
			i = 0

	#prints total gathered followers
	print("Follower count gathered: ", len(ids))
	return(ids)

def check_connectivity(ids, original_user):

	downtime = 0
	i = 0
	out_list = []
	centrality_list = []

	#shows writing to a new file
	print ("writing to {0}_followers_tweets.csv".format(original_user))
	with open("{0}_followers.csv".format(original_user) , 'w') as file:
		writer = csv.writer(file, delimiter= '|')

		#start with original user's followers' ids
		out_list = ids
		out_list.insert(0, original_user)
		print(out_list)
		#append and then prepare for new rows for follower's mutual followers
		writer.writerow(out_list)
		out_list = []

		#now that we wrote the original user, we can remove
		#from the check since we already know the ids are friends of original_user
		ids.remove(original_user)

		rate_count = 0

		for root in ids:
			out_list = []
			out_list.insert(0, root)
			print("follower ", i+1, " of ", len(ids))
			num_mutual = 0
			
			for node in ids:

				rate_count += 1
				if root == node:
					break

				print(root, node)

				while True:
					try:
						#check if user is friends
						out = (api.show_friendship(source_id = root, target_id = node))
						print(out)
						#rate_count = num of queries
						#this if statement attempts to prevent hitting rate limit
						if rate_count == 150:
							print("Avoiding rate Limit at {0}: Waiting 15 mins".format(strftime("%H:%M:%S"), gmtime()))
							time.sleep(900)
							downtime += 900
							rate_count = 0

					except tweepy.TweepError:
						print("YOU HIT THE RATE LIMIT AT {0}: Waiting 15 mins".format(strftime("%H:%M:%S"), gmtime()))
						time.sleep(900)
						downtime += 900
						continue

					break


				#if user is following = true
				if(out[0].following):

					print("BING")
					num_mutual += 1
					out_list.append(node)

			print()
			print("writing to list")
			writer.writerow(out_list)
			print()

			#this attempts to create a degree of connectivity by dividing total number of mutuals
			#by the total number of root node followers
			u_centrality = num_mutual / len(ids)

			centrality_list.append(u_centrality)     
			i += 1

	file.close()
	return(centrality_list, downtime)

def main():

	totaldowntime = 0
	downtime = 0
	start = time.time()
	print("start time: {0}".format(strftime("%H:%M:%S"), gmtime()))

	nameFile = open("/home/colin/tweepy_followers/usernames", "r")

	for username in nameFile:
		centrality_list = []
		data = api.rate_limit_status()
		x = data['resources']['followers']['/followers/ids']
		rate_limit_left = x['remaining']

		username = username.strip()
		#username = str(input("Enter a twitter username (no @):"))
		original_user = username
		
		if(rate_limit_left == 1):
			print("Follower ID check rate-limited at {0}: Waiting 15 mins".format(strftime("%H:%M:%S"), gmtime()))
			time.sleep(900)
			downtime += 900

		print(username)
		try:
			ids = get_followers(username)

			#if the user has less than 250 followers, continue
			if len(ids) <= 250:
				centrality_list, downtime = check_connectivity(ids, original_user)


		#if account privacy set to private
		#skip account and print this message
		except:
			print("THIS USERS ACCOUNT IS HIDDEN.")


		totaldowntime += downtime
		print(centrality_list)
		print ("writing to analysis.csv")
		with open("analysis.csv", 'a') as endfile:
			out_writer = csv.writer(endfile, delimiter= '|')

			centrality_list.insert(0, original_user)
			out_writer.writerow(centrality_list)

	print("TOTAL TIME LOST TO API RATE LIMIT: ", totaldowntime/60, "MINUTES")

	end = time.time()
	print("\n elapsed time: ", end - start)

main()
