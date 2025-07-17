import io
import os
import logging
import requests
from typing import Optional
from fastapi.templating import Jinja2Templates
from rdflib import Graph, Namespace, Literal, URIRef
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import FastAPI, Request, Form, Depends, Response, HTTPException, status
from datetime import datetime

import database
import data_models
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

# for setting up oauth for orcid
oauth.register(
    name="orcid",
    client_id=os.getenv("ORCID_CLIENT_ID"),
    client_secret=os.getenv("ORCID_CLIENT_SECRET"),
    authorize_url="https://orcid.org/oauth/authorize",
    access_token_url="https://orcid.org/oauth/token",
    client_kwargs={"scope": "/authenticate"},
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
    kg_metadata = database.get_all_kg_metadata()
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": user, "kg_metadata": kg_metadata}
    )


@app.get("/login")
async def login(request: Request):
    """Check if user is already logged in if not show login page or redirect to GitHub OAuth."""
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/")

    # If github=true in query params, proceed with OAuth
    if request.query_params.get("github") == "true":
        redirect_uri = request.url_for("auth_github")
        return await oauth.github.authorize_redirect(
            request, redirect_uri, prompt="consent", approval_prompt="force"
        )

    if request.query_params.get("orcid") == "true":
        redirect_uri = request.url_for("auth_orcid")
        return await oauth.orcid.authorize_redirect(request, redirect_uri)

    # Otherwise show the login page
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/auth/github")
async def auth_github(request: Request):
    """Authenticate the user and redirect to home page."""
    try:
        token = await oauth.github.authorize_access_token(request)
        resp = await oauth.github.get("https://api.github.com/user", token=token)
        user = resp.json()

        emails_resp = await oauth.github.get(
            "https://api.github.com/user/emails", token=token
        )
        emails = emails_resp.json()

        primary_email = None
        for email in emails:
            if email.get("primary"):
                primary_email = email.get("email")
                break

        user["email"] = primary_email if primary_email else user["login"]
        request.session["type"] = "github"
        request.session["user"] = user

        return RedirectResponse(url="/")
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        return {"error": str(e)}


@app.get("/auth/orcid")
async def auth_orcid(request: Request):
    try:
        token = await oauth.orcid.authorize_access_token(request)
        orcid_id = token.get("orcid")
        access_token = token.get("access_token")
        name = token.get("name")

        email = None
        if orcid_id:
            try:
                response = requests.get(
                    f"https://pub.orcid.org/v3.0/{orcid_id}/email",
                    headers={"Accept": "application/json"},
                )

                if response.status_code == 200:
                    email_data = response.json()
                    emails = email_data.get("email", [])

                    for email_entry in emails:
                        if email_entry.get("visibility") == "public":
                            email = email_entry.get("email")
                            break

            except Exception as e:
                logging.error(f"Error fetching ORCID email: {e}")

        request.session["type"] = "orcid"
        request.session["email"] = email if email else orcid_id

        request.session["user"] = {
            "orcid_id": orcid_id,
            "login": email if email else name,
            "email": email if email else orcid_id,
        }
        request.session["type"] = "orcid"
        request.session["user"][
            "avatar_url"
        ] = f'https://ui-avatars.com/api/?name={request.session["user"]["login"]}&background=0D8ABC&color=fff&rounded=true'

        return RedirectResponse(url="/")
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        return {"error": str(e)}


@app.get("/logout")
async def logout(request: Request):
    """Log out the user and redirect to login page with a success message."""
    request.session.pop("user", None)
    return RedirectResponse(url="/login?logged_out=true")


@app.post("/submit_query")
async def submit_query(
    request: Request,
    kg_endpoint: str = Form(...),
    nl_question: str = Form(...),
    sparql_query: str = Form(None),  # Made optional
    kg_name: str = Form(None),
    kg_description: str = Form(None),
    user: dict = Depends(get_current_user),
):
    """Handles submission of NL question + optional SPARQL query + KG endpoint."""
    try:
        if not helper_methods.check_sparql_endpoint(kg_endpoint):
            return JSONResponse(
                {"status": "error", "message": "Invalid SPARQL endpoint"},
                status_code=400,
            )

        # Only validate SPARQL query if it's provided
        if sparql_query and sparql_query.strip():
            if not helper_methods.validate_sparql_query(sparql_query):
                return JSONResponse(
                    {"status": "error", "message": "Invalid SPARQL query"},
                    status_code=400,
                )

        if not database.get_if_endpoint_exists(kg_endpoint):
            database.insert_kg_endpoint(kg_name, kg_description, kg_endpoint)

        database.insert_submission(
            kg_endpoint=kg_endpoint,
            nl_question=nl_question,
            email=user["email"],
            sparql_query=(
                sparql_query if sparql_query and sparql_query.strip() else None
            ),
        )

        # Return appropriate message based on whether SPARQL was provided
        if sparql_query and sparql_query.strip():
            message = "Question and SPARQL query submitted successfully"
        else:
            message = "Question submitted successfully."

        return JSONResponse({"status": "success", "message": message})
    except Exception as e:
        logging.info(f"Error submitting query: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.get("/trigger_modification", include_in_schema=False)
async def trigger_modification(
    request: Request,
    id_submission: str,
    user: dict = Depends(get_current_user),
):
    """Triggers the modification of a submission."""
    try:
        submission = database.get_submission(id_submission)
        logging.info(f"Submission: {submission}")
        return templates.TemplateResponse(
            "modify_form.html",
            {"request": request, "submission": submission, "user": user},
        )
    except Exception as e:
        logging.info(f"Error modifying submission: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.post("/modify_db_submission", include_in_schema=False)
async def modify_db_submission(
    request: Request,
    id_submission: str = Form(...),
    kg_endpoint: str = Form(...),
    nl_question: Optional[str] = Form(None),
    updated_sparql_query: Optional[str] = Form(None),
    user: dict = Depends(get_current_user),
):
    """Handles modification of a submission."""
    try:
        if updated_sparql_query:
            if not helper_methods.validate_sparql_query(updated_sparql_query):
                return JSONResponse(
                    {"status": "error", "message": "Invalid SPARQL query"},
                    status_code=500,
                )
        database.modify_submission(
            kg_endpoint, id_submission, user["email"], nl_question, updated_sparql_query
        )
        return JSONResponse(
            {
                "status": "success",
                "message": "Submission for SPARQL query modified successfully",
            }
        )
    except Exception as e:
        logging.info(f"Error modifying submission: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.get("/list")
async def list_kglite_endpoints(
    request: Request, user: dict = Depends(get_current_user)
):
    """Lists unique KG endpoints with submissions."""
    kg_endpoints = database.get_unique_kg_endpoints()
    kg_metadata = database.get_all_kg_metadata()

    for endpoint_data in kg_metadata:
        endpoint = endpoint_data["endpoint"]
        submissions = database.get_submissions_by_kg(endpoint)

        total_submissions = len(submissions)
        query_pairs = sum(
            1
            for sub in submissions
            if sub.get("sparql_query") and sub.get("sparql_query").strip()
        )
        questions_only = total_submissions - query_pairs

        endpoint_data["total_submissions"] = total_submissions
        endpoint_data["query_pairs"] = query_pairs
        endpoint_data["questions_only"] = questions_only

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "kg_endpoints": kg_endpoints,
            "kg_metadata": kg_metadata,
        },
    )


@app.get("/list/{kg_endpoint:path}")
async def list_submissions_for_kg(
    request: Request, kg_endpoint: str, user: dict = Depends(get_current_user)
):
    """Lists all submissions for a specific KG endpoint."""
    submissions = database.get_submissions_by_kg(kg_endpoint)
    kg_metadata = database.get_all_kg_metadata(for_one=True, endpoint=kg_endpoint)
    return templates.TemplateResponse(
        "submissions.html",
        {
            "request": request,
            "user": user,
            "submissions": submissions,
            "endpoint": kg_endpoint,
            "kg_name": kg_metadata["name"],
            "kg_description": kg_metadata["description"],
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


@app.get("/home")
async def home_page(request: Request):
    """Home page with statistics about the crowdsourcing project."""
    try:
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")

        # Get statistics from database
        all_submissions = database.get_all_submissions()

        # Calculate statistics
        n_queries = sum(
            1
            for sub in all_submissions
            if sub.get("sparql_query") and sub.get("sparql_query").strip()
        )
        n_questions = len(all_submissions) - n_queries
        n_contributors = len(
            set(
                sub.get("username", "")
                for sub in all_submissions
                if sub.get("username")
            )
        )
        n_kgs = len(database.get_unique_kg_endpoints())

        return templates.TemplateResponse(
            "home.html",
            {
                "request": request,
                "current_date": current_date,
                "n_queries": n_queries,
                "n_questions": n_questions,
                "n_contributors": n_contributors,
                "n_kgs": n_kgs,
            },
        )
    except Exception as e:
        logging.error(f"Error loading home page: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
