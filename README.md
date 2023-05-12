# twitter-graph

## graph.py
Code for graph manipulation, such as creating graphs and detecting communities.

## main.py
Code for setting up experiments and parameters.

## sir.py
Code for simulating information diffusion based on the SIR model.

## visualization.py
Code for visualizing experimental results.

## Experiments folder
A Jupyter notebook for preprocessing experiments. With code explanation and experimental results.


# 1. Introduction

Twitter is a popular social media platform that can provide valuable insights for marketing. By analyzing the tweets and interactions of users, marketers can identify and target potential customers based on their interests and behaviors. One of the key tasks in Twitter analysis is community detection, which aims to find groups of users who share similar characteristics or preferences. However, Twitter has a very large and complex network structure, with millions of nodes (users) and edges (relationships). Running a community detection algorithm on such a huge graph can be computationally expensive and may not produce meaningful results. Therefore, I am interested in exploring methods to reduce the size of a large graph while preserving its essential features and properties. This way, I can apply community detection more efficiently and effectively on Twitter data.

# 2. Dataset

An analysis was conducted using a dataset of Twitter data published on [Kaggle](https://www.kaggle.com/datasets/hwassner/TwitterFriends). The data is from 7 years ago, and although it is slightly outdated, it was determined that there is no significant impact on the analysis results because there have been no major changes to the essential functions of Twitter, such as tweeting, liking, and following features. If you want to take into account recent trends in your analysis, you would need to update the data to something more current. The following are the description of the dataset used in this study.

The dataset is a list of Twitter user's information. In the CSV format one Twitter user is stored in one object of this more than 40000 objects list. 

Each object holds:

- **avatar**: URL to the profile picture
- **followerCount**: the number of followers of this user
- **friendsCount**: the number of people following this user.
- **friendName**: stores the @name (without the '@') of the user (beware this name can be changed by the user)
- **id**: user ID, this number can not change (you can retrieve screen name with this service: [https://tweeterid.com/](https://tweeterid.com/))
- **friends**: the list of IDs the user follows (data stored is IDs of users followed by this user)
- **lang**: the language declared by the user (in this dataset there is only "en" (English))
- **lastSeen**: the time stamp of the date when this user have post his last tweet.
- **tags**: the hashtags (with or without #) used by the user. It's the "trending topic" the user tweeted about.
- **tweetID**: Id of the last tweet posted by this user.

These users have at least 100 followers and following at least 100 other accounts (in order to filter out spam and non-informative/empty accounts).

### Full report: [https://docs.google.com/document/d/1w6_RfkuJBWhA4urZ08jgmGPF26piIG4zCHR8oV_sfZ8/edit?usp=sharing](https://docs.google.com/document/d/1w6_RfkuJBWhA4urZ08jgmGPF26piIG4zCHR8oV_sfZ8/edit?usp=sharing)
### Full slides: [https://docs.google.com/presentation/d/10t8CASVLFqdeCP91gzllROu1b1QqVjI9wIQqaPyQDII/edit?usp=sharing](https://docs.google.com/presentation/d/10t8CASVLFqdeCP91gzllROu1b1QqVjI9wIQqaPyQDII/edit?usp=sharing)
### Dataset: [https://www.kaggle.com/datasets/hwassner/TwitterFriends](https://www.kaggle.com/datasets/hwassner/TwitterFriends)
