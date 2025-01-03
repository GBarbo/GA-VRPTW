# ==================================================
# VRPTW functions
# Author: Giovanni Cesar Meira Barboza
# Date: 2024-12-31
# Description: restrictions and calculation functions to use in multiple VRPTW heuristics
# ==================================================

def calculate_distances(customers):
	n = len(customers) - 1
	d = []

	for i in range(n + 1):
		d.append([])
		for j in range(n + 1):
			dij = ((customers[i].x_coord - customers[j].x_coord)**2 + (customers[i].y_coord - customers[j].y_coord)**2)**(1/2)
			d[i].append(dij)	

	return d

def begin_time(j, route, t, customers):
    # Calculate the beggining of the service of j
	# Returns whole route time if j is not in the route

	time = customers[0].ready_time
	for i in range(len(route)):
		if i == 0:
			time += t[0][route[i]]
		else:
			time += t[route[i - 1]][route[i]]
		
		# Add wait if not ready yet
		time = max(customers[route[i]].ready_time, time)

		if route[i] == j:
			return time
		
		time += customers[route[i]].service_time

	else:
		time += t[route[len(route) - 1]][0]
		return time
	
def check_time_windows(route, t, customers):
	# Input: single route string, time matrix and customers
	# Output: whether the route respect time windows
	
	time = customers[0].ready_time
	for i in range(len(route)):
		if i == 0:
			time += t[0][route[i]]
		else:
			time += t[route[i - 1]][route[i]]

		# Add wait if not ready yet, this way the ready time will always be feasible
		time = max(customers[route[i]].ready_time, time)

		# Check due date
		if time > customers[route[i]].due_date:
			return False
		
		time += customers[route[i]].service_time

	# Check depot due date
	time += t[route[i]][0]
	if time > customers[0].due_date:
		return False
	
	return True

def routes_distance(routes, d):
	total_distance = 0
	for route in routes:
		for i in range(len(route)):
			if i == 0:
				total_distance += d[0][route[i]]
			else:
				total_distance += d[route[i-1]][route[i]]

			if i == len(route) - 1:
				total_distance += d[route[i]][0]

	return total_distance

def routes_time(routes, t, customers):
	total_time = 0
	for route in routes:
		total_time += begin_time(-1, route, t, customers)

	return total_time