# Friend Point Service: The Pester-O-Matic

This project started as a joke to mildly annoy a friend. It's a friendship tracking system to quantify your bonds. It also gave me an excuse to deploy an HTTP service on my personal Kubernetes cluster, routing through Cloudflare Zero Trust.

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

## Deployment on Kubernetes and Cloudflare Zero Trust

1.  **Build and Push the Docker Image:**

    *   **Build the image:**

        ```bash
        docker build -t friendship-service:latest .
        ```

        *This builds the image locally.  You can tag it with your Docker Hub username if you intend to push it to a registry.*

    *   **(Optional) Tag and Push the image:**

        ```bash
        docker tag friendship-service:latest your-dockerhub-username/friendship-service:latest
        docker login
        docker push your-dockerhub-username/friendship-service:latest
        ```

        *Replace `your-dockerhub-username` with your Docker Hub username (or your container registry).*

        *If you skip this step, Kubernetes will attempt to pull the image locally, which is fine for a single-node cluster or local testing.*

2.  **Deploy to Kubernetes:**

    *   Apply the Kubernetes manifests:

        ```bash
        kubectl apply -f kubernetes/pvc.yaml
        kubectl apply -f kubernetes/deployment.yaml
        kubectl apply -f kubernetes/service.yaml
        ```

3.  **Expose via Ingress (Optional):**

    *   If you're not using Cloudflare Tunnel, you'll need an Ingress to expose the service.  Make sure your Ingress controller is properly configured.

4.  **Cloudflare Zero Trust Configuration (using Cloudflare Tunnel):**

    *   **Create a Cloudflare Tunnel:** Follow Cloudflare's documentation to set up a tunnel connecting your cluster to Cloudflare.
    *   **Configure the Tunnel:**  When configuring the tunnel, you'll route traffic to the `friendship-service` Kubernetes service.  The key is to route traffic to the *internal* Kubernetes service name and port.
    *   **No Public Ports Needed:** Because you're using Cloudflare Tunnel, you *don't* need to expose any public ports on your Kubernetes nodes.  The tunnel handles the secure connection.
    *   **Set up Access Policies:** In Cloudflare Zero Trust, define access policies to control who can access the service.  This is where you'll configure authentication (e.g., requiring users to log in with their Cloudflare accounts).

5.  **Cloudflare DNS Settings (if using Ingress):**

    *   Create a DNS record in Cloudflare that points to your Ingress controller's external IP address or hostname.
    *   Enable Cloudflare's proxy (the orange cloud) on the DNS record.

6.  **Ports and Cloudflare:**

    *   **Kubernetes Service Port:** The `targetPort` in your `kubernetes/service.yaml` (currently `5000`) is the port your application listens on *inside* the container.
    *   **Cloudflare Tunnel:** Cloudflare Tunnel connects directly to the Kubernetes service, so you don't need to expose any specific ports publicly.
    *   **Ingress (if not using Tunnel):** If you're using an Ingress, Cloudflare will connect to your Ingress controller on ports 80 or 443 (HTTPS). The Ingress controller will then route the traffic to your service on port 5000.
