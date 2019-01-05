# coding=utf-8
# Copyright (C) 2018 Janusz Skonieczny
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import os
import shutil
import sys
import webbrowser
from collections import OrderedDict
from itertools import chain
from pathlib import Path

# noinspection PyPackageRequirements
from urllib.request import pathname2url

from invoke import call, task

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# logging.getLogger().setLevel(logging.INFO)
# logging.disable(logging.NOTSET)
logging.debug('Loading %s', __name__)
log = logging.getLogger(__name__)

is_win = sys.platform == 'win32'
ROOT_DIR = Path(__file__).parent.absolute()
PROJ_TMP_DIR = ROOT_DIR / '.tmp'
FIXTURES = ROOT_DIR / 'fixtures' / 'fixtures_config.yml'


def get_current_version():
    from configparser import ConfigParser
    cfg = ConfigParser()
    cfg.read(str(Path(ROOT_DIR) / 'setup.cfg'))
    current_version = cfg.get('bumpversion', 'current_version')
    return current_version


# noinspection PyUnusedLocal
@task
def version(ctx):
    print("Version: " + get_current_version())


@task
def clean(ctx):
    """Remote temporary files"""
    for item in chain(Path(ROOT_DIR).rglob("*.pyc"), Path(ROOT_DIR).rglob("*.pyo")):
        logging.debug("Deleting: %s", item)
        item.unlink()

    log.info("Removing __pycache__ in sys.path folders")
    for folder in sys.path:
        for item in Path(folder).rglob("__pycache__"):
            logging.debug("Deleting: %s", item)
            shutil.rmtree(str(item), ignore_errors=True)

    folders = (
        ROOT_DIR / 'build',
        ROOT_DIR / 'example_project' / '.eggs',
        ROOT_DIR / '.eggs',
        ROOT_DIR / '.tox',
        ROOT_DIR / '.coverage',
        ROOT_DIR / '.htmlcov',
        ROOT_DIR / '.pytest_cache',
        ROOT_DIR / '.cache',
        PROJ_TMP_DIR,
    )

    for folder in folders:
        print("Removing folder {}".format(folder))
        shutil.rmtree(str(folder), ignore_errors=True)

    ctx.run('git checkout -- .tmp')


@task
def check(ctx):
    """Check project codebase cleanness"""
    ctx.run("flake8 src tests setup.py manage.py")
    ctx.run("isort --check-only --diff --recursive src tests setup.py")
    ctx.run("python setup.py check --strict --metadata --restructuredtext")
    ctx.run("check-manifest  --ignore .idea,.idea/* .")
    ctx.run("pytest --cov=src --cov=tests --cov-fail-under=5 -n auto --html="+str(PROJ_TMP_DIR / 'pytest.html'))


@task
def coverage(ctx):
    ctx.run("pytest --cov=src --cov=tests --cov-fail-under=5 --cov-report html")
    webbrowser.open("file://" + pathname2url(str(ROOT_DIR / '.tmp' / 'coverage' / 'index.html')))


@task
def isort(ctx):
    """Check project codebase cleanness"""
    ctx.run("isort --recursive src tests setup.py")


@task
def detox(ctx):
    """Run detox with a subset of envs and report run separately"""
    envs = ctx.run("tox -l").stdout.splitlines()
    envs.remove('clean')
    envs.remove('report')
    envs = [e for e in envs if not e.startswith('py2')]
    log.info("Detox a subset of environments: %s", envs)
    ctx.run("tox -e clean")
    ctx.run("detox --skip-missing-interpreters -e " + ",".join(envs))
    ctx.run("tox -e report")


@task
def register_pypi(ctx):
    """Register project on PyPi"""
    ctx.run("git checkout master")
    ctx.run("python setup.py register -r pypi")


@task
def register_pypi_test(ctx):
    """Register project on TEST PyPi"""
    ctx.run("git checkout master")
    ctx.run("python setup.py register -r pypitest")


@task
def upload_pypi(ctx):
    """Upload to PyPi"""
    ctx.run("python setup.py sdist upload -r pypi")
    ctx.run("python setup.py bdist_wheel upload -r pypi")


@task(clean)
def dist(ctx):
    """Build setuptools dist package"""
    ctx.run("python setup.py sdist")
    ctx.run("python setup.py bdist_wheel")
    ctx.run("ls -l dist")


@task(clean)
def install(ctx):
    """Install setuptools dist package"""
    ctx.run("python setup.py install")


@task
def sync(ctx):
    """Sync master and develop branches in both directions"""
    ctx.run("git checkout develop")
    ctx.run("git pull origin develop --verbose")

    ctx.run("git checkout master")
    ctx.run("git pull origin master --verbose")

    ctx.run("git checkout develop")
    ctx.run("git merge master --verbose")

    ctx.run("git checkout develop")


@task(sync)
def sync_master(ctx):
    ctx.run("git checkout master")
    ctx.run("git merge develop --verbose")

    ctx.run("git checkout develop")
    ctx.run("git merge master --verbose")

    ctx.run("git push origin develop --verbose")
    ctx.run("git push origin master --verbose")
    ctx.run("git push --follow-tags")


@task()
def bump(ctx):
    """Increment version number"""
    # ctx.run("bumpversion patch --no-tag")
    ctx.run("bumpversion patch")


@task()
def pip_compile(ctx):
    """Upgrade frozen requirements to the latest version"""
    ctx.run('pip-compile requirements/production.txt -o requirements/lock/production.txt --verbose --upgrade')
    ctx.run('sort requirements/lock/production.txt -o requirements/lock/production.txt')
    ctx.run('git add requirements/lock/*.txt')
    if ctx.run('git diff-index --quiet HEAD', warn=True).exited != 0:
        ctx.run('git commit -m "Requirements compiled by pip-compile" --allow-empty')


@task()
def pipenv(ctx):
    """Upgrade frozen requirements to the latest version"""
    ctx.run('pipenv install -r requirements/production.txt')
    ctx.run('pipenv install --dev -r requirements/development.txt')
    ctx.run('pipenv lock --requirements > requirements/lock/production.txt')
    ctx.run('pipenv lock --requirements --dev | grep -v "/multiinfo-python" -- > requirements/lock/development.txt')
    ctx.run('pipenv graph --reverse -- > requirements/lock/graph.txt')
    ctx.run('sort requirements/lock/production.txt -o requirements/lock/production.txt')
    ctx.run('sort requirements/lock/development.txt -o requirements/lock/development.txt')
    ctx.run('git add Pipfile Pipfile.lock requirements/lock/*.txt')
    ctx.run('git commit -m "Requirements locked by pipenv"')


@task
def assets(ctx):
    """
    Collect and build website assets
    """
    # ctx.run("gulp")
    ctx.run("python manage.py collectstatic --noinput")  # in some cases assets build requires static to be updated
    ctx.run("python manage.py assets build")
    ctx.run("python manage.py collectstatic --noinput")  # update static with compressed assets
    ctx.run("git add --all static assets", warn=True)
    ctx.run('git commit -m "Build assets"', warn=True)


# noinspection PyUnusedLocal
@task(check, sync, detox)
def release_start(ctx):
    """Start a release cycle with publishing a release branch"""
    ctx.run("git flow release start v{}-release".format(get_current_version()))
    ctx.run("git merge master --verbose")
    ctx.run("bumpversion patch --no-tag --verbose ")
    ctx.run("git flow release --verbose publish")


# noinspection PyUnusedLocal
@task(check, sync, detox, post=[])
def release_finish(ctx):
    """Finish a release cycle with publishing a release branch"""
    ctx.run("git flow release finish --fetch --push")


# noinspection PyUnusedLocal
@task(isort, check, pip_compile, sync, detox, bump, sync_master)
def release(ctx):
    """Build new package version release and sync repo"""


# noinspection PyUnusedLocal
@task(release, post=[upload_pypi])
def publish(ctx):
    """Merge develop, create and upload new version"""
    ctx.run("git checkout master")
    ctx.run("git merge develop --verbose")


@task
def locales_django(ctx):
    """
    Collect and compile translation strings
    """
    # https://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-makemessages
    ctx.run('python manage.py makemessages -v 3 --no-wrap --ignore ".*" --locale=pl_PL')
    ctx.run('python manage.py compilemessages -v 3  --locale pl_PL')


@task
def locales_babel(ctx):
    """
    Collect and compile translation strings
    """
    # https://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-makemessages
    # http://babel.edgewall.org/wiki/BabelDjango
    pybabel = str('pybabel')
    ctx.run(pybabel + " extract -F locale/babel.cfg -o locale/django.pot --no-wrap --sort-output .")
    # create locales firs
    # pybabel init -D django -i locale/django.pot -d locale -l es
    # http://babel.edgewall.org/wiki/BabelDjango#CreatingandUpdatingTranslationsCatalogs
    # ctx.run(pybabel + " update -D django -i locale/django.pot -d locale --ignore-obsolete")
    ctx.run(pybabel + " update -D django -i locale/django.pot -d locale --previous --no-wrap")
    ctx.run(pybabel + " compile -D django -d locale --statistics")
    log.info("JavaScript locales")
    # ctx.run(pybabel + " update -D djangojs -i locale/djangojs.pot -d locale --previous --no-wrap")
    ctx.run("django-admin makemessages -d djangojs -i static -i node_modules")
    ctx.run(pybabel + " compile -D djangojs -d locale --statistics")


# noinspection PyUnusedLocal
@task(post=[locales_django])
def locales(ctx):
    """
    Collect and compile translation strings
    """
    tmp = ROOT_DIR / ".tmp"
    if not tmp.exists():
        os.makedirs(str(tmp))
    locale = ROOT_DIR / "src" / "locale"
    if not locale.exists():
        os.makedirs(str(locale))


@task
def trigger_tests(ctx):
    """Trigger test cycle"""
    print(" #### Signaling test repo")
    ingeration_testing_root = str(Path(ROOT_DIR).parent / "integration-testing")
    print(ingeration_testing_root)
    env = {
        'GIT_WORK_TREE': ingeration_testing_root,
        'GIT_DIR': str(Path(ingeration_testing_root) / '.git'),
    }
    current_version = get_current_version()
    ctx.run("git checkout develop", env=env)
    cmd = 'git commit --allow-empty -m "Test release {}"'.format(current_version)
    print(cmd)
    ctx.run(cmd, env=env)
    ctx.run("git push origin develop", env=env)


@task(iterable=['remote'], help={'remote': "Git remote used to ship local repository"})
def ship(ctx, remote='dev', branch='master'):
    """
    Ship current version to a remote environment
    """
    ctx.run("git checkout {branch}".format(branch=branch))
    ctx.run("git push {remote} {branch}  --verbose".format(remote=remote, branch=branch))
    ctx.run("git checkout develop")
    # Uncomment this to show release script output
    ctx.run("heroku logs -r {remote}".format(remote=remote))


# noinspection PyUnusedLocal
@task(pre=[isort, pip_compile, sync, bump, sync_master, ship], post=[])
def yolo(ctx):
    """
    A dirty no test deploy
    """


# noinspection PyUnusedLocal
@task(pre=[assets, release, ship], post=[])
def deploy(ctx):
    """
    Collect and compile assets, add, commit and push to remote
    """


# noinspection PyUnusedLocal
@task(pre=[assets, release, call(ship, remote='production', branch='master')])
def deploy_production(ctx):
    """Deploy to production remote"""
    pass


# noinspection PyUnusedLocal
@task(pre=[assets, release, call(ship, remote='staging', branch='master')])
def deploy_staging(ctx):
    """Deploy to staging remote"""
    pass


@task
def vagrant(ctx):
    """
    Collect and compile assets, add, commit and push to production remote
    """
    ctx.run("git checkout develop")
    ctx.run("git push vagrant develop --verbose")



@task
def dump(ctx):
    """Dump django fixtures with initial and test data"""

    with FIXTURES.open() as f:
        import yaml
        fixtures = yaml.load(f)

    for file, what in fixtures.items():
        log.info("Dumping fixture: %s" % file)
        cmd = "python manage.py dumpdata --format=json --indent 2 --natural-foreign --natural-primary {} > " + str(ROOT_DIR / 'fixtures' / '{}.json')
        cmd = cmd.format(" ".join(what), file)
        log.debug(cmd)
        ctx.run(cmd)

@task
def load_fixtures(ctx):
    """Load initial and test data fixtures"""
    import yaml

    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

    def dict_representer(dumper, data):
        return dumper.represent_dict(data.iteritems())

    def dict_constructor(loader, node):
        return OrderedDict(loader.construct_pairs(node))

    yaml.add_representer(OrderedDict, dict_representer)
    yaml.add_constructor(_mapping_tag, dict_constructor)

    with FIXTURES.open() as f:
        fixtures = yaml.load(f)

    for fixture in fixtures.keys():
        fixture = str(ROOT_DIR / 'fixtures' / (fixture + '.json'))
        log.info("Dumping fixture: %s" % fixture)
        cmd = "python manage.py loaddata " + fixture
        logging.debug(cmd)
        ctx.run(cmd)


@task
def reset_db(ctx):
    """Remove and reinitialize database"""
    data = ROOT_DIR / 'data'
    for p in data.glob("db.*"):
        os.remove(str(p))
    if not data.exists():
        os.makedirs(str(data))
    ctx.run("python manage.py migrate")


@task(pre=[reset_db, load_fixtures])
def db(ctx):
    """
    Full database re-initialization
    """
    cmd = "python manage.py fill_test_data --on-empty"
    ctx.run(cmd)
