from server import error

import asyncio
import logging

from server.http import request, response


LOGGER = logging.getLogger("server")
LOGGER.setLevel(logging.DEBUG)


async def serve(host, port, client_handler=None):
    if not client_handler:
        client_handler = default_client_handler

    server = await asyncio.start_server(client_handler, host, port)

    async with server:
        await server.serve_forever()


async def default_client_handler(reader, writer, buff_size=1024):
    addr = writer.get_extra_info("peername")
    LOGGER.info(f"Client connected: [{addr}]")

    data = await reader.read(buff_size)
    writer.write(data)
    await writer.drain()
    writer.close()


async def http_client_handler(reader, writer, buff_size=1024):
    addr = writer.get_extra_info("peername")
    LOGGER.info(f"Client connected: [{addr}]")

    try:
        req = request.LazyRequest(reader)
        path = await req.path
        body = path + b"  good to go!"
        resp = response.Response(
            protocol=response.Protocol.HTTP1_1,
            status=response.Status.OK,
            body=body,
        )
        resp_msg = response.to_bytes(resp)
        writer.write(resp_msg)
        await writer.drain()
        writer.close()

    except Exception as e:
        body = e.args[0].encode()
        resp = response.Response(
            protocol=response.Protocol.HTTP1_1,
            status=response.Status.NotFound,
            body=body,
        )
        resp_msg = response.to_bytes(resp)
        writer.write(resp_msg)
        await writer.drain()
        writer.close()
