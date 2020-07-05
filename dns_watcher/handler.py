import json
import requests
import logging
from logging import StreamHandler, Formatter

domain_list_path = None
state_file = None

gdns = "https://dns.google.com/resolve?"
cflare = "https://cloudflare-dns.com/dns-query?ct=application/dns-json&"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = StreamHandler()
stream_handler.setLevel(logging.DEBUG)
handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)


def handler(event, context):
    with open(domain_list_path, 'r') as file:
        domain_list = json.load(file)
    all_state = {}

    for domain in domain_list:
        domain_state = {}
        for record_type in domain["record"].keys():
            if domain['record'].get(record_type):
                domain_state[record_type] = check_records(cflare, domain.get("domain"), record_type)
                print(check_diff(domain.get('domain'), record_type, domain_state[record_type]))
        all_state[domain.get('domain')] = domain_state

    save_state(all_state)


def check_records(dns, domain, record_type):
    res = requests.get('%sname=%s&type=%s' % (dns, domain, record_type))
    records = []
    if res.status_code != 200:
        return "http error"

    record_json = json.loads(res.text)

    try:
        for key in record_json['Answer']:
            records.append(key['data'])
    except KeyError:
        return None

    records.sort()
    return records


def save_state(state):
    with open(state_file, 'w') as file:
        file.write(json.dumps(state))


def check_diff(domain, record_type, rec):
    with open(state_file, 'r') as file:
        state = json.load(file)
    try:
        last_state = state.get(domain).get(record_type)
    except AttributeError:
        logger.info("domain or record attribute not fount on the last state. might be a new domain or record")
        return "aaa"
    logger.info(domain + " " + record_type + ": " + json.dumps(last_state) + "<-------->" + json.dumps(rec))
    if rec == last_state:
        return None
    else:
        return last_state

