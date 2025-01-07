# ==================================================
# Time-Oriented Nearest Neighbor
# Author: Giovanni Cesar Meira Barboza
# Date: 2024-01-07
# Description: Solomon's Time-Orineted NN for the VRPTW. Admits Solomons R, C and RC instances
# ==================================================


from parsing import parse_file
from vrptw_functions import calculate_distances
from vrptw_functions import begin_time
from vrptw_functions import check_time_windows
from vrptw_functions import routes_distance
from vrptw_functions import routes_time

def time_oriented_nn(d, t, problem, customers, to_params):
    # Input: distances and time matrices, problem data and list of customers (nodes)
    # Output: feasible routes to the VRPTW

    delta_1, delta_2, delta_3 = to_params

    routes = []
    unrouted_customers = [i for i in range(1, len(customers))]

    while len(unrouted_customers) > 0:
        route = []
        load = 0
        
        while True:
            if not route:
                j = 0
            else:
                j = route[len(route) - 1]

            # Calculate cost of appendage for each unrouted customer
            append_candidates = []
            for i in unrouted_customers:
                if load + customers[i].demand > problem.capacity:
                    continue
                
                new_route = route[:]
                new_route.append(i)

                if not check_time_windows(new_route, t, customers):
                    continue
                
                T = begin_time(j, new_route, t, customers) - (begin_time(i, new_route, t, customers) + customers[i].service_time)
                v = customers[j].due_date - (begin_time(i, new_route, t, customers) + customers[i].service_time + t[i][j])

                cij = delta_1 * d[i][j] + delta_2 * T + delta_3 * v

                append_candidates.append([i, cij])
                
            if not append_candidates:
                routes.append(route)
                break
            
            # Append feasible customer of minimum cost
            i = max(append_candidates, key=lambda x: x[1])[0]
            route.append(i)
            load += customers[i].demand
            unrouted_customers.remove(i)

    return routes   

def best_run(file_path):
    # Run the eight Solomons configurations, return the best distance-wise

    problem, customers = parse_file(file_path)
    print(f'Problem {problem.problem_id} Capacity = {problem.capacity} Vehicles = {problem.vehicle_number} Customers = {len(customers) - 1}')
    d = calculate_distances(customers)
    to_params = [
            [
            0.4,    # delta_1
            0.4,    # delta_2
            0.2     # delta_3
            ],
            [
            0.0,    # delta_1
            1.0,    # delta_2
            0.0     # delta_3
            ],
            [
            0.5,    # delta_1
            0.5,    # delta_2
            0.0     # delta_3
            ],
            [
            0.3,    # delta_1
            0.3,    # delta_2
            0.4     # delta_3
            ]
    ]
    solutions = []
    for params in to_params:
        routes = time_oriented_nn(d, d, problem, customers, params)
        solutions.append([params, 0, routes_distance(routes, d), routes, routes_time(routes, d, customers)])

    return min(solutions, key=lambda x: x[2])
def main():
    # Example usage
    problem, customers = parse_file("data/r101.txt")
    print(f'Problem {problem.problem_id} Capacity = {problem.capacity} Vehicles = {problem.vehicle_number} Customers = {len(customers) - 1}')
    d = calculate_distances(customers)
    to_params = [
        0.3,    # delta_1
        0.3,    # delta_2
        0.4     # delta_3
    ]
    routes = time_oriented_nn(d, d, problem, customers, to_params)
    print(routes)
    print(f'vehicles_used = {len(routes)}, total_distance = {routes_distance(routes, d)}, total_time = {routes_time(routes, d, customers)}')
    
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
        print(f'Best params: delta_1 = {solution[0][0]}, delta_2 = {solution[0][1]}, delta_3 = {solution[0][2]}')
    total_dist /= len(data_x)
    total_routes /= len(data_x)
    total_time /= len(data_x)
    print(f'\nAverage: distance = {total_dist}, number of routes =  {total_routes}, time = {total_time}')

if __name__ == "__main__":
	main()
