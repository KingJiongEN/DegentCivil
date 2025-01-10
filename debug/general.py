import matplotlib.pyplot as plt

# Data provided in the table
teams = ['A', 'B', 'C']
salaries = {
    'Salary One': [48.60, 49.60, 100.80],
    'Salary Two': [53.60, 58.20, 110.40],
    'Salary Three': [59.60, 63.60, 117.80]
}

# Plotting the salaries over the three time points for each team
plt.figure(figsize=(10, 8))
for team in teams:
    plt.plot(salaries.keys(), [salaries[salary][teams.index(team)] for salary in salaries], marker='o', label=f'Team {team}')

# Adding title and labels
plt.title('Trends in Salaries Over Time by Team')
plt.xlabel('Time Points')
plt.ylabel('Mean Salary')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
