from ..celery import app
from ..forms import *
from ..models import *

from ..api import ContraAPI

import requests, json, ast

import logging
from ..logger import getlogger
logger = getlogger(logging.DEBUG)

@app.task(soft_time_limit=30)
def content_analysis(cid):

    c = Content.objects.get(pk=cid)
    payload = {
        'content': c.content.encode('utf-8'),
        'id': c.id,
    }
    raw = {}
    result = {}
    yara = None
    try:
        api = ContraAPI()
        #res = requests.post(api.local_thug, data=payload)
        res = requests.post(api.docker_thug, data=payload)
        raw = res.content
        result = res.json()
        if result:
            if "yara_matched" in result:
                yara = result["yara_matched"]
    except Exception as e:
        #result["error"] = str(e)
        logger.error(str(e))

    rules = []
    for y in yara:
        desc = None
        if "description" in y:
            desc = ast.literal_eval(y["description"])
        if desc:
            rule = None
            if "rule" in desc:
                try:
                    rule = YaraRule.objects.get(
                        name = desc["rule"]
                    )
                except:
                    rule = YaraRule.objects.create(
                        name = desc["rule"]
                    )
                if rule:
                    rules.append(rule)
            if "tags" in desc:
                for t in desc["tags"]:
                    tag = None
                    try:
                        tag = YaraTag.objects.get(
                            name = t
                        )
                    except:
                        tag = YaraTag.objects.create(
                            name = t
                        )
                    if rule:
                        rule.tag.add(tag)
                        rule.save()
    analysis = None
    try:
        analysis = Analysis.objects.get(
            content = c,
        )
    except:
        analysis = Analysis.objects.create(
            content = c,
        )
    if analysis:
        analysis.result = raw
        for r in rules:
            analysis.rule.add(r)
        analysis.save()
        return analysis.id
    else:
        return None
