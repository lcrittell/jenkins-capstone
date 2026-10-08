import threading
import time
from urllib.request import urlopen

from app import create_server


def test_application_health():
    server = create_server()

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    time.sleep(0.5)

    response = urlopen("http://127.0.0.1:8000/")

    assert response.status == 200

    server.shutdown()
    server.server_close()