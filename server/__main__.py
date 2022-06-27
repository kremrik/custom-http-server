from server import server

import asyncio
import logging
from functools import partial


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    
    host = "localhost"
    port = 50007
    client_handler = partial(server.http_client_handler, buff_size=8)
    logging.info(f"Starting server on http://{host}:{port} with client handler {client_handler}")

    asyncio.run(
        server.serve(
            host=host,
            port=port,
            client_handler=client_handler,
        )
    )
