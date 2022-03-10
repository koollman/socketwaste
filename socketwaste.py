#!/usr/bin/env python3
import asyncio
import random
from datetime import datetime, timezone
from decorator import decorator

@decorator
async def log4handler(handler, *args, **kw):
    addr = args[1].get_extra_info('peername')
    start=datetime.now(tz=timezone.utc)
    print(f'{start} start peer {addr}')
    await handler(*args, *kw)
    end=datetime.now(tz=timezone.utc)
    duration=end-start
    print(f'{end} end peer {addr}. duration:{duration}')

@log4handler
async def http_handler(_reader, writer):
    writer.write(b'HTTP/1.1 200 OK\r\n')
    try:
        while True:
            await asyncio.sleep(5)
            header = random.randint(0, 2**32)
            value = random.randint(0, 2**32)
            writer.write(b'X-%x: %x\r\n' % (header, value))
            await writer.drain()
    except ConnectionResetError:
        pass

@log4handler
async def basic_handler(_reader, writer):
    try:
        while True:
            await asyncio.sleep(10)
            writer.write(b'%x\r\n' % random.randint(0, 2**32))
            await writer.drain()
    except ConnectionResetError:
        pass


handlers={}
handlers['basic']=basic_handler
handlers['http']=http_handler
# TODO: smtp_handler
#handlers['smtp']=smtp_handler

async def main(handler, port):
    server = await asyncio.start_server(handler, '0.0.0.0', port)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("-t", "--type", default="basic",
            choices=sorted(handlers.keys()))
    args = parser.parse_args()
    print(args)
    asyncio.run(main(handlers[args.type], args.port))

