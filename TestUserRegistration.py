#!/usr/bin/python3.7

import argparse
import asyncio

from aiohttp import ClientSession, MultipartWriter, ClientConnectionError, ClientPayloadError, ClientResponseError, \
    FormData


async def upload_file(url, username, password, responses):

    mpw = MultipartWriter()

    fd = FormData()
    fd.add_field('username', username)
    fd.add_field('password', password)

    async with ClientSession() as session:
        try:
            async with session.post(url, data=fd) as response:
                response = await response.read()
                response_str = response.decode('utf-8')
                responses[response_str] = responses.get(response_str, 0) + 1
        except ClientConnectionError:
            responses['CONNECTION_ERR'] = responses.get('CONNECTION_ERR', 0) + 1
        except ClientPayloadError:
            responses['PAYLOAD_ERR'] = responses.get('PAYLOAD_ERR', 0) + 1
        except ClientResponseError:
            responses['RESPONSE_ERR'] = responses.get('RESPONSE_ERR', 0) + 1


async def status_printer(requests, responses):
    while True:
        print("Uploaded: %d files, responses: %s" % (requests['i'], responses))
        await asyncio.sleep(1.0)


async def load_gen(url, username, password, rate,  n_uploads):
    responses = {}
    requests = {'i': 0}
    asyncio.create_task(status_printer(requests, responses))
    while n_uploads == 0 or requests['i'] < n_uploads:
        upload_task = upload_file(url, username, password, responses)
        asyncio.create_task(upload_task)
        requests['i'] += 1
        await asyncio.sleep(1.0 / rate)

async def load_gen():
    responses = {}
    requests = {'i': 0}
    asyncio.create_task(status_printer(requests, responses))

    upload_task = upload_file("http://pipixia.ca/api/register", "admin", "admin", responses)
    asyncio.create_task(upload_task)
    requests['i'] += 1
    await asyncio.sleep(1.0 / 20)

    upload_task = upload_file("http://pipixia.ca/api/register", "test1", "", responses)
    asyncio.create_task(upload_task)
    requests['i'] += 1
    await asyncio.sleep(1.0 / 20)

    upload_task = upload_file("http://pipixia.ca/api/register", "", "123", responses)
    asyncio.create_task(upload_task)
    requests['i'] += 1
    await asyncio.sleep(1.0 / 20)

    upload_task = upload_file("http://pipixia.ca/api/register", "test3   ", "123", responses)
    asyncio.create_task(upload_task)
    requests['i'] += 1
    await asyncio.sleep(1.0 / 20)

    upload_task = upload_file("http://pipixia.ca/api/register", "    ", "123", responses)
    asyncio.create_task(upload_task)
    requests['i'] += 1
    await asyncio.sleep(1.0 / 20)


    for var in range(10):
        upload_task = upload_file("http://pipixia.ca/api/register", "handsomeFredkk" + str(var), "fakedPWD", responses)
        asyncio.create_task(upload_task)
        requests['i'] += 1
        await asyncio.sleep(1.0/20)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate file uploading load',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load_gen())
