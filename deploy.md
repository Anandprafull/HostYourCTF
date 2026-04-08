# Deploying CTFd on Azure Container Instances (ACI)

This guide walks you through building, pushing, deploying, updating, and cleaning up a Dockerized CTFd instance on Azure using Azure Container Instances.

---

## 1. Build and Push Your Docker Image

1. **Build your Docker image locally:**
   ```sh
   docker build -t ctfd:latest .
   ```
2. **Tag your image for Docker Hub:**
   ```sh
   docker tag ctfd:latest <your-dockerhub-username>/ctfd:latest
   ```
3. **Login to Docker Hub:**
   ```sh
   docker login
   ```
4. **Push your image:**
   ```sh
   docker push <your-dockerhub-username>/ctfd:latest
   ```

---

## 2. Deploy to Azure Container Instances

1. **Open Azure Cloud Shell** (or use Azure CLI locally).
2. **Create a resource group (choose a supported region, e.g., centralindia):**
   ```sh
   az group create --name ctfd-test-rg --location centralindia
   ```
3. **Deploy your container (expose the correct port, e.g., 8000):**
   ```sh
   az container create \
     --resource-group ctfd-test-rg \
     --name ctfd-test \
     --image <your-dockerhub-username>/ctfd:latest \
     --ports 8000 \
     --dns-name-label ctfdtest$RANDOM \
     --location centralindia \
     --os-type Linux \
     --cpu 1 \
     --memory 1.5
   ```

---

## 3. Access Your CTFd Instance

1. **Get the public FQDN:**
   ```sh
   az container show --resource-group ctfd-test-rg --name ctfd-test --query ipAddress.fqdn -o tsv
   ```
2. **Open in your browser:**
   ```
   http://<fqdn>:8000
   ```

---

## 4. Update Environment Variables or Code

- Edit your files locally, rebuild, push, and redeploy as above.
- To update the CTFd URL or admin token inside the container (if needed):
   ```sh
   az container exec --resource-group ctfd-test-rg --name ctfd-test --exec-command "/bin/sh"
   sed -i 's|CTFd_URL = ".*"|CTFd_URL = "http://<fqdn>:8000/"|' import_challenges.py
   sed -i 's|ADMIN_TOKEN = ".*"|ADMIN_TOKEN = "<your_new_token>"|' import_challenges.py
   ```

---

## 5. Run Management Commands Inside the Container

- To run a script (e.g., import_challenges.py):
   ```sh
   az container exec --resource-group ctfd-test-rg --name ctfd-test --exec-command "python import_challenges.py"
   ```

---

## 6. View Logs

```sh
az container logs --resource-group ctfd-test-rg --name ctfd-test
```

---

## 7. Restart or Delete the Container

- **Restart:**
  ```sh
  az container restart --resource-group ctfd-test-rg --name ctfd-test
  ```
- **Delete (stop):**
  ```sh
  az container delete --resource-group ctfd-test-rg --name ctfd-test --yes
  ```
- **Delete the resource group (removes all resources):**
  ```sh
  az group delete --name ctfd-test-rg --yes --no-wait
  ```

---

## Notes
- Always use the correct port (default CTFd is 8000).
- If you need to edit files, do so locally and redeploy for best results.
- For persistent SSH or advanced features, consider Azure Web App for Containers or a VM.

---

**Replace placeholders like `<your-dockerhub-username>`, `<fqdn>`, and `<your_new_token>` with your actual values.**
