import io
import os
import logging
from typing import Optional
from fastapi.templating import Jinja2Templates
from rdflib import Graph, Namespace, Literal, URIRef
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import FastAPI, Request, Form, Depends, Response, HTTPException, status

import database
import helper_methods

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

logging.getLogger().setLevel(logging.INFO)
templates = Jinja2Templates(directory="templates")

BASE_URI = "http://example.org/question-kg-linker/"
QKL = Namespace(BASE_URI)

# for setting up oauth for github
oauth = OAuth()
oauth.register(
    name="github",
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    client_kwargs={"scope": "user:email"},
)


async def get_current_user(request: Request):
    """Get the current user from the session."""
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.on_event("startup")
def on_startup():
    """Initialize the database."""
    database.init_db()


@app.get("/")
async def read_root(request: Request):
    """Homepage with submission forms."""
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login")
async def login(request: Request):
    """Check if user is already logged in if not show login page or redirect to GitHub OAuth."""
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/")

    # If github=true in query params, proceed with OAuth
    if request.query_params.get("github") == "true":
        redirect_uri = request.url_for("auth")
        return await oauth.github.authorize_redirect(
            request, redirect_uri, prompt="consent", approval_prompt="force"
        )

    # Otherwise show the login page
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/auth")
async def auth(request: Request):
    """Authenticate the user and redirect to home page."""
    try:
        token = await oauth.github.authorize_access_token(request)
        resp = await oauth.github.get("https://api.github.com/user", token=token)
        user = resp.json()

        emails_resp = await oauth.github.get(
            "https://api.github.com/user/emails", token=token
        )
        emails = emails_resp.json()

        # Find primary email
        primary_email = None
        for email in emails:
            if email.get("primary"):
                primary_email = email.get("email")
                break

        user["email"] = primary_email if primary_email else user["login"]
        request.session["user"] = user
        return RedirectResponse(url="/")
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        return {"error": str(e)}


@app.get("/logout")
async def logout(request: Request):
    """Log out the user and redirect to login page with a success message."""
    request.session.pop("user", None)
    return RedirectResponse(url="/login?logged_out=true")


@app.post("/submit_question")
async def submit_question(
    request: Request,
    kg_endpoint: str = Form(...),
    nl_question: str = Form(...),
    user: dict = Depends(get_current_user),
):
    """Handles submission of NL question + KG endpoint (SPARQL optional/later)."""
    try:

        if not helper_methods.check_sparql_endpoint(kg_endpoint):
            return JSONResponse(
                {"status": "error", "message": "Invalid SPARQL endpoint"},
                status_code=400,
            )

        database.insert_submission(
            kg_endpoint=kg_endpoint,
            nl_question=nl_question,
            email=user["email"],
            sparql_query=None,
        )
        return JSONResponse(
            {
                "status": "success",
                "message": "Natural language question submitted successfully",
            }
        )
    except Exception as e:
        logging.info(f"Error submitting question: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.post("/submit_query")
async def submit_query(
    request: Request,
    kg_endpoint: str = Form(...),
    nl_question: str = Form(...),
    sparql_query: str = Form(...),
    user: dict = Depends(get_current_user),
):
    """Handles submission of NL question + SPARQL query + KG endpoint."""
    try:

        if not helper_methods.check_sparql_endpoint(kg_endpoint):
            return JSONResponse(
                {"status": "error", "message": "Invalid SPARQL endpoint"},
                status_code=500,
            )
        if not helper_methods.validate_sparql_query(sparql_query):
            return JSONResponse(
                {"status": "error", "message": "Invalid SPARQL query"}, status_code=500
            )

        database.insert_submission(
            kg_endpoint=kg_endpoint,
            nl_question=nl_question,
            email=user["email"],
            sparql_query=sparql_query,
        )
        return JSONResponse(
            {"status": "success", "message": "SPARQL query submitted successfully"}
        )
    except Exception as e:
        logging.info(f"Error submitting query: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.get("/list")
async def list_kglite_endpoints(
    request: Request, user: dict = Depends(get_current_user)
):
    """Lists unique KG endpoints with submissions."""
    kg_endpoints = database.get_unique_kg_endpoints()
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": user, "kg_endpoints": kg_endpoints}
    )


@app.get("/list/{kg_endpoint:path}")
async def list_submissions_for_kg(
    request: Request, kg_endpoint: str, user: dict = Depends(get_current_user)
):
    """Lists all submissions for a specific KG endpoint."""
    submissions = database.get_submissions_by_kg(kg_endpoint)
    return templates.TemplateResponse(
        "submissions.html",
        {
            "request": request,
            "user": user,
            "submissions": submissions,
            "endpoint": kg_endpoint,
        },
    )


@app.get("/export", include_in_schema=False)
async def export_submissions_rdf(
    request: Request, user: dict = Depends(get_current_user)
):
    """Exports all submissions as RDF (Turtle format)."""
    all_submissions = database.get_all_submissions()

    # create the content of the rdf file in a specified format
    # reference: https://github.com/sib-swiss/sparql-examples
    rdf_content = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <http://schema.org/> .
@prefix qkl: <http://example.org/question-kg-linker/> .
"""

    for sub in all_submissions:
        submission_id = sub["id"]
        comment = (
            "SPARQL - Natural language question pair"
            if sub["sparql_query"]
            else "Natural Language Question"
        )

        rdf_content += f"""qkl:{submission_id} .
\ta sh:SPARQLExecutable, sh:SPARQLSelectExecutable ;
\trdfs:comment "{comment}" ;
\tsh:prefixes _:sparql_examples_prefixes ;
"""

        if sub["sparql_query"]:
            rdf_content += f'\tsh:select """{helper_methods.escape_string(sub["sparql_query"])}""" ;\n'

        rdf_content += f'\tschema:target <{sub["kg_endpoint"]}> ;\n'
        rdf_content += (
            f'\tqkl:nlQuestion "{helper_methods.escape_string(sub["nl_question"])}" ;\n'
        )
        rdf_content += ".\n\n"

    return Response(content=rdf_content.encode("utf-8"), media_type="text/turtle")
