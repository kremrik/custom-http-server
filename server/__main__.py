from server import server

import asyncio
import logging


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    
    host = "localhost"
    port = 50007
    client_handler = server.http_client_handler
    logging.info(f"Starting server on http://{host}:{port} with client handler {client_handler}")

    asyncio.run(
        server.serve(
            host=host,
            port=port,
            client_handler=client_handler
        )
    )
