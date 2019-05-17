
try:
    from fitness import Fitness

except ModuleNotFoundError as m:
    from .fitness import Fitness

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import math
from datetime import datetime
#naive bayes

class Optimizer(Fitness):
    def __init__(self, file_name):
        super().__init__(file_name)
        self.performance = self.config.performance()
        self.fitted_population = self.fit_population()
        
        self.log = str(datetime.now()) + '\n' + 'Fitness function established' + '\n'        
        print(self.log)
        
        self.group_population()

        self.log = str(datetime.now()) + '\n' + 'Population grouped into clusters' + '\n'        
        print(self.log)

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

#        print(population_groups.labels_)

        # plt.title('Fitted chromosomes groups')
        # plt.xlabel('Number of chromosome')
        # plt.ylabel('Total value')
        # plt.scatter(self.fitted_population['Chromosome'], self.fitted_population['Total'], c=population_groups.labels_)
        # plt.show()

        
