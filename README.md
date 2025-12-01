## Ferry Loading Visualiser

This project simulates loading vehicles onto a ferry with multiple lanes and visualises the result. This is something small that I worked on for fun.

### Files

- `ferry.py`: Command-line version that computes a loading solution and prints it as text.
- `GUI.py`: GUI version that computes a solution and opens a Tkinter window with:
  - A **coloured visual** of the first **10 lanes** (by vehicle type).
  - A **text summary** of the same lanes plus overflow details.
- `input.txt`: Example input data (capacity, number of lanes, and a list of vehicle lengths in cm).

### Vehicle types and colours (GUI)

- Small car: **red**
- Medium car: **orange**
- Large car: **green**
- Van: **blue**
- Lorry: **purple**

### Running the programs

1. Make sure you have **Python 3** installed.
2. Ensure `input.txt` is in the same directory as the scripts.

Where `strategy` is one of:

- `first` (default): first lane with enough remaining capacity
- `emptiest`: emptiest lane that can still fit the vehicle
- `fullest`: fullest lane that can still fit the vehicle
- `random`: random lane among those with enough capacity


