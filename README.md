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

#### 2.4. Install Ollama

Ollama is required for LLM processing. Follow the instructions on the [Ollama website](https://ollama.com/) to install it on your system.

Once installed, you can run the Ollama server on the desired port (e.g., 11450):

```bash
ollama serve
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

### 6. Building for Use

To build the frontend:

```bash
npm run build
npm run copy-assets
```

This will generate a production-ready version of the app, and copy to Django Static content for serving

### 7. Deploying with Ngrok

To deploy the app for external access using Ngrok, follow these steps:

#### 7.1. Install Ngrok

If you haven't already installed Ngrok, you can do so by following the instructions on the [Ngrok website](https://ngrok.com/download).

#### 7.2. Start the Backend

Ensure that your backend is running locally using Docker:

```bash
docker-compose up --build
```

This will start the Django server and PostgreSQL database on `http://localhost:8000`.

#### 7.3. Start Ngrok

In a separate terminal, run Ngrok to expose your local server to the internet:

```bash
ngrok http 8000
```

Ngrok will provide a public URL (e.g., `https://abcd1234.ngrok.io`) that forwards requests to your local Django server running on `http://localhost:8000`.

#### 7.4. Update Frontend Configuration

In your `.env.local` file for the frontend, update the `NEXT_PUBLIC_HOST_URL` to point to the Ngrok URL:

```plaintext
NEXT_PUBLIC_HOST_URL=https://abcd1234.ngrok.io
```

Replace `https://abcd1234.ngrok.io` with the actual URL provided by Ngrok.

### 8. Troubleshooting

If you encounter issues, check the following:

- Ensure Docker is running correctly.
- Verify environment variables are correctly set.
- Check that all dependencies are installed.

## License

This project is licensed under the MIT License.
