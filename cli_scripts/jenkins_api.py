#!/usr/bin/env python3
"""Use Jenkins' in-cluster REST API with the trusted service identity."""

import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = os.environ.get(
    "NITA_JENKINS_API_URL", "http://localhost:8080/jenkins"
).rstrip("/")
IDENTITY = os.environ.get("JENKINS_USER") or "admin"


def _open(path, method="GET", data=None, headers=None, opener=None):
    request_headers = {"X-Forwarded-User": IDENTITY}
    request_headers.update(headers or {})
    request = urllib.request.Request(
        BASE_URL + path, data=data, headers=request_headers, method=method
    )
    if opener is not None:
        return opener.open(request, timeout=30)
    return urllib.request.urlopen(request, timeout=30)


def _job_path(name):
    if not name or any(not part for part in name.split("/")):
        raise ValueError("job name must not be empty or contain empty path segments")
    return "".join("/job/" + urllib.parse.quote(part, safe="") for part in name.split("/"))


def _post(path, data=None, content_type=None):
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    with _open("/crumbIssuer/api/json", opener=opener) as response:
        crumb = json.load(response)
    headers = {crumb["crumbRequestField"]: crumb["crumb"]}
    if content_type:
        headers["Content-Type"] = content_type
    with _open(
        path, method="POST", data=data or b"", headers=headers, opener=opener
    ) as response:
        return response.read()


def _json(path):
    with _open(path) as response:
        return json.load(response)


def _plugin_list():
    data = _json("/pluginManager/api/json?tree=plugins[shortName,version,active,enabled,url]")
    return sorted(data.get("plugins", []), key=lambda plugin: plugin.get("shortName", ""))


def _run(args):
    if args[:2] == ["jobs", "ls"] and len(args) == 2:
        jobs = _json("/api/json?tree=jobs[name]").get("jobs", [])
        print("\n".join(sorted(job["name"] for job in jobs)))
        return

    if args[:2] == ["jobs", "get"] and len(args) == 3:
        with _open(_job_path(args[2]) + "/config.xml") as response:
            sys.stdout.buffer.write(response.read())
        return

    if args[:2] == ["jobs", "create"] and len(args) == 3:
        xml = sys.stdin.buffer.read()
        if not xml:
            raise ValueError("job XML must not be empty")
        query = urllib.parse.urlencode({"name": args[2]})
        _post("/createItem?" + query, xml, "application/xml")
        return

    if args[:2] == ["jobs", "delete"] and len(args) == 3:
        _post(_job_path(args[2]) + "/doDelete")
        return

    if args[:2] in (["jobs", "disable"], ["jobs", "enable"]) and len(args) == 3:
        operation = "disable" if args[1] == "disable" else "enable"
        _post(_job_path(args[2]) + "/" + operation)
        return

    if args == ["version"]:
        with _open("/api/", method="HEAD") as response:
            version = response.headers.get("X-Jenkins")
        if not version:
            raise RuntimeError("Jenkins response did not include the X-Jenkins version header")
        print(version)
        return

    if args == ["whoami"]:
        print(json.dumps(_json("/whoAmI/api/json"), indent=2, sort_keys=True))
        return

    if args == ["plugins", "ls"]:
        for plugin in _plugin_list():
            print(f"{plugin['shortName']}:{plugin['version']}")
        return

    if args == ["plugins", "details"]:
        for plugin in _plugin_list():
            print(
                f"{plugin['shortName']}\t{plugin['version']}\t"
                f"active={plugin.get('active', False)}\t"
                f"enabled={plugin.get('enabled', False)}\t"
                f"{plugin.get('url', '')}"
            )
        return

    if args == ["plugins", "backup-list"]:
        for plugin in _plugin_list():
            print(f"{plugin['shortName']}:{plugin['version']}")
        return

    if len(args) == 4 and args[:2] == ["views", "add-job"]:
        view, job = args[2:]
        path = "/view/" + urllib.parse.quote(view, safe="") + "/addJobToView?"
        _post(path + urllib.parse.urlencode({"name": job}))
        return

    raise ValueError("unsupported Jenkins API command: " + " ".join(args))


def main(args=None):
    try:
        _run(sys.argv[1:] if args is None else args)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        print(
            f"Jenkins API request failed: HTTP {exc.code} {exc.reason}"
            + (f": {detail}" if detail else ""),
            file=sys.stderr,
        )
        return 1
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"Jenkins API request failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
