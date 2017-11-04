from django import template
from home.models import Probe
import importlib
import logging


logger = logging.getLogger(__name__)
register = template.Library()


@register.filter
def status(probe_id):
    probe = Probe.get_by_id(probe_id)
    if probe is None:  # pragma: no cover
        return {"message": "Error - probe is None - param id not set : " + str(probe_id)}
    my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(probe_id)
    response = probe.status()
    if 'message' in response:
        if 'active (running)' in response['message']:
            return 'success'
        else:
            return 'danger'
    else:
        return 'danger'
