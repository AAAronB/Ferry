import random
import sys
from typing import Dict, List


VEHICLE_CLASSES = [
    ("Small car", 350, 400),
    ("Medium car", 400, 450),
    ("Large car", 450, 500),
    ("Van", 500, 600),
    ("Lorry", 600, 2001),
]


def classifyVehicle(length: int) -> str:
    for label, lower, upper in VEHICLE_CLASSES:
        if lower <= length < upper:
            return label
    return "Unknown"


def laneLoad(lane: List[Dict[str, int]]) -> int:
    return sum(vehicle["length"] for vehicle in lane)


def findLaneForSmallCarRelocation(
    carLen: int, S: List[List[Dict[str, int]]], c: int, forbiddenLane: int
) -> int:
    for idx, lane in enumerate(S):
        if idx == forbiddenLane:
            continue
        if laneLoad(lane) + carLen <= c:
            return idx
    return -1


def attemptSmallCarRelocation(
    targetLaneIndex: int, requiredSpace: int, S: List[List[Dict[str, int]]], c: int
) -> bool:
    targetLane = S[targetLaneIndex]
    smallCars = [vehicle for vehicle in targetLane if vehicle["type"] == "Small car"]
    # Sort descending so we move the biggest small cars first
    smallCars.sort(key=lambda v: v["length"], reverse=True)

    movedCars = []
    spaceFreed = 0

    for car in smallCars:
        destination = findLaneForSmallCarRelocation(
            car["length"], S, c, targetLaneIndex
        )
        if destination == -1:
            continue
        targetLane.remove(car)
        S[destination].append(car)
        movedCars.append((destination, car))
        spaceFreed += car["length"]

        if spaceFreed >= requiredSpace:
            return True

    # Not enough space freed — roll back moves
    for destination, car in reversed(movedCars):
        S[destination].remove(car)
        targetLane.append(car)

    return False


def findLaneWithSmallCarRearrangement(
    carLen: int, S: List[List[Dict[str, int]]], c: int
) -> int:
    for idx in range(len(S)):
        lane = S[idx]
        freeSpace = c - laneLoad(lane)
        if freeSpace >= carLen:
            return idx

        requiredSpace = carLen - freeSpace
        if requiredSpace <= 0:
            return idx

        if attemptSmallCarRelocation(idx, requiredSpace, S, c):
            return idx

    return -1


def buildSolutionSummary(S, overflow) -> str:
    lines = []
    for i in range(len(S)):
        lane = S[i]
        lane_lengths = laneLoad(lane)
        lane_details = [
            f"{vehicle['length']}cm ({vehicle['type']})" for vehicle in lane
        ]
        lines.append(f"Ln {i}\t{lane_lengths}cm\t{lane_details}")
    overflow_details = [
        f"{vehicle['length']}cm ({vehicle['type']})" for vehicle in overflow
    ]
    lines.append("Overflow = " + str(overflow_details))
    lines.append(
        "Total length in overflow = "
        + str(sum(vehicle["length"] for vehicle in overflow))
        + " cm"
    )
    return "\n".join(lines)


def printSol(S, overflow):
    summary = buildSolutionSummary(S, overflow)
    print(summary)
    return summary


def showSolutionWindow(summary: str):
    try:
        import tkinter as tk
        from tkinter.scrolledtext import ScrolledText
    except ImportError:
        print("tkinter is not available; skipping GUI display.")
        return

    window = tk.Tk()
    window.title("Ferry Loading Results")
    window.geometry("600x400")

    text_area = ScrolledText(window, wrap=tk.WORD, state="normal")
    text_area.insert(tk.END, summary)
    text_area.config(state="disabled")
    text_area.pack(fill=tk.BOTH, expand=True)

    # Run the window in a separate blocking loop
    window.mainloop()


def getFirstLane(carLen, S, c):
    # Return the index of the first suitable lane for the current car.
    # Return -1 is there is no suitable lane
    for i in range(len(S)):
        if laneLoad(S[i]) + carLen <= c:
            return i
    return -1


def getEmptiestLaneWithCapacity(carLen, S, c):
    # Return the index of the emptiest lane with sufficient capacity for the vehicle.
    # Return -1 if there is no suitable lane
    emptiestLane = -1
    emptiestLaneSum = c + 1  # Initialize to capacity + 1
    for i in range(len(S)):
        currentSum = laneLoad(S[i])
        if currentSum + carLen <= c and currentSum < emptiestLaneSum:
            emptiestLane = i
            emptiestLaneSum = currentSum
    return emptiestLane


def getFullestLaneWithCapacity(carLen, S, c):
    # Return the index of the fullest lane with sufficient capacity for the vehicle.
    # Return -1 if there is no suitable lane
    fullestLane = -1
    fullestLaneSum = -1  # Initialize to -1
    for i in range(len(S)):
        currentSum = laneLoad(S[i])
        if currentSum + carLen <= c and currentSum > fullestLaneSum:
            fullestLane = i
            fullestLaneSum = currentSum
    return fullestLane


def getRandomLaneWithCapacity(carLen, S, c):
    # Return the index of a random lane with sufficient capacity for the vehicle.
    # Return -1 if there is no suitable lane
    suitableLanes = []
    for i in range(len(S)):
        if laneLoad(S[i]) + carLen <= c:
            suitableLanes.append(i)
    if len(suitableLanes) == 0:
        return -1
    return random.choice(suitableLanes)

def main(strategy="first"):
    # Read the problem file. All car lengths are put into the list L
    L = []
    with open("input.txt", "r") as f:
        c = int(f.readline())
        numLanes = int(f.readline())
        for line in f:
            L.append(int(line))

    # Output some basic information
    print("Number of vehicles           = " + str(len(L)))
    print("Total length of vehicles     = " + str(sum(L)) + " cm")
    print("Number of lanes              = " + str(numLanes))
    print("Capacity per lane            = " + str(c) + " cm")
    print("Strategy                     = " + strategy)

    # Declare the remaining data structures
    S: List[List[Dict[str, int]]] = [[] for i in range(numLanes)]
    overflow: List[Dict[str, int]] = []

    # Select the appropriate lane selection function based on strategy
    if strategy == "emptiest":
        getLane = getEmptiestLaneWithCapacity
    elif strategy == "fullest":
        getLane = getFullestLaneWithCapacity
    elif strategy == "random":
        getLane = getRandomLaneWithCapacity
    else:  # default to "first"
        getLane = getFirstLane

    # Here is the basic algorithm.
    for i in range(len(L)):
        carLen = L[i]
        vehicle = {"length": carLen, "type": classifyVehicle(carLen)}
        lane = getLane(carLen, S, c)
        if lane == -1:
            lane = findLaneWithSmallCarRearrangement(carLen, S, c)
        if lane != -1:
            S[lane].append(vehicle)
        else:
            overflow.append(vehicle)

    # Print details of the solution to the screen and pop out a window view
    summary = printSol(S, overflow)
    showSolutionWindow(summary)


if __name__ == "__main__":
    # Allow strategy selection via command-line argument
    # Options: "first", "emptiest", "fullest", "random"
    if len(sys.argv) > 1:
        strategy = sys.argv[1]
    else:
        strategy = input(
            "Select lane strategy (first/emptiest/fullest/random) [first]: "
        ).strip() or "first"
    main(strategy)
