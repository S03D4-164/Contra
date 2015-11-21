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
    #api="http://localhost:8000/api/docker/thug/"
    #api="http://localhost:8000/api/local/thug/"

    c = Content.objects.get(pk=cid)
    payload = {
        'content': c.content.encode('utf-8'),
        'resource': c.id,
    }
    raw = {}
    result = {}
    yara = None
    try:
        api = ContraAPI()
        res = requests.post(api.local_thug, data=payload)
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
        try:
            desc = ast.literal_eval(y["description"])
        except Exception as e:
            logger.debug(str(e))
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
            """
            if "stings" in desc:
                for s in desc["strings"]:
                    if not s["data"] in matched:
                        matched.append(s["data"])
            """
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
