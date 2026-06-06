# 🎬 Mvs-Movie | Retro Cinema Streaming Platform

[![Live Demo](https://img.shields.io/badge/▶_Live_Demo-mvs--movie.site-10b981?style=for-the-badge&logoColor=white)](https://mvs-movie.site)

A nostalgic video streaming service styled after early-2000s web cinemas, dedicated to classic and public-domain films. Behind the retro aesthetic sits a modern Django backend with time-restricted free tiers, Stripe subscriptions, asynchronous task processing, and persistent user state.

![Django](https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-A30000?style=flat-square&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-635BFF?style=flat-square&logo=stripe&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Caddy](https://img.shields.io/badge/Caddy-1F88C0?style=flat-square&logo=caddy&logoColor=white)

> [!NOTE]
> Demo / portfolio project. Stripe runs in test mode.

---

## 🚀 Key Features

* **2000s Cinema Aesthetic:** Authentic retro UI/UX for browsing and streaming timeless classics.
* **Time-Limited Free Tier:** Tracking system granting users 1 hour of free streaming per 24-hour cycle.
* **Premium Subscriptions:** Stripe integration (subscriptions, webhooks, secure checkout) to unlock unlimited streaming.
* **"Resume Watching" State:** User-state tracking to continue playback exactly where the user left off.
* **Asynchronous Processing:** Celery + Celery Beat handle scheduled jobs — email confirmation, subscription lifecycle, and periodic limit resets.
* **Secure Authentication:** Custom user model with mandatory email verification.

---

## 🛠️ Tech Stack

* **Backend:** Django / Django REST Framework
* **Database:** PostgreSQL
* **Cache / Broker:** Redis
* **Async:** Celery (worker + beat scheduler)
* **Payments:** Stripe API (subscription billing, webhooks)
* **Static Files:** WhiteNoise
* **Web Server:** Gunicorn (WSGI)
* **Reverse Proxy:** Caddy (automatic SSL/HTTPS)
* **Containerization:** Docker & Docker Compose

---

## 🏗️ Architecture

Multi-container environment managed by **Docker Compose**:

* `web` — Django application: streaming endpoints, authentication, and time-tracking logic (Gunicorn).
* `db` — PostgreSQL with a persistent volume (users, subscriptions, streaming metrics, video metadata).
* `redis` — Redis, used as Celery broker / result backend.
* `celery` — Celery worker processing asynchronous tasks (emails, payment events, subscription updates).
* `celery-beat` — Celery Beat scheduler running periodic jobs (limit resets, cleanup, recurring checks).

A shared **Caddy** container (separate compose project) is the single entry point on ports 80/443, serving `/media` directly from a volume, proxying everything else to Django, and handling SSL certificates automatically.