# ==================================================
# Parsing for the Solomon's instances
# Author: Giovanni Cesar Meira Barboza
# Date: 2024-12-23
# Description: parsing script to get problem specific values for one R, C or RC instance
# ==================================================

class Problem:
    def __init__(self, problem_id, vehicle_number, capacity):
        self.problem_id = problem_id
        self.vehicle_number = vehicle_number
        self.capacity = capacity

class Customer:
    def __init__(self, cust_no, x_coord, y_coord, demand, ready_time, due_date, service_time):
        self.cust_no = cust_no
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.demand = demand
        self.ready_time = ready_time
        self.due_date = due_date
        self.service_time = service_time

def parse_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Extract the problem ID
    problem_id = lines[0].strip()
    
    # Extract vehicle information
    for idx, line in enumerate(lines):
        if "VEHICLE" in line:
            vehicle_number, capacity = map(int, lines[idx + 2].split())
            break
    
    # Create Problem instance
    problem = Problem(problem_id, vehicle_number, capacity)
    
    # Extract customer data
    customers = []
    customer_section_found = False
    for line in lines:
        if "CUSTOMER" in line:
            customer_section_found = True
            continue
        if customer_section_found and line.strip():
            if line.strip().startswith("CUST NO."):
                continue  # Skip the header line
            # Parse customer line
            values = list(map(int, line.split()))
            cust_no, x_coord, y_coord, demand, ready_time, due_date, service_time = values
            customers.append(Customer(cust_no, x_coord, y_coord, demand, ready_time, due_date, service_time))
    
    return problem, customers

class Solution:
    def __init__(self):
        self.routes = []  # List of lists for routes
        self.cost = 0.0   # Float for cost

    def parse_solution_file(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        self._parse_lines(lines)

    def save_solution_to_file(self, file_path):
        with open(file_path, 'w') as file:
            for idx, route in enumerate(self.routes, start=1):
                file.write(f"Route #{idx}: {' '.join(map(str, route))} \n")
            file.write(f"Cost {self.cost}\n")

    def _parse_lines(self, lines):
        for line in lines:
            if line.startswith("Route #"):
                # Extract the route numbers after the colon
                route = list(map(int, line.split(":")[1].strip().split()))
                self.routes.append(route)
            elif line.startswith("Cost"):
                # Extract the cost after the word "Cost"
                self.cost = float(line.split()[1])

def main():
    file_path = "data/r101.txt"
    problem, customers = parse_file(file_path)

    # Print the parsed data
    print(f"Problem ID: {problem.problem_id}")
    print(f"Number of vehicles: {problem.vehicle_number}")
    print(f"Capacity: {problem.capacity}")
    print("Customers:")
    for customer in customers:
        print(vars(customer))

if __name__ == "__main__":
    main()
