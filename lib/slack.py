import requests

'''
simple slack bot posting class. relies on an establshed web hook.
this is just a wrapper for the POST command. This url defaults to channel #code
'''
class SlackPoster:
    def __init__(self,user,
                 url = 'https://hooks.slack.com/services/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',
                 channel=None):
        self.url = url
        self.user = user
        self.channel = channel

    def send(self,message):
        payload = {'text': message, 'username': self.user}
        if self.channel:
            payload['channel'] = self.channel
        r = requests.post(self.url, json=payload)
        return r.text

    
if __name__ == '__main__':

    sp = SlackPoster('Your Mom', channel='@barry')
    print(sp.send('you suck'))
