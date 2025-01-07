#%%
# ==================================================
# K-Means VRPTW route construction heuristic
# Author: Giovanni Cesar Meira Barboza
# Date: 2024-01-06
# Description: 3D K-means to solve the VRPTW. Admits Solomons R, C and RC instances
# ==================================================

import random

from parsing import parse_file
from vrptw_functions import calculate_distances
from vrptw_functions import routes_distance
from vrptw_functions import routes_time
from solomon_insertion import insertion_heuristic_sr

def euc_distance(coord1, coord2):
    # Calculate euclidean time weighted distance between customers 1 and 2
    x1, y1 = coord1
    x2, y2 = coord2

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1/2)
    
def kmeanspp_initialization(k, points, customers):
    # Input: k, list of points to be clustered, customers list and time distance weight
    # Output: list of centroid customers to start a k-means procedure

    centroids = []

    # Choose first centroid uniformely at random
    j = random.randint(1, 100)
    centroids.append(j)

    # Compute distance between customers and nearest centroid
    while len(centroids) < k:
        centroid_candidates = []
        for i in points:
            if i in centroids:
                continue
            
            coord_i = [customers[i].x_coord, customers[i].y_coord]

            distances = []
            for j in centroids:
                coord_j = [customers[j].x_coord, customers[j].y_coord]
                distances.append(euc_distance(coord_i, coord_j))

            min_distance = min(distances)
            centroid_candidates.append([i, min_distance])
        
        # Choose next point as new centroid using a weighted probability proportinal to the squared distance
        total_distance = sum(candidate[1] ** 2 for candidate in centroid_candidates)
        probabilities = [(candidate[1] ** 2) / total_distance for candidate in centroid_candidates]
        new_centroid = random.choices(
            [candidate[0] for candidate in centroid_candidates],
            weights=probabilities,
            k=1
        )[0]
        centroids.append(new_centroid)

    return centroids

class Cluster:
    def __init__(self, centroid):
        self.centroid = centroid    # Position of the centroid [x, y, ready_time]
        self.customers = []         # List of customers (indices) in the cluster

    def add_customer(self, customer_idx):
        self.customers.append(customer_idx)

def kmeans_vrptw(d, t, problem, customers, max_iter, i1_params, init_criterium):
    # Input: distances and time matrices, problem data and list of customers (nodes) and maximum n. of iterations
	# Output: feasible routes to the VRPTW

    unrouted_customers = [i for i in range(1, len(customers))]
    routes = []

    while len(unrouted_customers) > 0:
        # Run k-means
        k = problem.vehicle_number * len(unrouted_customers)//(len(customers) * 5)
        iter_count = 0
        while iter_count < max_iter:
            # Start centroids
            centroid_positions = []
            if iter_count == 0:
                centroid_customers = kmeanspp_initialization(k, unrouted_customers, customers)
                for i in centroid_customers:
                    centroid_positions.append([customers[i].x_coord, customers[i].y_coord])
                
                clusters = [Cluster(centroid) for centroid in centroid_positions]

            for cluster in clusters:
                cluster.customers = []  # Clear the list of customers

            # Assign customers to nearest centroid
            for i in unrouted_customers:
                coord_i = [customers[i].x_coord, customers[i].y_coord]
                cluster_distances = []
                for j in range(len(clusters)):
                    coord_j = clusters[j].centroid
                    cluster_distances.append([j, euc_distance(coord_i, coord_j)])

                j = min(cluster_distances, key=lambda x: x[1])[0]
                clusters[j].add_customer(i)

            # Recalculate centroid
            for cluster in clusters:
                if len(cluster.customers) == 0:
                    continue

                mean_x = sum(customers[i].x_coord for i in cluster.customers) / len(cluster.customers)
                mean_y = sum(customers[i].y_coord for i in cluster.customers) / len(cluster.customers)
                cluster.centroid = [mean_x, mean_y]

            iter_count += 1

        # Build routes
        unrouted_customers = []
        for cluster in clusters:    
            if len(cluster.customers) == 0:
                    continue

            route, unrouted = insertion_heuristic_sr(d, t, problem, customers, cluster.customers, i1_params, init_criterium)
            routes.append(route)
            unrouted_customers = unrouted_customers + unrouted

    return routes

def best_run(file_path):
	# Run the eight Solomons configurations, return the best distance-wise

	problem, customers = parse_file(file_path)
	print(f'Problem {problem.problem_id} Capacity = {problem.capacity} Vehicles = {problem.vehicle_number} Customers = {len(customers) - 1}')
	d = calculate_distances(customers)
	i1_params = [[
		1,	# mu
		2,	# lam
		1,	# alpha_1
		0,	# alpha_2
	],
	[
		1,	# mu
		1,	# lam
		1,	# alpha_1
		0,	# alpha_2
	],
	[
		1,	# mu
		1,	# lam
		0,	# alpha_1
		1,	# alpha_2
	],
	[
		1,	# mu
		2,	# lam
		0,	# alpha_1
		1,	# alpha_2
	]]
	solutions = []
	for params in i1_params:
		for i in range(2):
			routes = kmeans_vrptw(d, d, problem, customers, 10, params, i)
			solutions.append([params, i, routes_distance(routes, d), routes, routes_time(routes, d, customers)])

	return min(solutions, key=lambda x: x[2])

def main():
    # Example usage
    problem, customers = parse_file("data/r101.txt")
    print(f'Problem {problem.problem_id} Capacity = {problem.capacity} Vehicles = {problem.vehicle_number} Customers = {len(customers) - 1}')
    d = calculate_distances(customers)
    i1_params = [
		1,	# mu
		2,	# lam
		0,	# alpha_1
		1,	# alpha_2
	]
    routes = kmeans_vrptw(d, d, problem, customers, 10, i1_params, 0)
    print(routes)
    print(f'vehicles_used = {len(routes)}, total_distance = {routes_distance(routes, d)}, total_time = {routes_time(routes, d, customers)}')

    print()

    # Run all instances
    data_r1 = ("data/r101.txt", "data/r102.txt", "data/r103.txt", "data/r104.txt", "data/r105.txt","data/r106.txt", "data/r107.txt", "data/r108.txt", "data/r109.txt", "data/r110.txt","data/r111.txt", "data/r112.txt")
    data_r2 = ("data/r201.txt", "data/r202.txt", "data/r203.txt", "data/r204.txt", "data/r205.txt","data/r206.txt", "data/r207.txt", "data/r208.txt", "data/r209.txt", "data/r210.txt","data/r211.txt")
    data_c1 = ("data/c101.txt", "data/c102.txt", "data/c103.txt", "data/c104.txt", "data/c105.txt","data/c106.txt", "data/c107.txt", "data/c108.txt", "data/c109.txt")
    data_c2 = ("data/c201.txt", "data/c202.txt", "data/c203.txt", "data/c204.txt", "data/c205.txt","data/c206.txt", "data/c207.txt", "data/c208.txt")
    data_rc1 = ("data/rc101.txt", "data/rc102.txt", "data/rc103.txt", "data/rc104.txt", "data/rc105.txt","data/rc106.txt", "data/rc107.txt", "data/rc108.txt")
    data_rc2 = ("data/rc201.txt", "data/rc202.txt", "data/rc203.txt", "data/rc204.txt", "data/rc205.txt","data/rc206.txt", "data/rc207.txt", "data/rc208.txt")

    total_dist = 0
    total_routes = 0
    total_time = 0
    data_x = data_c2	# Select dataset
        
    for data in data_x:
        solution = best_run(data)
        total_routes += len(solution[3])
        total_dist += solution[2]
        total_time += solution[4]
        print(len(solution[3]))
        #print(f'Best params: mu = {solution[0][0]}, lambda = {solution[0][1]}, alpha_1 = {solution[0][2]}, alpha_2 = {solution[0][3]}, init = {init_proc(solution[1])}')
    total_dist /= len(data_x)
    total_routes /= len(data_x)
    total_time /= len(data_x)
    print(f'\nAverage: distance = {total_dist}, number of routes =  {total_routes}, time = {total_time}')

if __name__ == "__main__":
	main()

# %%
