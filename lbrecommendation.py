# -*- coding: utf-8 -*-
"""LBRecommendation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/sachin7695/LB_RECOMENDATIONS/blob/main/LBRecommendation.ipynb

# Location-Based Recommendations

Recommendation systems are widely utilized in different applications for predicting the preference or rating of a user in a product or service. Most likely you have come across or interacted with some type of recommender systems in the past few minutes or hours in your online presence. Even this article might have been suggested to you using Recommender systems. These Recommender systems can be of different types and the most prominent ones include Content-based filtering and Collaborative filtering. In this article, we will study location-based recommendations, where we specifically focus on geographic locations to render more relevant recommendations utilizing the location of the users. 


To illustrate the crucial aspects of location-based recommenders we will perform a simple Location-based recommendation using the K-Means algorithm with Yelp Dataset from Kaggle. The data comes in JSON files and can be easily read with pandas. The following table shows the first 5 rows of the datase
"""

!apt install gdal-bin python-gdal python3-gdal 
!apt install python3-rtree 
!pip install git+git://github.com/geopandas/geopandas.git
!pip install descartes 
!pip install folium 
!pip install plotly_express

import pandas as pd 
import numpy as np
!pip install geopandas
import geopandas as gpd

import matplotlib.pyplot as plt
import seaborn as sns

import folium

import plotly 
import plotly.offline as py
import plotly.graph_objs as go
import plotly_express as px

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

!wget https://www.dropbox.com/s/3x1w789mmuae3ao/yelp_academic_dataset_business.zip
!unzip yelp_academic_dataset_business.zip

import pandas as pd
import random
import string
df = pd.read_json('yelp_academic_dataset_business.json', lines=True)
df['farm_name'] = [''.join(random.choices(string.ascii_letters, k=5)) for _ in range(len(df))]
df.head()

# df.shape
df.drop('name', axis=1, inplace=True)

"""## Exploratory Data Analaysis (EDA)"""

df['Farming'] = df['categories'].str.contains('Restaurants')
df.head(2)

df_farming = df.loc[df.Farming == True]
df_farming.head()

df_farming.shape

fig, ax = plt.subplots(figsize=(12,10))
sns.countplot(df_farming['stars'], ax=ax)
plt.title('Review Stars Countplot')
plt.savefig('stars.png')
plt.show()

top_farm = df_farming.sort_values(by=['review_count', 'stars'], ascending=False)[:20]
top_farm.head()

fig, ax = plt.subplots(figsize=(12,10))
sns.barplot(x = 'stars', y = 'farm_name', data=top_farm, ax= ax);
plt.savefig('top20_farm.png')
plt.show()

px.set_mapbox_access_token("pk.eyJ1Ijoic2hha2Fzb20iLCJhIjoiY2plMWg1NGFpMXZ5NjJxbjhlM2ttN3AwbiJ9.RtGYHmreKiyBfHuElgYq_w")
#configure_plotly_browser_state()
px.scatter_mapbox(df_farming, lat="latitude", lon="longitude", color="stars", size='review_count' ,
                   size_max=30, zoom=3, width=1200, height=800)

lasVegas = df_farming[df_farming.state == 'NV']
# px.scatter_mapbox(lasVegas, lat="latitude", lon="longitude", color="stars", size='review_count' ,
#                    size_max=15, zoom=10, width=1200, height=800)
lasVegas.shape
lasVegas.head()

"""## K-Means Clustering

### Determing the number of clusters (K)
"""

# Elbow method to determine the number of K in Kmeans Clustering
coords = lasVegas[['longitude','latitude']]

distortions = []
K = range(1,25)
for k in K:
    kmeansModel = KMeans(n_clusters=k)
    kmeansModel = kmeansModel.fit(coords)
    distortions.append(kmeansModel.inertia_)

fig, ax = plt.subplots(figsize=(12, 8))
plt.plot(K, distortions, marker='o')
plt.xlabel('k')
plt.ylabel('Distortions')
plt.title('Elbow Method For Optimal k')
plt.savefig('elbow.png')
plt.show()

"""Silhoute method

"""

from sklearn.metrics import silhouette_score

sil = []
kmax = 50

# dissimilarity would not be defined for a single cluster, thus, minimum number of clusters should be 2
for k in range(2, kmax+1):
  kmeans = KMeans(n_clusters = k).fit(coords)
  labels = kmeans.labels_
  sil.append(silhouette_score(coords, labels, metric = 'euclidean'))

sil

"""### K-Means Clustering"""

kmeans = KMeans(n_clusters=5, init='k-means++')
kmeans.fit(coords)
y = kmeans.labels_
print("k = 5", " silhouette_score ", silhouette_score(coords, y, metric='euclidean'))

lasVegas['cluster'] = kmeans.predict(lasVegas[['longitude','latitude']])
lasVegas.head()

px.scatter_mapbox(lasVegas, lat="latitude", lon="longitude", color="cluster", size='review_count', 
                  hover_data= ['farm_name', 'latitude', 'longitude'], zoom=10, width=1200, height=800)

"""## Location-Based Recommendation"""

top_farm_lasVegas = lasVegas.sort_values(by=['review_count', 'stars'], ascending=False)
top_farm_lasVegas.head()
# top_farm_lasVegas.drop("name", axis = 1, inplace=True)
# top_farm_lasVegas.head()

def recommend_restaurants(df, longitude, latitude):
    # Predict the cluster for longitude and latitude provided
    cluster = kmeans.predict(np.array([longitude,latitude]).reshape(1,-1))[0]
    print(cluster)
   
    # Get the best restaurant in this cluster
    return  df[df['cluster']==cluster].iloc[0:5][['farm_name', 'latitude','longitude'	]]

recommend_restaurants(top_farm_lasVegas,-115.1891691,  36.1017316)

recommend_restaurants(top_farm_lasVegas,-115.2798544, 36.0842838)

recommend_restaurants(top_farm_lasVegas, 	-115.082821, 36.155011 )

test_coordinates = {
    'user': [1, 2, 3], 
    'latitude' : [36.1017316, 36.0842838, 36.155011],
    'longitude' : [-115.1891691, -115.2798544, -115.082821],
}

test_df = pd.DataFrame(test_coordinates)
test_df

user1 = test_df[test_df['user'] == 1]
user1

fig = px.scatter_mapbox(recommend_restaurants(top_farm_lasVegas, user1.longitude, user1.latitude), lat="latitude", lon="longitude",  
                   zoom=10, width=1200, height=800, hover_data= ['farm_name', 'latitude', 'longitude'])
fig.add_scattermapbox(lat=user1["latitude"], lon= user1["longitude"]).update_traces(dict(mode='markers', marker = dict(size = 15)))

user2 = test_df[test_df['user'] == 2].reset_index()
fig = px.scatter_mapbox(recommend_restaurants(top_farm_lasVegas, user2.longitude, user2.latitude), lat="latitude", lon="longitude",  
                   zoom=10, width=1200, height=800, hover_data= ['farm_name', 'latitude', 'longitude'])
fig.add_scattermapbox(lat=user2["latitude"], lon= user2["longitude"]).update_traces(dict(mode='markers', marker = dict(size = 15)))

user3 = test_df[test_df['user'] == 2].reset_index()
fig = px.scatter_mapbox(recommend_restaurants(top_farm_lasVegas, user3.longitude, user3.latitude), lat="latitude", lon="longitude",  
                   zoom=10, width=1200, height=800, hover_data= ['farm_name', 'latitude', 'longitude'])
fig.add_scattermapbox(lat=user3["latitude"], lon= user3["longitude"]).update_traces(dict(mode='markers', marker = dict(size = 15)))

"""## End"""