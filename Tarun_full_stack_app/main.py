# main.py
from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import Project, Client, Contact, Subscriber

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------------------- PUBLIC ROUTES (Landing) ---------------------- #

@app.get("/")
def landing(
    request: Request,
    db: Session = Depends(get_db),
    message: str | None = None,
    error: str | None = None
):
    projects = db.query(Project).all()
    clients = db.query(Client).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "projects": projects,
            "clients": clients,
            "message": message,
            "error": error,
        },
    )


@app.post("/contact")
def submit_contact(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    city: str = Form(...),
    db: Session = Depends(get_db),
):
    # Basic validation (server side)
    if not (full_name and email and mobile and city):
        url = app.url_path_for("landing") + "?error=Please+fill+all+fields"
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    contact = Contact(
        full_name=full_name,
        email=email,
        mobile=mobile,
        city=city,
    )
    db.add(contact)
    db.commit()
    url = app.url_path_for("landing") + "?message=Thank+you!+We+will+contact+you+soon."
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.post("/subscribe")
def subscribe(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    if not email:
        url = app.url_path_for("landing") + "?error=Please+enter+a+valid+email"
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    existing = db.query(Subscriber).filter(Subscriber.email == email).first()
    if existing:
        url = app.url_path_for("landing") + "?message=You+are+already+subscribed!"
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    sub = Subscriber(email=email)
    db.add(sub)
    db.commit()
    url = app.url_path_for("landing") + "?message=Subscribed+successfully!"
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


# ---------------------- ADMIN ROUTES ---------------------- #
# NOTE: No authentication here for simplicity (assignment usually doesn’t require).
# You can add auth with a simple login later if needed.

@app.get("/admin")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    total_clients = db.query(Client).count()
    total_contacts = db.query(Contact).count()
    total_subscribers = db.query(Subscriber).count()
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "total_projects": total_projects,
            "total_clients": total_clients,
            "total_contacts": total_contacts,
            "total_subscribers": total_subscribers,
        },
    )


# ---- Projects CRUD ---- #

@app.get("/admin/projects")
def admin_projects(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return templates.TemplateResponse(
        "admin_projects.html",
        {"request": request, "projects": projects},
    )


@app.get("/admin/projects/create")
def admin_project_create_form(request: Request):
    return templates.TemplateResponse(
        "admin_project_form.html", {"request": request, "project": None}
    )


@app.post("/admin/projects/create")
def admin_project_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    image_url: str = Form(""),
    db: Session = Depends(get_db),
):
    if not (name and description):
        url = app.url_path_for("admin_projects")
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    p = Project(name=name, description=description, image_url=image_url or None)
    db.add(p)
    db.commit()
    url = app.url_path_for("admin_projects")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/admin/projects/{project_id}/edit")
def admin_project_edit_form(
    request: Request, project_id: int, db: Session = Depends(get_db)
):
    project = db.query(Project).get(project_id)
    if not project:
        url = app.url_path_for("admin_projects")
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin_project_form.html",
        {"request": request, "project": project},
    )


@app.post("/admin/projects/{project_id}/edit")
def admin_project_edit(
    request: Request,
    project_id: int,
    name: str = Form(...),
    description: str = Form(...),
    image_url: str = Form(""),
    db: Session = Depends(get_db),
):
    project = db.query(Project).get(project_id)
    if not project:
        url = app.url_path_for("admin_projects")
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    project.name = name
    project.description = description
    project.image_url = image_url or None
    db.commit()
    url = app.url_path_for("admin_projects")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.post("/admin/projects/{project_id}/delete")
def admin_project_delete(
    request: Request, project_id: int, db: Session = Depends(get_db)
):
    project = db.query(Project).get(project_id)
    if project:
        db.delete(project)
        db.commit()
    url = app.url_path_for("admin_projects")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


# ---- Clients CRUD ---- #

@app.get("/admin/clients")
def admin_clients(request: Request, db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return templates.TemplateResponse(
        "admin_clients.html",
        {"request": request, "clients": clients},
    )


@app.get("/admin/clients/create")
def admin_client_create_form(request: Request):
    return templates.TemplateResponse(
        "admin_client_form.html",
        {"request": request, "client": None},
    )


@app.post("/admin/clients/create")
def admin_client_create(
    request: Request,
    name: str = Form(...),
    designation: str = Form(""),
    description: str = Form(""),
    image_url: str = Form(""),
    db: Session = Depends(get_db),
):
    if not name:
        url = app.url_path_for("admin_clients")
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    c = Client(
        name=name,
        designation=designation or None,
        description=description or None,
        image_url=image_url or None,
    )
    db.add(c)
    db.commit()
    url = app.url_path_for("admin_clients")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/admin/clients/{client_id}/edit")
def admin_client_edit_form(
    request: Request, client_id: int, db: Session = Depends(get_db)
):
    client = db.query(Client).get(client_id)
    if not client:
        url = app.url_path_for("admin_clients")
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin_client_form.html",
        {"request": request, "client": client},
    )


@app.post("/admin/clients/{client_id}/edit")
def admin_client_edit(
    request: Request,
    client_id: int,
    name: str = Form(...),
    designation: str = Form(""),
    description: str = Form(""),
    image_url: str = Form(""),
    db: Session = Depends(get_db),
):
    client = db.query(Client).get(client_id)
    if not client:
        url = app.url_path_for("admin_clients")
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    client.name = name
    client.designation = designation or None
    client.description = description or None
    client.image_url = image_url or None
    db.commit()
    url = app.url_path_for("admin_clients")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.post("/admin/clients/{client_id}/delete")
def admin_client_delete(
    request: Request, client_id: int, db: Session = Depends(get_db)
):
    client = db.query(Client).get(client_id)
    if client:
        db.delete(client)
        db.commit()
    url = app.url_path_for("admin_clients")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


# ---- View Contacts ---- #

@app.get("/admin/contacts")
def admin_contacts(request: Request, db: Session = Depends(get_db)):
    contacts = db.query(Contact).order_by(Contact.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin_contacts.html",
        {"request": request, "contacts": contacts},
    )


# ---- View Subscribers ---- #

@app.get("/admin/subscribers")
def admin_subscribers(request: Request, db: Session = Depends(get_db)):
    subscribers = db.query(Subscriber).order_by(Subscriber.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin_subscribers.html",
        {"request": request, "subscribers": subscribers},
    )
