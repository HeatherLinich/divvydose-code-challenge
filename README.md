# divvydose-code-challenge   
Code challenge for divvyDOSE 2019   
This api provides three endpoints for the user to explore repository information on GitHub, BitBucket or aggregated over both systems.  Basic unit tests have been included to verify that calls to the endpoints will succeed if correctly formatted. (Tests are created and run with pytest)

This is currently version 1 of this API.

The following URLs are available for use and all take an ‘org’ parameter

```http://127.0.0.1:5000/v1/comboorgs?org=<name>```   
provides the following data points aggregated over both platforms
 - name
 - number of public repos
 - number of forked repos
 - total watchers/followers
 - list of all languages used across repos
 - count of unique languages used across repos
 - list of descriptions/topics across all repos
 - count of unique descriptions across all repos

example call 

```curl http://127.0.0.1:5000/v1/comboorgs?org=mailchimp```

Currently, this endpoint takes only one parameter, ‘org’, assuming that the organization name would be the same on both platforms.  This could be expanded to receive additional parameters in the event of different names for the same organization or a desire to aggregate over multiple organizations

```http://127.0.0.1:5000/v1/github?org=<name>```
provides all basic data points on the organization from GitHub

example call

```curl http://127.0.0.1:5000/v1/github?org=mailchimp```

```http://127.0.0.1:5000/v1/bitbucket?org=<name>```
provides all basic data points on the organization from BitBucket

example call

```curl http://127.0.0.1:5000/v1/bitbucket?org=mailchimp```


Ideas for future enhancements:
 - Make calls to GitHub/BitBucket APIs authenticated as there is a lower daily threshold on non-authenticated calls to their api
 - Look into ways to refactor and speed up processing for aggregating endpoint
 - If functionality is fleshed out, add in database connectivity, token authentication and additional testing
