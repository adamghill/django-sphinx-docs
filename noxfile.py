import nox


@nox.session(python=["3.10", "3.11", "3.12", "3.13"])
def tests(session):
    session.install("django", "pytest", "pytest-django")
    session.install(".")
    session.run("pytest")


@nox.session
def lint(session):
    session.install("ruff")
    session.run("ruff", "check", ".")


@nox.session
def type_check(session):
    session.install("ty", "django-stubs")
    session.run("ty")
