import os
import re
import yaml

import src.mockGithub as mockGithub

def get_test_data(settings, move_data, owner, i):
    labels = []
    comments = []

    if 'Start new game' in move_data['move']:
        if move_data['author'] == owner:
            comments += [settings['comments']['successful_new_game'].format(author='@.+')]
        else:
            comments += [settings['comments']['invalid_new_game'].format(author='@.+')]
    elif ('is_consecutive' not in move_data or move_data['is_consecutive'] == False) and ('is_invalid' not in move_data or move_data['is_invalid'] == False):
        labels += ['White' if i % 2 == 1 else 'Black']
        comments += [settings['comments']['successful_move'].format(author='@.+', move='.....?')]

    if 'is_winner' in move_data and move_data['is_winner'] == True:
        labels += ['👑 Winner!']
        comments += [settings['comments']['game_over'].format(outcome='.+', num_moves='\\d+', num_players='\\d+', players='(@.+,)* @.+')]

    if 'is_draw' in move_data and move_data['is_draw'] == True:
        labels += ['👑 Draw!']
        comments += [settings['comments']['game_over'].format(outcome='.+', num_moves='\\d+', num_players='\\d+', players='(@.+,)* @.+')]

    if 'is_capture' in move_data and move_data['is_capture'] == True:
        labels += ['⚔️ Capture!']

    if 'is_consecutive' in move_data and move_data['is_consecutive'] == True:
        labels += ['Invalid']
        comments += [settings['comments']['consecutive_moves'].format(author='@.+')]

    if 'is_invalid' in move_data and move_data['is_invalid'] == True:
        labels += ['Invalid']
        comment = re.escape(settings['comments']['invalid_move']).replace("\\{", "{").replace("\\}", "}")
        comments += [comment.format(author='@.+', move='.+')]

    return labels, comments


def run_test_case(filename, main_fn):
    passed = 0
    failed = 0

    with open(filename, 'r') as test_file:
        test_data = yaml.load(test_file, Loader=yaml.FullLoader)

    with open('data/settings.yaml', 'r') as settings_file:
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)

    print('\u001b[0m\u001b[1m\u001b[37m  ' + test_data['name'])

    for i in range(len(test_data['moves'])):
        move_data = test_data['moves'][i]
        labels, comments = get_test_data(settings, move_data, test_data['owner'], i)

        issue = mockGithub.Issue(move_data['move'])
        issue.expect_labels(labels)
        issue.expect_comments(comments)

        issue_author = move_data['author']
        repo_owner = test_data['owner']
        os.environ['GITHUB_REPOSITORY'] = repo_owner[1:] + '/' + repo_owner[1:]

        main_fn(issue, issue_author, repo_owner)

        result, reason = issue.expectations_fulfilled()
        if result == True:
            print('\u001b[0m    \u001b[1m\u001b[32m✓\u001b[0m\u001b[37m {} by {}\u001b[0m'.format(move_data['move'], move_data['author']))
            passed += 1
        else:
            print('\u001b[0m    \u001b[1m\u001b[32m✓\u001b[0m\u001b[37m {} by {}\u001b[1m →\u001b[31m {}\u001b[0m'.format(move_data['move'], move_data['author'], reason))
            failed += 1

    return passed, failed


def run(main_fn):
    passed = 0
    failed = 0

    for f in [f for f in os.listdir('tests/') if re.match('.+\\.yml', f)]:
        passed_tmp, failed_tmp = run_test_case('tests/' + f, main_fn)
        passed += passed_tmp
        failed += failed_tmp

    total = passed + failed

    print()
    print(f'\u001b[1m\u001b[33m    {total} total', end='');
    print(f'\u001b[1m\u001b[32m   {passed} passed', end='');
    print(f'\u001b[1m\u001b[31m   {failed} failed');
