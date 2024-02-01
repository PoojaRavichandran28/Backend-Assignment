import json
from datetime import datetime

json_file_path = "config/rules.json"
with open(json_file_path, "r") as json_file:
    rules = json.load(json_file)


def contains(field_value, rule_value):
    return True if rule_value in field_value else False


def not_contains(field_value, rule_value):
    return True if rule_value not in field_value else False


def equals(field_value, rule_value):
    return True if field_value == rule_value else False


def not_equals(field_value, rule_value):
    return True if field_value != rule_value  else False


def less_than(field_value, rule_value):
    days = (datetime.now() - datetime.strptime(field_value, '%Y-%m-%d %H:%M:%S')).days
    return True if days < rule_value else False


def greater_than(field_value, rule_value):
    days = (datetime.now() - datetime.strptime(field_value, '%Y-%m-%d %H:%M:%S')).days
    return True if days > rule_value else False


predicate_map = {
    'contains': contains,
    'not contains': not_contains,
    'equals': equals,
    'not equals': not_equals,
    'less than': less_than,
    'greater than': greater_than
}


def mark_and_move_mails(data, actions, service):
    try:
        add_labels = [actions['mark_as'], actions['move_to']]
        remove_labels = []
        if 'READ' in add_labels:
            remove_labels.append('UNREAD')
            add_labels.remove('READ')
        service.users().messages().modify(userId='me', id=data['message_id'],
                                          body={'addLabelIds': add_labels,
                                                'removeLabelIds': remove_labels}).execute()
        print(f'Email from {data["From"]} and subject {data["Subject"]} marked as {actions["mark_as"]} and moved to {actions["move_to"]}')

    except Exception as e:
        print(f'Error happened while taking actions:{e}')


def execute_rules(formatted_data, service):
    try:
        for data in formatted_data:
            for rule in rules['rules']:
                result = []
                for condition in rule['conditions']:
                    result.append(predicate_map[condition['predicate']](data[condition['field']], condition['value']))
                if rule['overall_predicate'] == 'All':
                    take_action = all(result)
                elif rule['overall_predicate'] == 'Any':
                    take_action = any(result)
                if take_action:
                    mark_and_move_mails(data, rule['actions'], service)
        print(f'Rules executed successfully')
    except Exception as e:
        print(f'Error while executing rules{e}')




