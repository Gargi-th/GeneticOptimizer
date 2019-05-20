
try:
    from fitness import Fitness

except ModuleNotFoundError as m:
    from .fitness import Fitness

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import math
from datetime import datetime
import pandas as pd
import numpy as np
import scipy.stats as stats
# anova

class Optimizer(Fitness):
    def __init__(self, file_name):
        super().__init__(file_name)
        self.performance = self.config.performance()
        self.fitted_population = self.fit_population()
        
        self.log = str(datetime.now()) + '\n' + 'Fitness function established' + '\n'        
        print(self.log)
        
        self.population_groups = self.group_population()

        self.log = str(datetime.now()) + '\n' + 'Population grouped into clusters' + '\n'        
        print(self.log)

        self.parent_selection()

    def elbow(self):
        sum_of_squared_distances = []
 
        for cluster in range(1, int(self.population.shape[0]) + 1):
            clusters_no = KMeans(n_clusters=cluster)
            clusters_no = clusters_no.fit(self.fitted_population[['Chromosome', 'Total']])
            sum_of_squared_distances.append(clusters_no.inertia_)
        
#        print(sum_of_squared_distances)
        return self.linear_group_size(sum_of_squared_distances)
        
        # plt.plot(range(1, int(self.population.shape[0])), Sum_of_squared_distances, 'bx-')
        # plt.xlabel('cluster number')
        # plt.ylabel('Sum_of_squared_distances')
        # plt.title('Elbow method for optimal number of clusters')
        # plt.show()

    def linear_group_size(self, sum_of_squared_distances):
#        sum_of_squared_distances[0] == 22.78.. for y axis and 1 for x axis
#        sum_of_squared_distances[int(self.population.shape[0])-1] == 0.0 for y axis and int(self.population.shape[0]) for x axis
#        sum_of_squared_distances[int(self.population.shape[0])-1] - sum_of_squared_distances[0] = int(self.population.shape[0])*a - a
        
        slope = (sum_of_squared_distances[int(self.population.shape[0])-1] - sum_of_squared_distances[0]) / (int(self.population.shape[0]) - 1)
        intercept = sum_of_squared_distances[0] - slope
        
        distance = []

        for label in range(len(sum_of_squared_distances)):
            distance.append(abs((slope * label) - (sum_of_squared_distances[label]) + intercept)/(math.sqrt(slope**2 + intercept**2)))
        
        return distance.index(max(distance))
            
    def group_population(self):
        self.fitted_population['Chromosome'] = self.fitted_population['Chromosome'] * self.performance['chromosome_weight']

        population_groups = KMeans(n_clusters=self.elbow())
        population_groups.fit(self.fitted_population[['Chromosome', 'Total']])

#        self.fitted_population['Labels'] = population_groups.labels_
        self.fitted_population = pd.concat([self.fitted_population, pd.Series(population_groups.labels_, name='Labels')], axis=1)
        
        print(population_groups.cluster_centers_)
        
        plt.title('Fitted chromosomes groups')
        plt.xlabel('Number of chromosome')
        plt.ylabel('Total value')
        plt.scatter(self.fitted_population['Chromosome'], self.fitted_population['Total'], c=population_groups.labels_)
        plt.scatter(population_groups.cluster_centers_[:,0], population_groups.cluster_centers_[:,1], marker='x')
        plt.show()

        return population_groups

    def cluster_distances(self):
        centroid_dists = []
        centroids = list(self.population_groups.cluster_centers_)
        centroids_converted = sorted(list(map(lambda x: x[1], centroids)))
        centroids.sort(key=lambda x: x[1])
#        print(centroids_converted)
#        centroids = sorted(list(self.population_groups.cluster_centers_), key = lambda x: x[1])
        print(centroids)
#        print(len(centroids))
        for destination_cluster, value in enumerate(centroids):
            dists = []
            for source_cluster, value in enumerate(centroids):
                if (centroids[source_cluster][0] == centroids[destination_cluster][0]) and (centroids[source_cluster][1] == centroids[destination_cluster][1]):
                    pass
                else:
                    dist = math.sqrt((centroids[source_cluster][0] - centroids[destination_cluster][0])**2 + (centroids[source_cluster][1] - centroids[destination_cluster][1])**2)
                    dists.append(dist)
            
            centroid_dists.append(dists)
#            dist = math.sqrt((cluster[1][0] - cluster[0][0])**2 + (cluster[1][1] - cluster[0][1])**2)
#            print(dist)

        return centroid_dists

    def roulette_wheel_selection(self):
        centroid_dists = self.cluster_distances()
#        print(centroid_dists) 
        max_prob = [sum(dist) for dist in centroid_dists]
        cluster = 0
        dists = {}
        for centroid in centroid_dists:
            dist = []
            for target in centroid:
                dist.append(target / max_prob[cluster])

            dist.insert(cluster, 0)
            dists[cluster] = dist
            cluster += 1
#        print(dists) 
        return dists

    def parent_selection(self):
        # try except somewhere here where 'Selected' will not match
        probability = self.roulette_wheel_selection()
        print(probability)
#        print(self.fitted_population)
        self.fitted_population['Selected'] = pd.Series(data=[False for row in range(self.fitted_population.shape[0])])
        print(self.fitted_population)
        first_parent = self.fitted_population[self.fitted_population['Selected'] == False].sample(n = 1)
        print(first_parent)

        label = np.random.choice([cluster for cluster in probability.keys()], p=probability[int(first_parent['Labels'])])
        second_parent = self.fitted_population[(self.fitted_population['Selected'] == False) & (self.fitted_population['Labels'] == label)].sample(n = 1)
        print(second_parent)

        F_test = stats.f_oneway(first_parent.iloc[:, 0: self.fitted_population.columns.get_loc('Total')].values[0], second_parent.iloc[:, 0: self.fitted_population.columns.get_loc('Total')].values[0])
        print(F_test)
        print(F_test[0])
        print(self.population)
#        if (float(first_parent['Total']) + float(second_parent['Total']))... and F_test > new F_test
        


        
