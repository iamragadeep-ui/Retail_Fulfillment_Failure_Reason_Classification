# Deployment Notes

## Frontend

The frontend is designed to be Vercel-ready. Configure the environment variable `NEXT_PUBLIC_API_URL` to the backend URL, then deploy the `frontend` directory as a Next.js app.

## Backend

The backend is cloud-neutral and can be deployed to a Python app platform or container runtime. Set `DATABASE_URL`, `REDIS_URL`, and `OPENAI_API_KEY` environment variables before deployment.

## Docker

Use the included `docker-compose.yml` for local and demonstration environments.
