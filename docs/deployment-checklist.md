# Deployment Checklist

This checklist covers steps to deploy and verify `social-media-feed-backend`.

1. Add GitHub secrets

   - `CODECOV_TOKEN` (optional)
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `RENDER_API_KEY`
   - `RENDER_SERVICE_ID`
   - `SLACK_WEBHOOK` (optional)

2. Push changes to `main` to trigger CI

   - Confirm GitHub Actions → `CI Pipeline` completes successfully.

3. Verify Render deployment

   - For manual deploys, trigger via Render dashboard or let CD workflow call the Render API.
   - If needed, run migrations via Render Shell: `python manage.py migrate`.

4. Smoke tests

   - Health endpoint: `curl -i https://<your-service>.onrender.com/health/` → expect `200 OK`.
   - GraphQL: visit `https://<your-service>.onrender.com/graphql/` and run a simple query.

5. Monitoring & Logging

   - Verify Sentry is configured (SENTRY_DSN env) and check for events.
   - Verify performance warnings in logs (via the middleware added).

6. Load testing (optional)

   - Run Locust locally: `locust -f locustfile.py --host=http://localhost:8000`
   - Headless: `locust -f locustfile.py --host=https://your-app.onrender.com --headless -u 50 -r 10 --run-time 2m`

7. Finalize
   - Validate backups and database settings in Render.
   - Ensure secrets are rotated and documented.
