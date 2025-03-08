# Friend Point Service: The Pester-O-Matic

This project started as a joke to mildly annoy a friend. It's a friendship tracking system to quantify your bonds.

## Overview

This service tracks friendships using a point system. It's based on my **Logarithmic Fuzzy Friend System**. Good stuff gives points, bad stuff takes them away. The better your friendship the harder it is to lose/gain points.

### Algorithm

- **Lower Bound:** Confirmed level of friendship.
- **Fuzziness Factor:** Potential for more friendship
- **Logarithmic Scaling:** Harder to level up the better friends you are.
- **Fuzzy Points:** Range of friendship points.

## Key Technical Details

- **Framework:** Flask (REST API)
- **Database:** SQLite
- **Design Pattern:** Factory Pattern (for API creation)
- **Containerization:** Docker
- **Orchestration:** Kubernetes
