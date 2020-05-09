import asyncio
from urllib.parse import urlparse, parse_qs

import aiohttp
import requests
from flask import Flask, render_template, redirect, request

app = Flask(__name__)


# Asynchronous fetch, receives a session ClientSession object, and a URL to
# request, returns json. Although it is the third function inline it is the
# first to communicate with the API, can be ideal to deal with HTTP errors
# before they go deeper into the routine.
async def fetch(session, url):
    async with session.get(url) as response:
        # if response.status != 200:
        #     print('Not successful')
        return await response.json()


# Second asynchronous function, for task fetching. Makes a queue of tasks
# and call the fetch function for each task, passing along the ClientSession
# object and the URL from the first function.
async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        tasks.append(asyncio.create_task(fetch(session, url)))
    return await asyncio.gather(*tasks)


# First asynchronous function, receives the URL to fetch, creates a
# ClientSession object and passes it to the further fetch functions.
async def async_fetch(url):
    async with aiohttp.ClientSession() as session:
        return await fetch_all(session, url)


# Gets pokemon list from current URL and runs it through the async
# fetch functions. Those functions will return all pokemon information
# available at the time of the request, no filtering has been done.
def poke_filter(url):
    get_poke_url = url['results']
    pokemon_list = []
    for uri in get_poke_url:
        pokemon_list.append(uri['url'])
    return asyncio.run(async_fetch(pokemon_list))


# Returns the offset, which is a query, of the passed URL, useful to get
# the current position of the URL.
def update_offset_limit(url, where, offset):
    url_parsed = urlparse(url[where])
    url_queries = parse_qs(url_parsed.query)
    return url_queries[offset]


def updated_offset(the_list, where, offset):
    [url] = update_offset_limit(the_list, where, offset)
    return url


# Returns the specified value from a POST submitted form.
def query_html_form(name):
    return request.form.get(name)


# Returns how many pages can be listed, for pagination.
def get_page_list(size, limit):
    page_list = {
        'offset': 0,
        'counter': [],
        'page_list': []
    }

    try:
        for page in range(0, int((size - limit) / limit)):
            if page_list['offset'] == 0:
                page_list['page_list'].append(f'{0}&{limit}')
                page_list['counter'].append(0)
            page_list['page_list'].append(f'{page_list["offset"] + limit}&{limit}')
            page_list['counter'].append(page_list['counter'][-1] + 1)
            page_list['offset'] += limit
    except ZeroDivisionError:
        return get_page_list(size, 10)

    return page_list


# The main renderer, it will query the API and check if the specified
# response is valid. If the offset is bellow zero, it will cause problems
# with the update_offset_limit function. Because at zero the previous and
# next values on the start/end of the list are None and the parser can't
# work on it. If the range is higher than the API response count, it will
# simply redirect to the main page. It also queries the URL to get the
# current offset and limit numbers to keep track of the user's position
# within the pages.
def render_pokedex(page_name, offset, limit):
    if limit < 10:
        limit = 10

    poke_list = requests.get(
        f'https://pokeapi.co/api/v2/pokemon?offset={offset}&limit={limit}').json()

    if offset <= 0:
        return render_template(page_name,
                               page_list=get_page_list(poke_list['count'], limit),
                               pokemon_list=poke_filter(poke_list),
                               next_offset=updated_offset(poke_list, 'next', 'offset'),
                               next_limit=updated_offset(poke_list, 'next', 'limit'),
                               previous_offset=offset,
                               previous_limit=limit,
                               current_offset=offset,
                               current_limit=limit)

    elif offset >= poke_list['count'] - limit:
        return redirect('/')

    else:
        return render_template(page_name,
                               page_list=get_page_list(poke_list['count'], limit),
                               pokemon_list=poke_filter(poke_list),
                               next_offset=updated_offset(poke_list, 'next', 'offset'),
                               next_limit=updated_offset(poke_list, 'next', 'limit'),
                               previous_offset=updated_offset(poke_list, 'previous', 'offset'),
                               previous_limit=updated_offset(poke_list, 'previous', 'limit'),
                               current_offset=offset,
                               current_limit=limit)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_pokedex('pokedex.html', 0, 10)
    elif request.method == 'POST':
        return redirect(f'/pokedex/f/{0}&{query_html_form("user_limit")}/')


@app.route('/pokedex/f/<int:offset>&<int:limit>/', methods=['GET', 'POST'])
def pokedex_filter(offset, limit):
    if request.method == 'GET':
        return render_pokedex('pokedex.html', offset, limit)
    elif request.method == 'POST':
        return redirect(f'/pokedex/f/{offset}&{query_html_form("user_limit")}/')


@app.route('/pokedex/n/<int:offset>&<int:limit>/', methods=['GET', 'POST'])
def next_page(offset, limit):
    if request.method == 'GET':
        return render_pokedex('pokedex.html', offset, limit)
    elif request.method == 'POST':
        return redirect(f'/pokedex/f/{offset}&{query_html_form("user_limit")}/')


@app.route('/pokedex/p/<int:offset>&<int:limit>/', methods=['GET', 'POST'])
def previous_page(offset, limit):
    if request.method == 'GET':
        return render_pokedex('pokedex.html', offset, limit)
    elif request.method == 'POST':
        return redirect(f'/pokedex/f/{offset}&{query_html_form("user_limit")}/')


@app.route('/pokemon/i/<string:pokemon>/')
def pokemon_info(pokemon):
    try:
        poke_list = requests.get(f'https://pokeapi.co/api/v2/pokemon?offset={0}&limit={-1}').json()

        poke = {}
        for i in poke_list['results']:
            poke.update({i['name']: i['url']})

        poke_info = requests.get(poke[pokemon]).json()
        species_info = requests.get(poke_info['species']['url']).json()
        habitat_info = requests.get(species_info['habitat']['url']).json()
        return render_template('pokemon.html',
                               poke_info=poke_info,
                               species_info=species_info,
                               habitat_info=habitat_info)

    except KeyError:
        return redirect('/404/')

    except TypeError:
        return redirect('/404/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
