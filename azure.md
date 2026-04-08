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