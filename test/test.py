from dns_watcher import handler
import sys
sys.path.append('../')


def test(domain, state, event, context):
    handler.domain_list_path = domain
    handler.state_file = state
    handler.handler(event, context)


test("./domainlist.json", "./state.json", None, None)
