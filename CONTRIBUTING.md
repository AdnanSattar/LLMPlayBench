# Contributing to LLMPlayBench

Thank you for your interest in contributing to LLMPlayBench! This document provides guidelines and instructions for contributing to this project.

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker and Docker Compose

### Setup Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/AdnanSattar/LLMPlayBench.git
   cd LLMPlayBench
   ```

2. Set up the backend:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:

   ```bash
   cd frontend
   npm install
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env` in both frontend and backend directories
   - Adjust settings as needed

## Development Workflow

### Running Locally

1. Start the backend:

   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Start the frontend:

   ```bash
   cd frontend
   npm run dev
   ```

3. Access the application:
   - Frontend: <http://localhost:3000>
   - Backend API: <http://localhost:8000>
   - API documentation: <http://localhost:8000/docs>

### Docker Development

You can also use Docker Compose for development:

```bash
docker-compose up --build
```

### Code Structure

- **Backend**:
  - `app/`: Main application code
    - `api/`: API endpoints and routers
    - `core/`: Configuration and core functionality
    - `models/`: Database and ML model definitions
    - `schemas/`: Data validation schemas
    - `services/`: Business logic services
  - `migrations/`: Database migrations
  - `tests/`: Unit and integration tests

- **Frontend**:
  - `src/`: Source code
    - `components/`: Reusable UI components
    - `lib/`: Utilities and API client
    - `pages/`: Main page components
    - `styles/`: CSS styles

## Coding Standards

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions and classes
- Format code with Black and isort
- Include author information in all new files

### Frontend (JavaScript/React)

- Follow ESLint and Prettier configuration
- Use functional components with hooks
- Include JSDoc comments for functions and components
- Include author information in all new files

## Pull Request Process

1. Fork the repository
2. Create a new branch for your feature/fix
3. Write your code and tests
4. Ensure all tests pass and code is formatted correctly
5. Submit a pull request with a clear description of the changes

## Commit Guidelines

- Use descriptive commit messages
- Reference issue numbers in commits when applicable
- Keep commits focused on a single task

## Adding Features

When adding new features:

1. Start by creating an issue describing the feature
2. Update the `TODO.md` file with your planned implementation
3. Implement the feature with appropriate tests
4. Update documentation to reflect changes
5. Submit a pull request

## Running Tests

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Documentation

- Update `README.md` for user-facing changes
- Update `docs/API.md` for API changes
- Create/update other documentation as needed

## License

By contributing to LLMPlayBench, you agree that your contributions will be licensed under the project's MIT license.

## Contact

If you have any questions or need help, please contact:

- Adnan Sattar
  - Email: <adnansattar09@gmail.com>
  - GitHub: <https://github.com/AdnanSattar>
  - LinkedIn: <https://www.linkedin.com/in/adnansattar09/>
  