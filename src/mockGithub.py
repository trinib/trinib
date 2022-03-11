import re

class Issue:
    def __init__(self, title=''):
        self.__title = title
        self.__closed = False
        self.__expected_labels = []
        self.__expected_comments = []
        self.__unexpected_labels = []
        self.__unexpected_comments = []

    @property
    def title(self):
        return self.__title

    def create_comment(self, text):
        if len(self.__expected_comments) == 0:
            self.__unexpected_comments += [text]
        elif re.match(self.__expected_comments[0], text) == None:
            self.__unexpected_comments += [text]
        else:
            self.__expected_comments.pop(0)

    def edit(self, state='opened', labels=[]):
        if state == 'closed':
            self.__closed = True

        for label in labels:
            try:
                self.__expected_labels.remove(label)
            except ValueError:
                self.__unexpected_labels += [label]

    def add_to_labels(self, label):
        try:
            self.__expected_labels.remove(label)
        except ValueError:
            self.__unexpected_labels += [label]

    ####################### Testing functions #######################

    def expect_labels(self, labels):
        self.__expected_labels = labels

    def expect_comments(self, regex_list):
        self.__expected_comments = regex_list

    def expectations_fulfilled(self, ):
        if len(self.__expected_labels) != 0:
            return False, f'Missing expected labels: {self.__expected_labels}'
        if len(self.__expected_comments) != 0:
            return False, f'Missing expected comments: {self.__expected_comments}'
        if len(self.__unexpected_labels) != 0:
            return False, f'Unexpected labels: {self.__unexpected_labels}'
        if len(self.__unexpected_comments) != 0:
            return False, f'Unexpected comments: {self.__unexpected_comments}'
        if self.__closed == False:
            return False, 'Issue not closed'

        return True, None
