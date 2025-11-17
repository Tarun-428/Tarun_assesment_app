# Tarun_assesment_app
A simple full-stack portfolio website built with **Flask**, **Python**, **PostgreSQL**, and **HTML/CSS**.

This v1 includes:

- Public landing page
- Dynamic projects & clients (from the database)
- Contact form (stored in DB)
- Newsletter subscription (stored in DB, duplicate-safe)
- Admin project creation with **image upload**
- Admin client add with **image upload**

---

## 🧱 Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** PostgreSQL
- **Frontend:** HTML5, CSS3 (Poppins font, basic responsive layout)
- **Server-side Templating:** Jinja2 (Flask default)

---


### Public Site

- **Landing page** 
- **Projects section**
  - Data fetched from PostgreSQL table `projects`
  - Each project has name, description, and a thumbnail image
- **Clients section**
  - Data fetched from PostgreSQL table `clients`
  - Each client has name, feedback, and avatar URL
- **Contact form**
  - Stores user name, email, mobile, and city into `contacts` table
- **Newsletter subscription**
  - Stores unique email addresses into `subscribers` table
  - Prevents duplicate subscriptions
