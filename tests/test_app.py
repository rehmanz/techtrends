import http.client

def test_get_health_endpoint():
    conn = http.client.HTTPConnection("localhost", 3111)
    conn.request("GET", "/healthz")
    res = conn.getresponse()
    assert "healthy" in res.read().decode("utf-8")

def test_get_root_endpoint():
    conn = http.client.HTTPConnection("localhost", 3111)
    conn.request("GET", "/metrics")
    res = conn.getresponse()
    assert "success" in res.read().decode("utf-8")
