# GitHub Configuration for LLMPlayBench

This directory contains configuration files for GitHub features and CI/CD workflows.

## Workflows

### CI/CD Pipeline (`ci-cd.yml`)

The main CI/CD workflow that runs when code is pushed to `main` or `master` branches, or when a tag is created:

1. **Linting**: Checks code quality for both backend and frontend
2. **Testing**: Runs unit tests for both backend and frontend
3. **Building**: Builds Docker images for backend and frontend
4. **Deployment**: Deploys the application to production (when triggered on main branch or manually)

### Pull Request Checks (`pr-check.yml`)

Validates pull requests before they can be merged:

1. **Validate PR**: Ensures PR titles follow semantic conventions
2. **Code Quality**: Checks code formatting and quality
3. **Docker Build**: Tests that Docker images build successfully

### Security Checks (`security.yml`)

Runs security scans on the codebase:

1. **Dependency Scanning**: Checks for vulnerabilities in dependencies
2. **Docker Scanning**: Scans Docker images for vulnerabilities
3. **Secret Scanning**: Ensures no secrets are committed to the repository

### Dependency Updates (`dependencies.yml`)

Automatically updates dependencies:

1. **Backend Dependencies**: Updates Python dependencies
2. **Frontend Dependencies**: Updates NPM dependencies
3. Creates pull requests for review when updates are found

### Documentation (`docs.yml`)

Builds and publishes documentation:

1. **Build Docs**: Generates documentation from Markdown files
2. **Deploy**: Publishes documentation to GitHub Pages

## CODEOWNERS

The `CODEOWNERS` file defines who should be requested for review when a pull request is opened.

## Required Secrets

The following secrets need to be configured in your GitHub repository:

1. `DOCKERHUB_USERNAME`: Your Docker Hub username
   - Purpose: Used to authenticate with Docker Hub for pushing images
   - How to get: Create a Docker Hub account at https://hub.docker.com/

2. `DOCKERHUB_TOKEN`: Your Docker Hub access token
   - Purpose: Used for authentication instead of your password
   - How to get: Go to Docker Hub > Account Settings > Security > New Access Token

3. `SSH_PRIVATE_KEY`: SSH private key for deployment
   - Purpose: Authenticates with your production server
   - How to generate: `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`
   - Note: Add the public key to your server's authorized_keys file

4. `SSH_KNOWN_HOSTS`: Known hosts configuration for SSH
   - Purpose: Prevents man-in-the-middle attacks
   - How to get: `ssh-keyscan -H your-server-hostname >> known_hosts`

5. `SSH_USER`: Username for SSH connection
   - Purpose: Specifies which user to connect as on your server
   - Example: `ubuntu`, `ec2-user`, etc.

6. `SSH_HOST`: Host for SSH connection
   - Purpose: Specifies which server to deploy to
   - Example: `example.com`, `123.456.789.0`, etc.

## Configuration

To set up the CI/CD pipeline:

1. Go to your repository settings
2. Navigate to "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add each of the required secrets listed above
5. Enable GitHub Pages in the repository settings if you want to publish documentation

## Manual Triggers

The following workflows can be triggered manually from the "Actions" tab:

- `CI/CD Pipeline`: Use the "workflow_dispatch" trigger with the option to deploy
- `Dependency Updates`: Use the "workflow_dispatch" trigger to check for updates
- `Documentation`: Use the "workflow_dispatch" trigger to rebuild and publish docs
