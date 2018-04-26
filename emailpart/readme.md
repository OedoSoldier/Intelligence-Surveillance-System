# Pre-requisite

Python2.7

A Google account with Gmail enabled

# Installing

Google API

```
$ pip install --upgrade google-api-python-client
```

* [Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)

# Introduction

### SendEmail

It will send an email with the sending time and an image attachment.

Also, it will record the time on the sheet on Google drive.

### GetEmail

It will get threads, which is in time order.

It can pick the latest one with the subject you input as 'target'.

### Alert

It contains SendEmail and GetEmail.

It will be triggered if the camera detect a stranger. The picture of the stranger and a code will be sented to the user by gmail. And then, in the next hour, it will keep checking if the user reply the code every minutes. If it did received the code, it will give a signal to set off the alarm.

### Reference

* [Sending Email](https://developers.google.com/gmail/api/guides/sending)

* [Managing Threads](https://developers.google.com/gmail/api/guides/threads)
