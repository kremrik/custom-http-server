from server import server

import asyncio
import logging
from functools import partial


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    host = "0.0.0.0"
    port = 8080
    client_handler = server.http_client_handler
    logging.info(
        f"Starting server on http://{host}:{port} with client handler {client_handler}"
    )

    asyncio.run(
        server.serve(
            host=host,
            port=port,
            client_handler=client_handler,
        )
    )
