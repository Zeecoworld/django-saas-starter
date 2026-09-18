# Django SaaS Starter

A production-ready foundation for a subscription SaaS product: email-based auth,
multi-tenant organizations with team roles, Stripe billing, a JSON API, and
background jobs — all wired together so you can focus on your product instead
of rebuilding plumbing everyone needs.

## What's included

- **Auth** — email/password signup & login via `django-allauth` (no usernames), email verification, password reset
- **Teams** — every account belongs to one or more `Organizations`, with Owner/Admin/Member roles and email invitations
- **Billing** — Stripe Checkout, the Stripe Customer Portal, and a webhook handler that keeps subscription status in sync automatically
- **API** — a Django REST Framework scaffold at `/api/v1/` (token + session auth) for a future mobile app or integrations
- **Background jobs** — Celery + Redis, ready for sending emails, syncing billing, etc.
- **Admin** — the full Django admin, so you can manage users, orgs, and plans without writing an internal tool
- **Deployment** — Dockerized (web, worker, beat, Postgres, Redis), GitHub Actions CI, Whitenoise for static files, S3-ready for media

This is deliberately **not** a framework with magic — it's plain Django you can read
top to bottom in an afternoon. Everything lives in `apps/`.

---

## Option A: I'm not a developer — deploy this without touching code

You can get a live, working app online in about 15 minutes using [Render](https://render.com)
(a hosting service with a generous free tier), with no local setup required.

1. Click **Use this template** at the top of this GitHub repo (or fork it) into your own GitHub account.
2. Go to [render.com](https://render.com) and sign up, then choose **New > Blueprint**.
3. Point it at your forked repo — Render reads the included `render.yaml` automatically and creates the web service, Postgres database, and Redis instance for you.
4. Render will ask for a few environment variables (it lists them from `.env.example`) — at minimum set `SECRET_KEY` (any long random string) and your Stripe keys once you're ready to take payments. You can leave Stripe values blank to start; billing pages just won't work until you add them.
5. Click **Apply**. Render builds and deploys the app — you'll get a live URL like `your-app.onrender.com`.
6. Once it's live, open `your-app.onrender.com/admin/` and log in with the superuser Render created (see the deploy logs, or run the "Create superuser" job from the Render dashboard's Shell tab).

From there, everything — creating pricing plans, managing users, checking subscriptions — happens through the Django admin at `/admin/`, no code required.

To connect real payments later: create a [Stripe](https://stripe.com) account, copy your API keys and webhook secret into Render's environment variables, and add your price IDs to a Plan in the admin (see "Setting up Stripe" below).

---

## Option B: I'm a developer — run it locally

### Prerequisites
Docker and Docker Compose. That's it — everything else (Python, Postgres, Redis) runs inside containers.

### Quick start

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
cp .env.example .env          # then open .env and set SECRET_KEY at minimum
make build
make up                       # starts web, worker, beat, db, redis
```

In a second terminal:

```bash
make migrate
make superuser                # create your admin login
make seed                     # creates two example Plans (edit their Stripe price IDs before going live)
```

Visit **http://localhost:8000** — the app is running. Visit **http://localhost:8000/admin/** to manage everything.

Common commands (see `Makefile` for the full list):

```bash
make logs         # tail the web container's logs
make test          # run the test suite
make lint          # ruff check
make shell         # Django shell inside the container
```

### Running without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env   # point DATABASE_URL / REDIS_URL at local services, or install Postgres+Redis locally
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Celery tasks run **synchronously** in the `development` settings (`CELERY_TASK_ALWAYS_EAGER = True`), so you don't need a worker running just to click around locally.

---

## Setting up Stripe (real payments)

1. Create a [Stripe](https://dashboard.stripe.com/register) account.
2. In the Stripe dashboard, create one or more **Products** with recurring **Prices** (e.g. "Pro — $49/month").
3. Copy each Price's ID (`price_...`) and set it on a `Plan` in the Django admin (**Billing → Plans**), or edit `apps/billing/management/commands/seed_plans.py` and re-run `make seed`.
4. Copy your **Publishable key** and **Secret key** from the Stripe dashboard into `.env` as `STRIPE_PUBLIC_KEY` / `STRIPE_SECRET_KEY`.
5. Add a webhook endpoint in Stripe pointing to `https://yourdomain.com/billing/webhook/`, subscribed to at least:
   `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`.
   Copy the webhook's **signing secret** into `.env` as `STRIPE_WEBHOOK_SECRET`.
6. Test locally with the [Stripe CLI](https://stripe.com/docs/stripe-cli):
   `stripe listen --forward-to localhost:8000/billing/webhook/`

The whole billing flow (checkout → webhook → subscription status) is in `apps/billing/`.

---

## Project structure

```
config/               # settings, root urls, celery app, wsgi/asgi
apps/
  users/               # custom email-based User model
  organizations/       # Organization, Membership (roles), Invitation, "current org" middleware
  billing/              # Plan, Subscription, Stripe checkout/portal/webhooks
  core/                 # landing page, dashboard
  api/                  # DRF v1 API
templates/             # server-rendered HTML (Tailwind via CDN — no build step needed)
tests/                 # pytest + factory_boy
```

## Customizing

- **Rename the product**: set `SITE_NAME` in `.env` and swap the color in `templates/base.html`.
- **Add a field to organizations/users**: edit the model, then `make makemigrations && make migrate`.
- **Change pricing tiers**: edit them in the Django admin — no deploy needed.
- **Add an API endpoint**: add a serializer + viewset in `apps/api/v1/`, register it on the router.
- **Swap Tailwind CDN for a real build**: the CDN script in `base.html` is fine for getting started; swap in `django-tailwind` or a Vite setup once you need custom design tokens.

## Security notes before going live

- Generate a real `SECRET_KEY` (never reuse the example one) — `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- Set `DEBUG=False` and a real `ALLOWED_HOSTS` in production
- `config/settings/production.py` already enables HSTS, secure cookies, and SSL redirect
- Set `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` (it's relaxed to `"optional"` in `development.py` only)

## License

MIT — do whatever you want with it. See `LICENSE`.
