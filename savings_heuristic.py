# %%

# ==================================================
# Solomon's Paralell Savings Heuristic for the VRPTW
# Author: Giovanni Cesar Meira Barboza
# Date: 2024-12-31
# Description: Savings heuristic to solve the VRPTW. Admits Solomons R, C and RC instances
# ==================================================

from parsing import parse_file

from vrptw_functions import calculate_distances
from vrptw_functions import begin_time
from vrptw_functions import routes_distance
from vrptw_functions import routes_time

def check_time_windows(route, t, customers, maximum_wait):
	# Input: single route string, time matrix and customers
	# Output: whether the route respect time windows
	
    time = customers[0].ready_time
    for i in range(len(route)):
        if i == 0:
            time += t[0][route[i]]
        else:
            time += t[route[i - 1]][route[i]]

        # Add wait if not ready yet, forbid wait longer than maximum
        previous_time = time
        time = max(customers[route[i]].ready_time, time)
        if time - previous_time > maximum_wait:
             return False

        # Check due date
        if time > customers[route[i]].due_date:
            return False

        time += customers[route[i]].service_time

    # Check depot due date
    time += t[route[i]][0]
    if time > customers[0].due_date:
        return False

    return True

def calculate_savings(d, mu):
    # Input: triangular matrix of distances (d) between all customers and depot and measure of cost (mu)
    # Output: list of customer pairs ranked by savings

    n = len(d) - 1

    # Calculate savings for each pair of clients (i, j)
    savings = []
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            saving_value = d[0][i] + d[0][j] - mu * d[i][j]  # Clarke-Wright's savings formula
            savings.append([i, j, saving_value])

    # Sort savings in descending order
    sorted_savings = sorted(savings, key=lambda x: x[2], reverse=True)
    sorted_savings = [sublist[:-1] for sublist in sorted_savings]   # Removing the saving term

    return sorted_savings

def savings_heuristic(d, t, problem, customers, mu, maximum_wait):
    # Input: distances and time matrices, problem data, list of customers (nodes), savings parameter (mu) and maximum wait allowed
	# Output: feasible routes to the VRPTW

    pairs = calculate_savings(d, mu)

    routes = []
    unrouted_customers = [i for i in range(1, len(customers))]
    loads = []

    while len(unrouted_customers) > 0:
        for (i, j) in pairs:
            # Route starting procedure
            if i in unrouted_customers and j in unrouted_customers:
                #x = min(i, j, key=lambda x: customers[x].due_date)    # Take earliest ready_time of them to start new route
                x =  max(i, j, key=lambda customer: d[0][customer])    # Take farthest of them to start route
                routes.append([x])
                loads.append(customers[x].demand)
                unrouted_customers.remove(x)

            # Find route k where i or j is in end position
            i_first = i_last = j_first = j_last = False
            for k in range(len(routes)):
                if i == routes[k][0]:
                    i_first = True
                    break
                elif i == routes[k][len(routes[k]) - 1]:
                    i_last = True
                    break
                elif j == routes[k][0]:
                    j_first = True
                    break
                elif j == routes[k][len(routes[k]) - 1]:
                    j_last = True
                    break

            else:
                continue

            # Check vehicle capacity and if both i and j are routed
            if i_last or i_first:
                if loads[k] + customers[j].demand > problem.capacity:
                    continue
                if not (j in unrouted_customers):
                    pairs.remove([i, j])
                    continue

            else:
                if loads[k] + customers[i].demand > problem.capacity:
                    continue
                if not i in unrouted_customers:
                    (pairs.remove([i, j]))
                    continue

            # Check Time Windows feasibility
            new_route = routes[k][:]
            if i_first:
                if len(new_route) == 1 and customers[i].ready_time < customers[j].ready_time:
                    new_route = new_route + [j]
                else: 
                    new_route = [j] + new_route
            elif i_last:
                new_route = new_route + [j]
            elif j_first:
                if len(new_route) == 1 and customers[k].ready_time < customers[i].ready_time:
                    new_route = new_route + [i]
                else:
                    new_route = [i] + new_route
            elif j_last:
                new_route = new_route + [i]
            
            if (i_first or i_last) and check_time_windows(new_route, t, customers, maximum_wait):
                routes[k] = new_route
                loads[k] += customers[j].demand
                unrouted_customers.remove(j)
            elif (j_first or j_last) and check_time_windows(new_route, t, customers, maximum_wait):
                routes[k] = new_route
                loads[k] += customers[i].demand
                unrouted_customers.remove(i)
            else:
                continue

            break
        
        else:   # Impossible to merge any pair, break while
            break

    return routes

# %%
def main():
    # Example usage
    problem, customers = parse_file("data/r105.txt")
    print(f'Problem {problem.problem_id} Capacity = {problem.capacity} Vehicles = {problem.vehicle_number} Customers = {len(customers) - 1}')
    d = calculate_distances(customers)
    routes = savings_heuristic(d, d, problem, customers, 0.2, 60)
    print(routes)
    print(f'vehicles_used = {len(routes)}, total_distance = {routes_distance(routes, d)}, total_time = {routes_time(routes, d, customers)}')

    def best_run(file_path):
    # Run four configurations varying wait time and parameter mu
        problem, customers = parse_file(file_path)
        print(f'Problem {problem.problem_id} Capacity = {problem.capacity} Vehicles = {problem.vehicle_number} Customers = {len(customers) - 1}')
        d = calculate_distances(customers)
        params = [1, 0.2]
        waits = [30, 60]
        solutions = []
        for mu in params:
            for wait in waits:
                routes = savings_heuristic(d, d, problem, customers, mu, wait)
                if len(routes) <= problem.vehicle_number:
                    solutions.append([mu, wait, routes_distance(routes, d), routes, routes_time(routes, d, customers)])
            
            if not solutions:
                wait = 120
                for mu in params:
                    routes = savings_heuristic(d, d, problem, customers, mu, wait)
                    if len(routes) <= problem.vehicle_number:
                        solutions.append([mu, wait, routes_distance(routes, d), routes, routes_time(routes, d, customers)])

        return min(solutions, key=lambda x: x[2])

    
    # Run all instances
    data_r = ("data/r101.txt","data/r102.txt","data/r103.txt","data/r104.txt","data/r105.txt","data/r106.txt","data/r107.txt","data/r108.txt","data/r109.txt","data/r110.txt","data/r111.txt","data/r112.txt")
    data_c = ("data/c101.txt","data/c102.txt","data/c103.txt","data/c104.txt","data/c105.txt","data/c106.txt","data/c107.txt","data/c108.txt","data/c109.txt")
    total_dist = 0
    total_routes = 0
    total_time = 0
    data_x = data_r	# Select dataset
    def init_proc(i):
        if i == 0:
            return "farthest"
        else:
            return "earliest due-date"
        
    for data in data_x:
        solution = best_run(data)
        total_routes += len(solution[3])
        total_dist += solution[2]
        total_time += solution[4]
        print(f'Best params: mu = {solution[0]}, wait = {solution[1]}')
        print(len(solution[3]))
    total_dist /= len(data_x)
    total_routes /= len(data_x)
    total_time /= len(data_x)
    print(f'\nAverage: distance = {total_dist}, number of routes =  {total_routes}, time = {total_time}')
    

if __name__ == "__main__":
	main()

# %%
