import logging
import subprocess

from django.conf import settings

logger = logging.getLogger(__name__)


def git_tag(git_root):
    command = [settings.GIT_BINARY, 'describe', '--tags', '--always']
    command_date = [settings.GIT_BINARY, 'log', '-n 1', '--date=short', '--pretty=%ad']
    p = subprocess.Popen(command, cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)
    out, err = p.communicate()
    if err:  # pragma: no cover
        logger.exception(str(err))
    p_date = subprocess.Popen(command_date, cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True)
    out_date, err_date = p_date.communicate()
    out_date.replace('-', '.')
    if err_date:  # pragma: no cover
        logger.exception(str(err_date))
    return out.strip() + "-" + out_date.strip()
