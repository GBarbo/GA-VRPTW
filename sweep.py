# ==================================================
# Solomon's Sweep Heuristic for the VRPTW
# Author: Giovanni Cesar Meira Barboza
# Date: 2025-01-03
# Description: Sweep to solve the VRPTW. Admits Solomons R, C and RC instances
# ==================================================

from math import atan2
from parsing import parse_file
from vrptw_functions import calculate_distances
from vrptw_functions import routes_distance
from vrptw_functions import routes_time
from solomon_insertion import c11, c12
from solomon_insertion import check_time_windows
from solomon_insertion import insertion

from math import atan2

def calculate_angles(customers):
    # Input: list of customers
    # Output: customer indices ranked by angle counter-clockwise and the angles list

    x0 = customers[0].x_coord
    y0 = customers[0].y_coord

    # Compute angles and associate them with customer indices
    customer_angles = []
    for i in range(1, len(customers)):
        xi = customers[i].x_coord
        yi = customers[i].y_coord
        angle = atan2(yi - y0, xi - x0)
        if angle < 0:
            angle += 2*3.1415
        customer_angles.append((i, angle))  # Store index and angle

    # Sort customers by angle in anti-clockwise order
    sorted_customers = sorted(customer_angles, key=lambda x: x[1])

    # Extract the indices of customers in sorted order
    sorted_indices = [index for index, _ in sorted_customers]

    return sorted_indices, customer_angles

def insertion_heuristic_st(d, t, problem, customers, cluster, i1_params, init_criterium):
    # Adapted insertion heuristic to deal with single tour building
    # Returns route and unrouted customers from a single set (cluster)

    mu, lam, alpha_1, alpha_2 = i1_params

    route = []
    unrouted_customers = cluster[:]
    load = 0

    # Initialization
    if init_criterium == 0:  # 0: fartherst unrouted customer
        farthest_customer = max(unrouted_customers, key=lambda customer: d[0][customer])
        route = [farthest_customer]
        unrouted_customers.remove(farthest_customer)
    elif init_criterium == 1:   # 1: earliest deadline unrouted customer
        earliest_deadline_customer = min(unrouted_customers, key=lambda i: customers[i].due_date)
        route = [earliest_deadline_customer]
        unrouted_customers.remove(earliest_deadline_customer)

    while True:
        # Compute best feasible insertion place in the current route for each unrouted customer (min(c1))
        insertion_candidates = []
        for u in unrouted_customers:
            # Capacity check
            new_load = load + customers[u].demand
            if new_load > problem.capacity:
                continue

            feasible_insertion_places = []
            for i, j in zip([0] + route, route + [0]):
                # Time window feasibility
                new_route = insertion(route, u, (i, j))
                if not check_time_windows(new_route, t, customers):
                    continue
            
                c1 = alpha_1 * c11(i, u, j, d, mu) + alpha_2 * c12(u, j, route, t, customers)
                feasible_insertion_places.append([u, (i, j), c1])
        
            if not feasible_insertion_places:
                continue

            # Only let the best insertion place be a candidate for each unrouted customer, then calculate c2
            best_place = min(feasible_insertion_places, key=lambda x: x[2])
            c2 = lam * d[0][u] - best_place[2]
            insertion_candidates.append([u, best_place[1], c2])

        if not insertion_candidates:
            break

        # Make best feasible insertion and update load
        u, (i, j), c2 = max(insertion_candidates, key=lambda x: x[2])
        new_route = insertion(route, u, (i, j))
        route = new_route[:]
        unrouted_customers.remove(u)
        load += customers[u].demand

    return route, unrouted_customers

def bissect(unrouted, angles):
    # Reorder unrouted according to the angle distance to the customer with smallest angle

    # Filter angles to include only indices in unrouted
    filtered_angles = [(idx, angle) for idx, angle in angles if idx in unrouted]

    # Find the index with the smallest angle
    reference_idx, reference_angle = min(filtered_angles, key=lambda x: x[1])

    # Sort the filtered list by increasing difference of angle from the reference angle
    sorted_angles = sorted(filtered_angles, key=lambda x: abs(x[1] - reference_angle))

    # Extract the indices in sorted order
    sorted_indices = [idx for idx, _ in sorted_angles]

    return sorted_indices

def sweep_heuristic(d, t, problem, customers, i1_params, init_criterium):
    # Input: distances and time matrices, problem data, list of customers (nodes) and insertion parameters
	# Output: feasible routes to the VRPTW

    routes = []
    clusters = [[]]

    # Start unrouted customers by ranking them by increasing angle
    unrouted_customers, angles = calculate_angles(customers)

    # Phase 1: Gillett-Miller's tour building with insertion heuristic
    load = 0
    for i in unrouted_customers:
        if load + customers[i].demand <= problem.capacity:
            clusters[-1].append(i)  # Add to the current cluster
            load += customers[i].demand
        else:
            # Start a new cluster and add the customer
            clusters.append([i])
            load = customers[i].demand

    unrouted_customers = []
    for cluster in clusters:
        route, unrouted = insertion_heuristic_st(d, t, problem, customers, cluster, i1_params, init_criterium)
        routes.append(route)
        unrouted_customers = unrouted_customers + unrouted

    # Phase 2: iterative bissection and tour building with unscheduled customers
    while len(unrouted_customers) > 0:
        unrouted_customers = bissect(unrouted_customers, angles)
        clusters = [[]]
        load = 0
        for i in unrouted_customers:
            if load + customers[i].demand <= problem.capacity:
                clusters[-1].append(i)  # Add to the current cluster
                load += customers[i].demand
            else:
                # Start a new cluster and add the customer
                clusters.append([i])
                load = customers[i].demand

        unrouted_customers = []
        for cluster in clusters:
            route, unrouted = insertion_heuristic_st(d, t, problem, customers, cluster, i1_params, init_criterium)
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
			routes = sweep_heuristic(d, d, problem, customers, params, i)
			solutions.append([params, i, routes_distance(routes, d), routes, routes_time(routes, d, customers)])

	return min(solutions, key=lambda x: x[2])

def main():
    # Example usage
    problem, customers = parse_file("data/c201.txt")
    print(f'Problem {problem.problem_id} Capacity = {problem.capacity} Vehicles = {problem.vehicle_number} Customers = {len(customers) - 1}')
    i1_params2 = [
		1,	# mu
		1,	# lam
		1,	# alpha_1
		0,	# alpha_2
	]
    d = calculate_distances(customers)
    routes = sweep_heuristic(d, d, problem, customers, i1_params2, 0)
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
