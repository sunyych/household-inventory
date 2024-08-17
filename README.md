# Home Inventory App

This project is a web application for managing household inventory and recording audio. It features a React frontend with Next.js, and a Django backend with PostgreSQL. The app allows users to manage their inventory, record audio, and process it with an LLM (using Ollama).
It is able to fully local run and serve by ngrok

## Features

- Manage household inventory (CRUD operations)
- Record and transcribe audio
- Integration with Ollama for LLM processing
- Dark mode support

## Prerequisites

Before you begin, ensure you have the following installed:

- [Node.js](https://nodejs.org/) (v14 or higher)
- [Python](https://www.python.org/) (v3.8 or higher)
- [Docker](https://www.docker.com/) (for running PostgreSQL and Django)
- [Git](https://git-scm.com/)

## Getting Started

### 1. Clone the Repository

```bash
git clone git@github.com:sunyych/household-inventory.git
cd household-inventory
```

### 2. Set Up the Backend

#### 2.1. Create and Activate a Virtual Environment

```bash
python -m venv hi
source hi/bin/activate  # On Windows use `hi\Scripts\activate`
```

#### 2.2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3. Set Up the Database

Ensure Docker is running and start the PostgreSQL container:

```bash
docker-compose up -d
```

Apply migrations:

```bash
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

### 3. Set Up the Frontend

#### 3.1. Install Node.js Dependencies

Navigate to the frontend directory and install the necessary packages:

```bash
npm install
```

### 4. Environment Variables

Create `.env` files for both development and production:

#### Backend (.env)

```plaintext
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/yourdb
```

#### Frontend (.env.local)

```plaintext
NEXT_PUBLIC_HOST_URL=http://localhost:8000
```

For production, create a `.env.production` with the correct values.

### 5. Running the App

#### 5.1. Start the Backend

Ensure the virtual environment is activated, then:

```bash
python manage.py runserver
```

#### 5.2. Start the Frontend

In a separate terminal, run:

```bash
npm run dev
```

### 6. Building for Production

To build the frontend for production:

```bash
npm run build
npm run copy-assets
```

This will generate a production-ready version of the app.

### 7. Deploying

To deploy the app, ensure that both the backend and frontend are properly configured for production. You may use Docker, AWS, or any cloud provider for deployment.

### 8. Troubleshooting

If you encounter issues, check the following:

- Ensure Docker is running correctly.
- Verify environment variables are correctly set.
- Check that all dependencies are installed.

## License

This project is licensed under the MIT License.


