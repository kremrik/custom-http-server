# Useless HTTP Server

Wrote this to get more comfortable with TCP/IP and async Python.
Uses only Python standard library.


## Most simple test imaginable

### Start server
```python
python -m server
```

### Hit with sleepy client
This client will sleep for `N` seconds between sending and receiving data - an action that would typically block a similar `socket` process in Python.
So we can launch one long-lived connection and some shorter ones and watch the latter return without being blocked:

```python
python client.py 20  # 20sec block
...
...
...
```

And in a separate process:
```python
python client.py 0  # no waiting at all
HTTP/1.1 200 OK

THIS IS SOME BODY TEXT
```

If that's not convicing, try running the same clients with the `sync_server.py`:
```python
python sync_server.py
```
