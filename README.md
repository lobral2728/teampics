# Health Check Application

A simple containerized application with a WebUI frontend and a backend API designed to run on Docker locally and deployable to Azure.

## Architecture

- **Frontend**: Node.js/Express web server serving a single-page application with a health check button
- **Backend**: Python Flask API with health check endpoints
- **Containerization**: Docker containers orchestrated with Docker Compose

## Project Structure

```
azuretest001/
├── backend/
│   ├── app.py              # Flask API with health endpoints
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container configuration
├── frontend/
│   ├── server.js           # Express server
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile          # Frontend container configuration
├── docker-compose.yml      # Multi-container orchestration
└── README.md              # This file
```

## Features

- **Backend API**:
  - `/health` - Returns health status with timestamp
  - `/ping` - Simple ping/pong endpoint
  - CORS enabled for cross-origin requests
  
- **Frontend WebUI**:
  - Clean, modern interface
  - Single button to ping backend
  - Visual feedback (success/error/loading states)
  - Real-time status display

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Running Locally with Docker

### Quick Start

1. **Clone or navigate to the project directory**:
   ```powershell
   cd c:\Users\lobra\Documents\Repos\azuretest001
   ```

2. **Build and start both containers**:
   ```powershell
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/health

4. **Stop the application**:
   ```powershell
   # Press Ctrl+C in the terminal, then:
   docker-compose down
   ```

### Individual Container Commands

**Backend only**:
```powershell
cd backend
docker build -t healthcheck-backend .
docker run -p 5000:5000 healthcheck-backend
```

**Frontend only**:
```powershell
cd frontend
docker build -t healthcheck-frontend .
docker run -p 3000:3000 -e BACKEND_URL=http://localhost:5000 healthcheck-frontend
```

## Testing the Application

1. Open your browser to http://localhost:3000
2. Click the "Ping Backend" button
3. You should see a success message with:
   - Backend status
   - Response message
   - Timestamp

## Development

### Backend Development (without Docker)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Frontend Development (without Docker)

```powershell
cd frontend
npm install
npm start
```

## Docker Commands Reference

```powershell
# Build containers
docker-compose build

# Start containers in foreground
docker-compose up

# Start containers in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# List running containers
docker ps

# View backend logs
docker logs healthcheck-backend

# View frontend logs
docker logs healthcheck-frontend
```

## Environment Variables

### Backend
- `FLASK_ENV`: Set to `production` or `development`

### Frontend
- `BACKEND_URL`: URL of the backend API (default: `http://backend:5000` in Docker)
- `PORT`: Frontend server port (default: `3000`)

## Next Steps: Azure Deployment

This application is ready for Azure deployment. Potential Azure services:

1. **Azure Container Instances (ACI)**: Simplest option for running containers
2. **Azure Container Apps**: Serverless container platform with auto-scaling
3. **Azure Kubernetes Service (AKS)**: For production-grade orchestration
4. **Azure App Service**: Container deployment with managed infrastructure

### Prerequisites for Azure
- Azure CLI installed
- Azure subscription
- Azure Container Registry for storing images

## Troubleshooting

**Backend not responding**:
- Check if backend container is running: `docker ps`
- View backend logs: `docker logs healthcheck-backend`
- Test backend directly: http://localhost:5000/health

**Frontend can't reach backend**:
- Ensure both containers are on the same network
- Check `BACKEND_URL` environment variable
- Verify CORS is enabled in backend

**Port already in use**:
- Change ports in `docker-compose.yml`
- Or stop the process using the port

## Repository Management

### Before First Commit

This repository includes large files and secrets that should NOT be committed:

**Already Protected** (via `.gitignore`):
- ✅ Machine learning models (`*.h5`, `*.keras`, `*.weights.h5`) - 90-100MB each
- ✅ Python cache (`__pycache__/`, `*.pyc`)
- ✅ Environment files (`.env`, `*.tfvars`)
- ✅ Terraform state and providers (`.terraform/`)
- ✅ Node modules (`node_modules/`)
- ✅ Secrets and credentials

**Safe to Commit**:
- ✅ Source code (`*.py`, `*.js`, `*.html`)
- ✅ Dockerfiles and docker-compose.yml
- ✅ Documentation (`*.md`)
- ✅ Configuration templates (`.env.example`, `*.tfvars.example`)
- ✅ Small test images in `profile_images/` (sample data)

**Important**: See `SECURITY.md` for complete secrets management guide.

### Initial Commit Commands

```bash
# Check what will be committed
git status

# Add all files (respects .gitignore)
git add .

# Verify no secrets are staged
git status | Select-String ".env|.tfvars|secret"

# Commit
git commit -m "Initial commit: Health Check application with ML classification"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/azuretest001.git

# Push to remote
git push -u origin main
```

### Model Files Note

The trained ML models (90-100MB each) are excluded from git. For deployment:
1. Models are included in Docker images (built locally, pushed to ACR)
2. For team sharing, consider Azure Blob Storage or Git LFS
3. Current deployment: Models built into container images

## License

MIT
# profile_pic_app
