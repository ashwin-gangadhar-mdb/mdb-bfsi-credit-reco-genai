# BFSI Credit Recommendation & Scoring Application

A modular, containerized full-stack solution for BFSI credit recommendation and scoring, featuring a Python/Flask backend, a React/Next.js frontend, and MongoDB for persistent storage.

## Features

- Secure user authentication and credit profile management
- Automated credit score calculation with explainability
- Personalized credit card product recommendations
- RESTful API endpoints for integration
- Containerized deployment using Docker Compose

## Architecture Overview

### Components

- **Backend**: Python (Flask) API for credit scoring, recommendations, and data management.
- **Frontend**: React/Next.js application for user interaction and visualization.
- **Database**: MongoDB for storing user profiles, credit scores, and recommendations.

### Backend

- **Framework**: Flask (Python)
- **Key Modules**:
    - `app.py`: Main Flask app, API endpoints for login, credit scoring, and product suggestions.
    - `credit_rating.py`: Loads ML models and computes credit scores.
    - `credit_score_expl.py`: Generates LLM-based explanations for credit scores.
    - `credit_product_recommender.py`: Recommends credit cards using LLM and vector search.
    - `graph.py`: Orchestrates agentic workflows with LangGraph.
    - `utils.py`: MongoDB connection and shared utilities.
    - `stat_score_util.py`: Traditional/statistical credit score calculations.
    - `dummy.py`: Data preprocessing utilities.
    - `llm_utils.py`: LLM and vector store setup (LangChain, Fireworks, MongoDB Atlas).
- **Persistence**: MongoDB (PyMongo), with collections for user data and responses.
- **ML/LLM**: Integrates pre-trained models (joblib), LangChain for LLM orchestration, and vector search for product retrieval.

### Frontend

- **Framework**: React/Next.js
- **Features**:
    - User login and authentication
    - Dashboard for credit profile and score visualization
    - Product recommendations display
    - Profile editing and updates
- **API Integration**: Communicates with backend via REST endpoints.

### Database

- **MongoDB**:
    - Stores user profiles, credit scores, recommendations, and product catalog.
    - Supports both transactional data and vector search for product recommendations.

### Containerization & Deployment

- **Docker Compose**: Orchestrates backend, frontend, and MongoDB containers.
- **Makefile**: Provides shortcuts for build, up, down, logs, backend, and frontend commands.

### Data Flow

1. **User Login**: Frontend sends credentials to `/login`. Backend authenticates and triggers agentic workflow.
2. **Credit Scoring**: Backend computes credit score using ML/statistical models and stores results in MongoDB.
3. **Recommendations**: LLM and vector search modules generate personalized credit card recommendations.
4. **Frontend Display**: User views credit profile, score, and recommendations. Profile updates trigger backend re-computation.

### Extensibility

- **ML Models**: Easily replaceable or upgradable (joblib files).
- **LLM/Vector Search**: Modular, allowing provider/model swaps.
- **API**: RESTful endpoints for integration with other systems.

---

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/)

## Quick Start

### 1. Clone the Repository

```sh
git clone <repo-url>
cd mdb-bfsi-credit-reco-genai
```

### 2. Configure Environment Variables

Edit the `.env` file in the root directory as needed. Example:

```env
MONGO_CONNECTION_STRING=mongodb://root:example@mongo:27017/?authSource=admin
FIREWORKS_API_KEY=fw_
# Add other keys as needed
```

### 3. Build and Run with Docker Compose

```sh
make build
make up
```

This will build and start the following services:

- **backend**: Python backend (Flask) on ports 8000 and 5001
- **frontend**: Node.js frontend on port 3000
- **mongo**: MongoDB database on port 27017

### 4. Access the Application

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:5001](http://localhost:5001)

### 5. Stopping the Application

```sh
make down
```

## Development

- View logs: `make logs`
- Start only backend or frontend: `make backend` or `make frontend`

## API Endpoints

- `POST /login`: User login
- `GET /credit_score/<user_id>`: Retrieve credit score and profile
- `POST /product_suggestions`: Get product recommendations (expects JSON body)
- `GET /product_suggestions/<user_id>`: Get product recommendations by user ID

## Project Structure

```
backend_agentic/   # Python backend code
frontend/          # Frontend code (React/Next.js)
docker-compose.yaml
.env
Makefile
```

## Testing

To run backend tests:

```sh
cd backend_agentic
python -m pytest test_app.py 
```

## License

MIT License (add your license here)
