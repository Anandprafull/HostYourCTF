To fix your Docker build and tagging process, follow these updated steps:

1. Build your Docker image (from your project root, where your Dockerfile is):
```sh
docker build -t ctfd:latest .
```
(The dot at the end is required!)

2. Tag your image for Docker Hub:
```sh
docker tag ctfd:latest prafullanand/ctfd:latest
```

3. Push your image to Docker Hub:
```sh
docker push prafullanand/ctfd:latest
```

Update your azure.md instructions to include the dot in the build command:

```markdown
docker build -t ctfd:latest .
```

---
### 1. Prepare Your Docker Image

- Make sure your CTFd Docker image works locally with docker-compose.
- Tag your image for Docker Hub (or Azure Container Registry).

Example:
```sh
docker tag ctfd:latest prafullanand/ctfd:latest
```

### 2. Push Image to Docker Hub

1. Login to Docker Hub:
   ```sh
   docker login
   ```
2. Push your image:
   ```sh
   docker push prafullanand/ctfd:latest
   ```

### 3. Install Azure CLI

- Download and install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

### 4. Login to Azure

```sh
az login
```
Follow the browser prompt to authenticate.

### 5. Create a Resource Group

```sh
az group create --name ctfd-test-rg --location eastus
```

### 6. Deploy to Azure Container Instances

```sh
az container create \
  --resource-group ctfd-test-rg \
  --name ctfd-test \
  --image prafullanand/ctfd:latest \
  --ports 80 \
  --dns-name-label ctfdtest$RANDOM \
  --location eastus
```
- Replace `<your-dockerhub-username>` with your Docker Hub username.
- The `--dns-name-label` must be unique; `$RANDOM` helps with that.

### 7. Get the Public URL

```sh
az container show --resource-group ctfd-test-rg --name ctfd-test --query ipAddress.fqdn -o tsv
```
- Open the resulting URL in your browser to access CTFd.

### 8. Test Your CTFd Instance

- Register/login as a user.
- Create a test challenge.
- Ensure teams can join and submit flags.
- Check the scoreboard and admin panel.

### 9. Clean Up (Delete Resources)

After testing, delete everything to save credits:
```sh
az group delete --name ctfd-test-rg --yes --no-wait
```

---

Here are the exact Azure CLI commands to deploy your Docker image (e.g., prafullanand/ctfd:latest) using Azure Cloud Shell or your local terminal:

1. Create a resource group:
```sh
az group create --name ctfd-test-rg --location eastus
```

2. Deploy your container to Azure Container Instances:
```sh
az container create \
  --resource-group ctfd-test-rg \
  --name ctfd-test \
  --image prafullanand/ctfd:latest \
  --ports 80 \
  --dns-name-label ctfdtest$RANDOM \
  --location eastus
```

3. Get the public URL:
```sh
az container show --resource-group ctfd-test-rg --name ctfd-test --query ipAddress.fqdn -o tsv
```
Open the resulting URL in your browser to access CTFd.

4. When finished, clean up resources:
```sh
az group delete --name ctfd-test-rg --yes --no-wait
```

Let me know if you need help with environment variables, database setup, or anything else!

If you already have an image on Docker Hub but you have made **updates or changes** to your local code (like your teams.csv or Python files), you **must** push it again to update the version that Azure uses.

Docker Hub stores "snapshots." If you don't push, Docker Hub (and consequently Azure) will continue using the old version of your code.

### How to update properly:

#### 1. Rebuild the image
This incorporates your latest changes into a new local image.
```powershell
docker build -t prafullanand/ctfd:latest .
```

#### 2. Push to overwrite (or use a new tag)
You can overwrite the `latest` tag, or better yet, use a version number so you can roll back if something breaks.

**Option A: Overwrite latest**
```powershell
docker push prafullanand/ctfd:latest
```

**Option B: Use a version tag (Recommended)**
```powershell
docker tag prafullanand/ctfd:latest prafullanand/ctfd:v2
docker push prafullanand/ctfd:v2
```

### 3. Update Azure ACI
After pushing to Docker Hub, you need to tell Azure to pull the new image. If you are using the `latest` tag, you can restart the container:

```powershell
az container restart --name ctfd-test --resource-group ctfd-test-rg
```
az group create --name ctfd-test-rg --location centralindia

If you used a **new tag** (like `v2`), you must update the container group:
```powershell
az container create --resource-group ctfd-test-rg --name ctfd-test --image prafullanand/ctfd:v2 --ports 80 --location centralindia
```

### Why do I have to push again?
*   **Azure doesn't see your local files:** Azure pulls the image from Docker Hub, not from your computer.
*   **Images are Immutable:** Once an image is built, it doesn't change. You have to "bake" a new one to include your code updates.