*This project has been created as part of the 42 curriculum by dgajowni.*

# fly-in

## Description

fly-in loads a textual map format describing hubs and connections, then simulates and visualises autonomous "drones" moving from a start hub to an end hub. The project goal is to demonstrate graph traversal, path management, and a simple animated visualization using pygame.

## Instructions

Requirements
- Python 3.10 +
- pygame

Installation
1. Clone the repository:
   git clone git@vogsphere.42warsaw.pl:vogsphere/intra-uuid-f6a89200-8e8f-40e6-85f3-4045e521c93e-7272821-dgajowni
2. Install dependencies:
   
    make install

Execution
- Run with a map file:

    python3 fly_in.py <map_file>

- Or using the Makefile helper:

    make run MAP=<map_file>

Map files are plain text in the maps/ directory.

## Algorithm choices and implementation strategy

- Parsing: The map parser reads lines describing nb_drones, hubs (start_hub/end_hub/hub) and connections (start-end). Invalid lines terminate with an error to keep format strict.
- Graph model: Hubs and Connections form a directed graph where Connection objects link Hub instances. Each Hub keeps its outgoing Connection objects for quick traversal.
- Dead-end & loop handling: Handling dead ends and loops: The implementation first finds loops using a recursive function that deactivates a connection when it detects a second occurrence of a hub in a given path. Then, a second function removes connections to hubs that have no further connections, repeatedly, until there is nothing left to remove.
- Drone scheduling: Drones are instantiated at the start hub and progress along active connections. Movement is coordinated in discrete frames; make_moves and helper checks ensure drones only travel active paths and handle contention.
- Smooth animation: Positions between discrete hub/connection waypoints are interpolated per-frame using a weighted linear interpolation (compute_weighted_position) for smooth visuals.

## Visual representation and UX

- Rendering: Uses pygame to draw blocks, hubs and connections onto a 2D canvas.
- Hub visuals: Hubs are drawn as rounded rectangles with color encoding the zone (priority/normal/restricted/blocked). Drone counts are displayed and drones are drawn as colored circles arranged in a grid inside the hub square for clarity.
- Connection visuals: Connections are drawn as colored lines; color and line thickness indicate zone and active/inactive state (thicker when active). Restricted connections additionally show a stop marker.
- Animation: Per-frame interpolation of drone coordinates produces smooth movement; previous positions are tracked to animate transitions.
- UX benefits: Colors and shapes make network status and priorities obvious; animated drones provide immediate feedback on flow and congestion.

## Resources

AI usage
- AI assistance (GitHub Copilot) was used to draft and format this README and to write simple functions. Core algorithm and code logic remain authored and reviewed by the project maintainer.

## Project structure

- fly_in.py — main program and rendering loop
- objects/ - objects used to OOP
- maps/ — sample and user map files

